#!/usr/bin/env python3
"""AI 小说挂机创作与发布脚本。

能力：
- 兼容远端 OpenAI 风格 API 与本地 Ollama 接口
- 状态机：大纲 -> 章节任务 -> 章节正文 -> 发布 -> 休眠循环
- 上下文截断策略，避免上下文无限膨胀
- 网络重试与指数退避
- 本地状态持久化，支持异常重启续跑
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


STATE_FILE = Path(os.getenv("AI_BOT_STATE_FILE", "./ai_bot_state.json"))


@dataclass
class BotConfig:
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com")

    # Ollama 风格接口
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
    backend_publish_token: str = os.getenv("BACKEND_PUBLISH_TOKEN", "demo-writer-token")
    backend_creator_id: int = int(os.getenv("BACKEND_CREATOR_ID", "1"))

    genre: str = os.getenv("NOVEL_GENRE", "都市异能")
    style: str = os.getenv("NOVEL_STYLE", "爽文快节奏")
    chapter_target_words: int = int(os.getenv("CHAPTER_TARGET_WORDS", "1800"))
    chapters_per_cycle: int = int(os.getenv("CHAPTERS_PER_CYCLE", "3"))

    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "8000"))
    max_retry: int = int(os.getenv("MAX_RETRY", "5"))
    cycle_sleep_seconds: int = int(os.getenv("CYCLE_SLEEP_SECONDS", "120"))


@dataclass
class ChapterTask:
    number: int
    title: str
    brief: str
    done: bool = False


@dataclass
class BotState:
    phase: str = "INIT"
    novel_id: int | None = None
    novel_title: str = ""
    novel_summary: str = ""
    outline: str = ""
    chapter_tasks: list[ChapterTask] = field(default_factory=list)
    published_chapters: int = 0
    context_memory: list[str] = field(default_factory=list)
    updated_at: int = field(default_factory=lambda: int(time.time()))

    def to_json(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "novel_id": self.novel_id,
            "novel_title": self.novel_title,
            "novel_summary": self.novel_summary,
            "outline": self.outline,
            "chapter_tasks": [task.__dict__ for task in self.chapter_tasks],
            "published_chapters": self.published_chapters,
            "context_memory": self.context_memory,
            "updated_at": int(time.time()),
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "BotState":
        tasks = [ChapterTask(**item) for item in raw.get("chapter_tasks", [])]
        return cls(
            phase=raw.get("phase", "INIT"),
            novel_id=raw.get("novel_id"),
            novel_title=raw.get("novel_title", ""),
            novel_summary=raw.get("novel_summary", ""),
            outline=raw.get("outline", ""),
            chapter_tasks=tasks,
            published_chapters=raw.get("published_chapters", 0),
            context_memory=raw.get("context_memory", []),
            updated_at=raw.get("updated_at", int(time.time())),
        )


def save_state(state: BotState) -> None:
    STATE_FILE.write_text(json.dumps(state.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_state() -> BotState:
    if not STATE_FILE.exists():
        return BotState()
    raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return BotState.from_json(raw)


def truncate_context(lines: list[str], max_chars: int) -> list[str]:
    """保留最新上下文，防止长篇后提示词失控。"""
    result: list[str] = []
    total = 0
    for item in reversed(lines):
        size = len(item)
        if total + size > max_chars:
            break
        total += size
        result.append(item)
    result.reverse()
    return result


def call_with_retry(action: str, fn, max_retry: int):
    error: Exception | None = None
    for i in range(max_retry):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            error = exc
            backoff = (2**i) + random.random()
            print(f"[{action}] 第 {i + 1} 次失败: {exc}; {backoff:.1f}s 后重试")
            time.sleep(backoff)
    raise RuntimeError(f"[{action}] 超过最大重试次数") from error


def parse_json_block(text: str) -> dict[str, Any]:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:  # noqa: BLE001
        return {}


class LLMClient:
    def __init__(self, cfg: BotConfig):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.8) -> str:
        if self.cfg.llm_provider == "ollama":
            return self._chat_ollama(messages, temperature)
        return self._chat_openai(messages, temperature)

    def _chat_openai(self, messages: list[dict[str, str]], temperature: float) -> str:
        endpoint = f"{self.cfg.llm_base_url.rstrip('/')}/v1/chat/completions"
        headers = {}
        if self.cfg.llm_api_key:
            headers["Authorization"] = f"Bearer {self.cfg.llm_api_key}"
        payload = {
            "model": self.cfg.llm_model,
            "messages": messages,
            "temperature": temperature,
        }
        response = self.session.post(endpoint, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _chat_ollama(self, messages: list[dict[str, str]], temperature: float) -> str:
        endpoint = f"{self.cfg.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.cfg.llm_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        response = self.session.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        message = data.get("message") or {}
        return message.get("content", "")


class BackendPublisher:
    def __init__(self, cfg: BotConfig):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cfg.backend_publish_token}",
            }
        )

    def publish_create_novel(self, title: str, summary: str, category: str) -> int:
        endpoint = f"{self.cfg.backend_base_url.rstrip('/')}/api/v1/completions"
        payload = {
            "model": "xiaoshuo-bot",
            "creator_id": self.cfg.backend_creator_id,
            "messages": [
                {"role": "system", "content": "ACTION: CREATE_NOVEL"},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "title": title,
                            "summary": summary,
                            "category": category,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        response = self.session.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()
        text = response.json()["choices"][0]["text"]
        match = re.search(r"id=(\d+)", text)
        if not match:
            raise RuntimeError(f"无法从响应解析 novel_id: {text}")
        return int(match.group(1))

    def publish_add_chapter(self, novel_id: int, number: int, title: str, content: str) -> None:
        endpoint = f"{self.cfg.backend_base_url.rstrip('/')}/api/v1/completions"
        payload = {
            "model": "xiaoshuo-bot",
            "creator_id": self.cfg.backend_creator_id,
            "messages": [
                {"role": "system", "content": "ACTION: ADD_CHAPTER"},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "novel_id": novel_id,
                            "chapter_number": number,
                            "title": title,
                            "content": content,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        response = self.session.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()


def build_outline_prompt(cfg: BotConfig) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是商业网文总编。输出严格 JSON，字段: title, summary, outline, chapters。"
                "chapters 为数组，每项包含 number, title, brief。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"请规划一部长篇{cfg.genre}小说，风格{cfg.style}。"
                f"先给出前{cfg.chapters_per_cycle}章任务。"
            ),
        },
    ]


def build_chapter_prompt(state: BotState, task: ChapterTask, cfg: BotConfig) -> list[dict[str, str]]:
    context = truncate_context(state.context_memory, cfg.max_context_chars)
    context_block = "\n".join(context) if context else "无"
    return [
        {
            "role": "system",
            "content": (
                "你是稳定更新的网文作者。注意人物设定一致、剧情连贯。"
                "直接输出正文，不要解释。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"小说标题: {state.novel_title}\n"
                f"小说概要: {state.novel_summary}\n"
                f"总纲: {state.outline}\n"
                f"上下文记忆(可能截断):\n{context_block}\n"
                f"请写第{task.number}章《{task.title}》，章节目标 {cfg.chapter_target_words} 字，"
                "并保证与前文衔接。"
            ),
        },
    ]


def init_outline(state: BotState, cfg: BotConfig, llm: LLMClient) -> None:
    text = call_with_retry("生成大纲", lambda: llm.chat(build_outline_prompt(cfg), 0.9), cfg.max_retry)
    data = parse_json_block(text)

    state.novel_title = data.get("title", f"{cfg.genre}长篇{int(time.time())}")
    state.novel_summary = data.get("summary", "一个普通人卷入超常世界，逐步成长并改写秩序。")
    state.outline = data.get("outline", "主角在危机中崛起，逐步揭开世界真相。")

    chapters = data.get("chapters") or []
    tasks: list[ChapterTask] = []
    for i, item in enumerate(chapters, start=1):
        tasks.append(
            ChapterTask(
                number=int(item.get("number", i)),
                title=item.get("title", f"第{i}章"),
                brief=item.get("brief", "推进主线冲突"),
            )
        )

    if not tasks:
        tasks = [
            ChapterTask(number=1, title="雨夜引子", brief="主角遭遇异常事件"),
            ChapterTask(number=2, title="失控回响", brief="危机扩大，线索浮现"),
            ChapterTask(number=3, title="第一次反击", brief="主角做出关键选择"),
        ]

    state.chapter_tasks = tasks
    state.phase = "CREATE_NOVEL"


def create_novel(state: BotState, cfg: BotConfig, publisher: BackendPublisher) -> None:
    novel_id = call_with_retry(
        "发布小说",
        lambda: publisher.publish_create_novel(state.novel_title, state.novel_summary, cfg.genre),
        cfg.max_retry,
    )
    state.novel_id = novel_id
    state.phase = "WRITE_CHAPTER"


def write_and_publish_one_chapter(state: BotState, cfg: BotConfig, llm: LLMClient, publisher: BackendPublisher) -> bool:
    next_task = next((task for task in state.chapter_tasks if not task.done), None)
    if not next_task:
        state.phase = "EXPAND_TASKS"
        return False

    chapter_text = call_with_retry(
        f"生成章节#{next_task.number}",
        lambda: llm.chat(build_chapter_prompt(state, next_task, cfg), 0.85),
        cfg.max_retry,
    )

    call_with_retry(
        f"发布章节#{next_task.number}",
        lambda: publisher.publish_add_chapter(
            novel_id=state.novel_id or 0,
            number=next_task.number,
            title=next_task.title,
            content=chapter_text,
        ),
        cfg.max_retry,
    )

    next_task.done = True
    state.published_chapters += 1
    state.context_memory.append(
        f"第{next_task.number}章《{next_task.title}》摘要: {chapter_text[:680]}"
    )
    state.context_memory = truncate_context(state.context_memory, cfg.max_context_chars)
    return True


def expand_tasks(state: BotState, cfg: BotConfig, llm: LLMClient) -> None:
    start_no = max([task.number for task in state.chapter_tasks] + [0]) + 1
    request_count = cfg.chapters_per_cycle

    messages = [
        {
            "role": "system",
            "content": (
                "你是网文策划编辑。输出严格 JSON: {chapters:[{number,title,brief}]}，"
                "只生成新的后续章节任务。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"小说标题: {state.novel_title}\n"
                f"已有章节数: {state.published_chapters}\n"
                f"请从第{start_no}章开始规划接下来{request_count}章任务。"
            ),
        },
    ]

    text = call_with_retry("扩展章节任务", lambda: llm.chat(messages, 0.8), cfg.max_retry)
    data = parse_json_block(text)
    chapters = data.get("chapters") or []

    new_tasks: list[ChapterTask] = []
    for i, item in enumerate(chapters, start=start_no):
        new_tasks.append(
            ChapterTask(
                number=int(item.get("number", i)),
                title=item.get("title", f"第{i}章"),
                brief=item.get("brief", "推进剧情"),
            )
        )

    if not new_tasks:
        for i in range(start_no, start_no + request_count):
            new_tasks.append(ChapterTask(number=i, title=f"第{i}章", brief="推进剧情"))

    state.chapter_tasks.extend(new_tasks)
    state.phase = "WRITE_CHAPTER"


def run_once(state: BotState, cfg: BotConfig, llm: LLMClient, publisher: BackendPublisher) -> None:
    if state.phase == "INIT":
        init_outline(state, cfg, llm)
        return

    if state.phase == "CREATE_NOVEL":
        create_novel(state, cfg, publisher)
        return

    if state.phase == "WRITE_CHAPTER":
        wrote = write_and_publish_one_chapter(state, cfg, llm, publisher)
        if wrote:
            state.phase = "SLEEP"
        return

    if state.phase == "EXPAND_TASKS":
        expand_tasks(state, cfg, llm)
        return

    if state.phase == "SLEEP":
        print(f"[SLEEP] 休眠 {cfg.cycle_sleep_seconds}s，已发布 {state.published_chapters} 章")
        time.sleep(cfg.cycle_sleep_seconds)
        state.phase = "WRITE_CHAPTER"
        return

    state.phase = "INIT"


def main() -> None:
    cfg = BotConfig()
    llm = LLMClient(cfg)
    publisher = BackendPublisher(cfg)
    state = load_state()

    print("[BOOT] AI Author Bot 启动")
    print(f"[BOOT] provider={cfg.llm_provider}, backend={cfg.backend_base_url}")

    while True:
        try:
            run_once(state, cfg, llm, publisher)
        except KeyboardInterrupt:
            print("\n[STOP] 收到退出信号，保存状态并停止")
            save_state(state)
            break
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {exc}")
            state.phase = "SLEEP"
            time.sleep(min(cfg.cycle_sleep_seconds, 60))
        finally:
            save_state(state)


if __name__ == "__main__":
    main()
