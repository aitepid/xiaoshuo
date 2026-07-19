from django.core.cache import cache
from django.db.models import F, Q, Sum
from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import User
from .models import Category, Chapter, Novel
from .serializers import CategorySerializer, ChapterDetailSerializer, ChapterListSerializer, NovelDetailSerializer, NovelListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    @action(detail=False, methods=["post"], url_path="init-demo")
    def init_demo(self, request):
        """初始化演示小说数据"""
        try:
            with transaction.atomic():
                # 创建分类
                categories_data = [
                    {'name': '悬疑', 'description': '推理、悬念、谜团等故事'},
                    {'name': '科幻', 'description': '未来世界、太空冒险、黑科技等'},
                    {'name': '奇幻', 'description': '魔法、异能、诡异等故事'},
                    {'name': '爱情', 'description': '恋爱、感情、情感故事'},
                    {'name': '都市', 'description': '现代城市、职场、生活故事'},
                    {'name': '历史', 'description': '朝代更替、历史背景故事'},
                    {'name': '网游', 'description': '网络游戏、游戏世界故事'},
                    {'name': '竞技', 'description': '竞赛、比赛、竞争故事'},
                    {'name': '克苏鲁', 'description': '诡异、恐怖、未知事物'},
                    {'name': '高能', 'description': '刺激、紧张、高潮不断'},
                    {'name': '魔幻', 'description': '魔法、妖怪、奇幻世界'},
                    {'name': '二次元', 'description': '动漫、漫画、虚拟世界'},
                ]
                
                categories = {}
                for cat_data in categories_data:
                    cat, _ = Category.objects.get_or_create(
                        name=cat_data['name'],
                        defaults={'description': cat_data['description']}
                    )
                    categories[cat_data['name']] = cat
                
                # 获取或创建作者
                author, _ = User.objects.get_or_create(
                    username='comedian_author',
                    defaults={
                        'email': 'comedian@xiaoshuo.local',
                        'first_name': '喜剧',
                        'last_name': '作者',
                    }
                )
                
                # 小说数据
                novels_data = [
                    {'title': '我的直播间被鬼占领了', 'summary': '主播在直播间里突然被鬼占领，发生了一系列爆笑又诡异的事件。', 'category': '都市'},
                    {'title': '穿越后发现皇帝是个演员', 'summary': '穿越到古代发现皇帝竟然是个演员，两个戏精碰撞。', 'category': '历史'},
                    {'title': '我的老婆是个主播，全网都暗恋我', 'summary': '娶了个网红主播当老婆，全网粉丝都暗恋自己。', 'category': '爱情'},
                    {'title': '我的转职成了烂摊子', 'summary': '在游戏里转职成垃圾收集员，却成为最赚钱职业。', 'category': '网游'},
                    {'title': '我被卷进一个诡异的克苏鲁小镇', 'summary': '误入诡异小镇，全镇居民都在演戏。', 'category': '克苏鲁'},
                    {'title': '我的剑灵是个段子手', 'summary': '捡到一把剑，剑灵竟然是个段子高手。', 'category': '奇幻'},
                    {'title': '悬疑剧组的搞笑日常', 'summary': '加入专拍悬疑剧的剧组，演员们引发无数爆笑事件。', 'category': '悬疑'},
                    {'title': '我的对手是个美食主播', 'summary': '电竞职业选手的对手突然改行做美食主播。', 'category': '竞技'},
                    {'title': '科幻穿梭者的倒霉日记', 'summary': '时间穿梭机故障频繁，每次穿梭都进错时代。', 'category': '科幻'},
                    {'title': '魔幻便利店的营业员', 'summary': '在魔幻生物开的便利店工作，每天应对奇葩顾客。', 'category': '魔幻'},
                    {'title': '二次元家族的现实冒险', 'summary': '动漫人物一家穿越到现实世界，用二次元逻辑生活。', 'category': '二次元'},
                ]
                
                created_novels = 0
                created_chapters = 0
                
                for novel_data in novels_data:
                    category = categories[novel_data['category']]
                    
                    novel, created = Novel.objects.get_or_create(
                        title=novel_data['title'],
                        defaults={
                            'author': author,
                            'category': category,
                            'summary': novel_data['summary'],
                            'status': Novel.Status.ONGOING,
                            'review_status': Novel.ReviewStatus.APPROVED,
                            'word_count': 0,
                        }
                    )
                    
                    if created:
                        created_novels += 1
                        
                        # 创建3000章
                        chapters = []
                        for chapter_num in range(1, 3001):
                            chapter = Chapter(
                                novel=novel,
                                chapter_number=chapter_num,
                                title=f'第{chapter_num}章',
                                content='这是章节内容。' * 500,
                                publish_status=Chapter.PublishStatus.PUBLISHED,
                                review_status=Chapter.ReviewStatus.APPROVED,
                                word_count=2000,
                            )
                            chapters.append(chapter)
                            
                            if len(chapters) >= 500:
                                Chapter.objects.bulk_create(chapters, batch_size=100)
                                created_chapters += len(chapters)
                                chapters = []
                        
                        if chapters:
                            Chapter.objects.bulk_create(chapters, batch_size=100)
                            created_chapters += len(chapters)
                        
                        # 更新字数
                        word_count = novel.chapters.aggregate(total=Sum('word_count'))['total'] or 0
                        novel.word_count = word_count
                        novel.save()
            
            return Response({
                'status': 'success',
                'message': f'创建了 {created_novels} 部小说，{created_chapters} 章内容',
                'data': {
                    'novels_created': created_novels,
                    'chapters_created': created_chapters,
                    'total_words': created_chapters * 2000,
                }
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class NovelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["category", "status"]
    search_fields = ["title", "summary"]
    ordering_fields = ["updated_at", "click_count", "favorite_count", "created_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return Novel.objects.filter(review_status=Novel.ReviewStatus.APPROVED).select_related("author").prefetch_related("tags")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NovelDetailSerializer
        return NovelListSerializer

    @action(detail=False, methods=["get"], url_path="rankings")
    def rankings(self, request):
        cache_key = "novel_rankings_v1"
        data = cache.get(cache_key)
        if not data:
            queryset = self.get_queryset().order_by("-click_count", "-favorite_count", "-updated_at")[:20]
            data = NovelListSerializer(queryset, many=True).data
            cache.set(cache_key, data, timeout=300)
        return Response({"results": data})


class ChapterViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        novel_id = self.kwargs.get("novel_pk")
        now = timezone.now()
        queryset = Chapter.objects.filter(
            novel_id=novel_id,
            review_status=Chapter.ReviewStatus.APPROVED,
        ).filter(
            Q(publish_status=Chapter.PublishStatus.PUBLISHED)
            | Q(publish_status=Chapter.PublishStatus.SCHEDULED, scheduled_at__lte=now)
        )
        return queryset.select_related("novel")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ChapterDetailSerializer
        return ChapterListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Novel.objects.filter(id=instance.novel_id).update(click_count=F("click_count") + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
