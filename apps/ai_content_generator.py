"""
AI 内容生成器 - 使用 Claude 或其他 AI 生成高质量小说内容
"""

import os
import json
from typing import Optional, Tuple
import anthropic

# 小说类型列表（按顺序循环使用）
NOVEL_TYPES = [
    {
        "name": "悬疑推理",
        "description": "充满谜团和推理元素的悬疑故事",
        "category": "悬疑",
        "style": "紧张刺激、逻辑严密、充满反转"
    },
    {
        "name": "科幻冒险",
        "description": "未来世界、太空旅行、高科技设定的故事",
        "category": "科幻",
        "style": "想象丰富、设定新颖、充满未知"
    },
    {
        "name": "奇幻魔法",
        "description": "魔法世界、异能设定、神秘力量的故事",
        "category": "奇幻",
        "style": "世界观宏大、充满奇观、神秘莫测"
    },
    {
        "name": "爱情言情",
        "description": "感人至深的爱情故事",
        "category": "爱情",
        "style": "温暖感人、情感细腻、柔情蜜意"
    },
    {
        "name": "都市情感",
        "description": "现代城市、职场、生活故事",
        "category": "都市",
        "style": "贴近生活、真实细腻、充满人情味"
    },
    {
        "name": "历史穿越",
        "description": "历史背景或穿越时空的故事",
        "category": "历史",
        "style": "厚重沧桑、文化底蕴、史诗感"
    },
    {
        "name": "游戏竞技",
        "description": "网络游戏、电竞竞技的故事",
        "category": "网游",
        "style": "紧张激烈、热血沸腾、充满挑战"
    },
    {
        "name": "克苏鲁恐怖",
        "description": "诡异、恐怖、疯狂的故事",
        "category": "克苏鲁",
        "style": "诡异压抑、恐怖惊悚、超越理性"
    },
    {
        "name": "高能刺激",
        "description": "高潮迭起、刺激紧张的故事",
        "category": "高能",
        "style": "节奏飞快、惊悚刺激、高潮不断"
    },
    {
        "name": "魔幻冒险",
        "description": "魔法、妖怪、奇幻世界的故事",
        "category": "魔幻",
        "style": "充满想象、妖怪妖魅、魔法奇幻"
    },
    {
        "name": "二次元",
        "description": "动漫、漫画、虚拟世界的故事",
        "category": "二次元",
        "style": "萌萌哒、充满趣味、非现实感"
    },
]


class AIContentGenerator:
    """AI 内容生成器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY 未设置")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.current_type_index = 0
    
    def get_next_novel_type(self) -> dict:
        """获取下一个小说类型（循环使用）"""
        novel_type = NOVEL_TYPES[self.current_type_index]
        self.current_type_index = (self.current_type_index + 1) % len(NOVEL_TYPES)
        return novel_type
    
    def generate_novel_outline(self, novel_type: dict) -> dict:
        """生成小说大纲"""
        prompt = f"""
你是一位资深网络文学作家。请根据以下要求为我生成一部{novel_type['name']}小说的大纲：

类型：{novel_type['name']}
描述：{novel_type['description']}
风格：{novel_type['style']}

要求：
1. 生成一个有吸引力的小说标题
2. 写一段精彩的小说简介（100-200字）
3. 列出小说的核心剧情框架（5-10个主要情节点）

请以 JSON 格式返回，包含以下字段：
{{
    "title": "小说标题",
    "summary": "小说简介",
    "plot_points": ["情节1", "情节2", ...]
}}
"""
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            content = message.content[0].text
            # 从 response 中提取 JSON
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            print(f"解析 JSON 失败: {e}")
        
        return {
            "title": f"{novel_type['name']}故事",
            "summary": novel_type['description'],
            "plot_points": []
        }
    
    def generate_chapter(self, novel_title: str, chapter_number: int, 
                        chapter_title: str, context: str = "") -> Tuple[str, int]:
        """
        生成单个章节
        
        返回: (章节内容, 字数)
        """
        prompt = f"""
你是一位资深网络文学作家，正在创作《{novel_title}》。

现在需要写第 {chapter_number} 章，章节标题是：《{chapter_title}》

背景信息：{context if context else "无特殊背景信息"}

要求：
1. 章节内容必须至少 3000 个字
2. 内容要生动有趣、引人入胜
3. 符合网络文学的快餐阅读风格
4. 可以适当使用网络文学常见的表达手法
5. 确保内容的连贯性和逻辑性

请直接输出章节内容，无需其他说明。
"""
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,  # 生成足够的内容
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = message.content[0].text
        word_count = len(content.replace('\n', '').replace(' ', ''))
        
        # 如果内容不足 3000 字，进行补充
        if word_count < 3000:
            supplement_prompt = f"""
接下来我需要继续补充内容，使总字数达到 3000 字以上。

现有内容字数约：{word_count} 字

请根据已有内容的剧情走向，继续为这一章补充内容，确保：
1. 总字数达到 3000 字以上
2. 内容自然流畅，无生硬接续
3. 继续推进剧情发展

请直接输出补充内容。
"""
            
            supplement_message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": content},
                    {"role": "user", "content": supplement_prompt}
                ]
            )
            
            supplement_content = supplement_message.content[0].text
            content += "\n" + supplement_content
            word_count = len(content.replace('\n', '').replace(' ', ''))
        
        return content, word_count
    
    def generate_novel_batch(self, chapters_count: int = 3000) -> dict:
        """
        批量生成小说
        
        参数:
            chapters_count: 生成章节数
        
        返回: 包含小说信息的字典
        """
        print(f"🚀 开始生成新小说...")
        
        # 获取小说类型
        novel_type = self.get_next_novel_type()
        print(f"📚 小说类型: {novel_type['name']}")
        
        # 生成大纲
        print(f"📋 生成大纲...")
        outline = self.generate_novel_outline(novel_type)
        
        result = {
            "title": outline.get("title", f"{novel_type['name']}故事"),
            "summary": outline.get("summary", novel_type['description']),
            "category": novel_type['category'],
            "chapters": [],
            "total_words": 0,
            "total_chapters": chapters_count,
        }
        
        print(f"📖 小说标题: {result['title']}")
        print(f"📝 开始生成 {chapters_count} 章节...")
        
        # 生成章节
        for chapter_num in range(1, min(chapters_count + 1, 51)):  # 演示版本先生成 50 章
            chapter_title = f"第 {chapter_num} 章"
            if outline.get("plot_points") and chapter_num <= len(outline["plot_points"]):
                chapter_title = f"第 {chapter_num} 章：{outline['plot_points'][chapter_num - 1]}"
            
            print(f"  生成第 {chapter_num} 章...", end=" ")
            
            try:
                content, word_count = self.generate_chapter(
                    result["title"],
                    chapter_num,
                    chapter_title,
                    context=result["summary"]
                )
                
                result["chapters"].append({
                    "chapter_number": chapter_num,
                    "title": chapter_title,
                    "content": content,
                    "word_count": word_count,
                })
                
                result["total_words"] += word_count
                print(f"✓ ({word_count} 字)")
                
            except Exception as e:
                print(f"✗ 生成失败: {str(e)}")
                continue
        
        print(f"\n✨ 小说生成完成!")
        print(f"  总章节数: {len(result['chapters'])}")
        print(f"  总字数: {result['total_words']}")
        
        return result
