import json
import time
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.novels.models import Chapter, Novel

User = get_user_model()


def _parse_key_value_text(raw: str) -> dict:
    payload = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            payload[key.strip()] = value.strip()
    return payload


class OpenAICompatCompletionsAPIView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def _resolve_creator(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None, "缺少 Bearer Token。"
        token = auth.split(" ", 1)[1].strip()

        jwt_auth = JWTAuthentication()
        try:
            validated = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated)
            return user, None
        except Exception:
            pass

        allowed = {item.strip() for item in getattr(settings, "OPENAI_COMPAT_API_KEYS", "").split(",") if item.strip()}

        if token not in allowed:
            return None, "无效的创作 Token。"

        creator_id = request.data.get("creator_id")
        if not creator_id:
            return None, "静态 API Key 需要提供 creator_id。"

        user = User.objects.filter(id=creator_id).first()
        if not user:
            return None, "creator_id 对应用户不存在。"
        return user, None

    def _extract_action(self, messages):
        for msg in messages:
            if msg.get("role") == "system":
                content = (msg.get("content") or "").strip().upper()
                if "ACTION:" in content:
                    return content.split("ACTION:", 1)[1].strip()
        return ""

    def _extract_payload(self, messages):
        user_msgs = [m for m in messages if m.get("role") in {"user", "assistant"}]
        if not user_msgs:
            return {}
        raw = user_msgs[-1].get("content") or ""
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw)
        except Exception:
            return _parse_key_value_text(str(raw))

    @transaction.atomic
    def post(self, request):
        messages = request.data.get("messages", [])
        if not isinstance(messages, list):
            return Response({"error": "messages 必须为数组。"}, status=status.HTTP_400_BAD_REQUEST)

        creator, err = self._resolve_creator(request)
        if err:
            return Response({"error": err}, status=status.HTTP_401_UNAUTHORIZED)

        action = self._extract_action(messages)
        payload = self._extract_payload(messages)

        if action == "CREATE_NOVEL":
            title = payload.get("title")
            if not title:
                return Response({"error": "CREATE_NOVEL 需要 title。"}, status=status.HTTP_400_BAD_REQUEST)

            novel = Novel.objects.create(
                author=creator,
                title=title,
                summary=payload.get("summary", ""),
                cover_url=payload.get("cover_url", ""),
                category=payload.get("category", "AI创作"),
                status=Novel.PublishStatus.ONGOING,
                review_status=Novel.ReviewStatus.PENDING,
            )
            result_text = f"Novel created: id={novel.id}, title={novel.title}, status=pending"

        elif action == "ADD_CHAPTER":
            novel_id = payload.get("novel_id")
            title = payload.get("title")
            content = payload.get("content")
            if not novel_id or not title or not content:
                return Response({"error": "ADD_CHAPTER 需要 novel_id/title/content。"}, status=status.HTTP_400_BAD_REQUEST)

            novel = Novel.objects.filter(id=novel_id, author=creator).first()
            if not novel:
                return Response({"error": "小说不存在或无权限。"}, status=status.HTTP_404_NOT_FOUND)

            latest = Chapter.objects.filter(novel=novel).order_by("-chapter_number").first()
            next_number = payload.get("chapter_number") or (latest.chapter_number + 1 if latest else 1)

            chapter = Chapter.objects.create(
                novel=novel,
                chapter_number=next_number,
                title=title,
                volume_title=payload.get("volume_title", "默认卷"),
                content=content,
                publish_status=Chapter.PublishStatus.DRAFT,
                review_status=Chapter.ReviewStatus.PENDING,
            )
            Novel.objects.filter(id=novel.id).update(word_count=novel.word_count + chapter.word_count)
            result_text = f"Chapter created: id={chapter.id}, novel_id={novel.id}, chapter={chapter.chapter_number}, status=pending"

        else:
            return Response(
                {"error": "未识别 action。请在 system message 使用 ACTION: CREATE_NOVEL 或 ACTION: ADD_CHAPTER"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": f"cmpl-{uuid.uuid4().hex}",
                "object": "text_completion",
                "created": int(time.time()),
                "model": request.data.get("model", "xiaoshuo-publisher"),
                "choices": [{"index": 0, "text": result_text, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            },
            status=status.HTTP_200_OK,
        )
