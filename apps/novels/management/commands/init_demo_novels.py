"""
Django 管理命令：快速初始化小说数据（无需外部文件）
使用方法：python manage.py init_demo_novels
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from apps.novels.models import Category, Novel, Chapter
from apps.users.models import User


class Command(BaseCommand):
    help = '快速初始化演示小说数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建（删除现有数据）'
        )
        parser.add_argument(
            '--chapters',
            type=int,
            default=3000,
            help='每个小说的章节数 (默认3000)'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        num_chapters = options.get('chapters', 3000)
        
        self.stdout.write(self.style.SUCCESS('\n🎬 开始初始化小说数据'))
        self.stdout.write(f'   章节数/小说: {num_chapters}\n')
        
        with transaction.atomic():
            # 创建分类
            self.create_categories()
            
            # 创建小说和章节
            self.create_novels_and_chapters(num_chapters)
        
        self.stdout.write(self.style.SUCCESS('\n✅ 数据初始化完成！\n'))

    def create_categories(self):
        """创建所有分类"""
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
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
        
        self.stdout.write(f'✅ 分类创建完成: {len(categories_data)} 个')

    def create_novels_and_chapters(self, num_chapters):
        """创建小说和章节"""
        
        # 获取作者
        author, _ = User.objects.get_or_create(
            username='comedian_author',
            defaults={
                'email': 'comedian@xiaoshuo.local',
                'first_name': '喜剧',
                'last_name': '作者',
            }
        )
        
        novels_data = [
            {
                'title': '我的直播间被鬼占领了',
                'summary': '主播在直播间里突然被鬼占领，发生了一系列爆笑又诡异的事件，粉丝们在弹幕上狂笑。',
                'category': '都市',
            },
            {
                'title': '穿越后发现皇帝是个演员',
                'summary': '穿越到古代发现皇帝竟然是个演员，两个戏精碰撞产生了无尽的喜剧效果。',
                'category': '历史',
            },
            {
                'title': '我的老婆是个主播，全网都暗恋我',
                'summary': '娶了个网红主播当老婆，结果全网粉丝都暗恋自己，每天都在和粉丝斗智斗勇。',
                'category': '爱情',
            },
            {
                'title': '我的转职成了烂摊子',
                'summary': '在游戏里转职成垃圾收集员，却意外发现这是最赚钱的职业，从此走向人生巅峰。',
                'category': '网游',
            },
            {
                'title': '我被卷进一个诡异的克苏鲁小镇',
                'summary': '误入一个诡异小镇，全镇居民都在演戏，主角每天都在揭露真相和被打脸之间循环。',
                'category': '克苏鲁',
            },
            {
                'title': '我的剑灵是个段子手',
                'summary': '捡到一把剑，剑灵竟然是个段子高手，战斗中全是吐槽和冷笑话，敌人被气得投降。',
                'category': '奇幻',
            },
            {
                'title': '悬疑剧组的搞笑日常',
                'summary': '加入了一个专拍悬疑剧的剧组，演员们为了诠释角色引发了无数爆笑事件。',
                'category': '悬疑',
            },
            {
                'title': '我的对手是个美食主播',
                'summary': '电竞职业选手的对手突然改行做美食主播，两个领域的冠军竞争变成了厨艺比拼。',
                'category': '竞技',
            },
            {
                'title': '科幻穿梭者的倒霉日记',
                'summary': '时间穿梭机故障频繁，每次穿梭都进错了时代，上演了各式各样的穿越喜剧。',
                'category': '科幻',
            },
            {
                'title': '魔幻便利店的营业员',
                'summary': '在魔幻生物开的便利店工作，每天都在应对各种奇葩顾客和超自然事件。',
                'category': '魔幻',
            },
            {
                'title': '二次元家族的现实冒险',
                'summary': '动漫人物一家穿越到现实世界，用二次元逻辑生活在现代社会，引发一系列爆笑事件。',
                'category': '二次元',
            },
        ]
        
        for i, novel_data in enumerate(novels_data, 1):
            category = Category.objects.get(name=novel_data['category'])
            
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
            
            # 获取或创建章节
            existing_chapters = novel.chapters.count()
            
            if existing_chapters < num_chapters:
                # 需要创建章节
                chapters_to_create = []
                for chapter_num in range(existing_chapters + 1, num_chapters + 1):
                    chapter = Chapter(
                        novel=novel,
                        chapter_number=chapter_num,
                        title=f'第{chapter_num}章',
                        content=f'这是第{chapter_num}章的内容。' * 500,
                        publish_status=Chapter.PublishStatus.PUBLISHED,
                        review_status=Chapter.ReviewStatus.APPROVED,
                        word_count=2000,
                    )
                    chapters_to_create.append(chapter)
                    
                    # 分批创建
                    if len(chapters_to_create) >= 500:
                        Chapter.objects.bulk_create(chapters_to_create, batch_size=100)
                        chapters_to_create = []
                
                if chapters_to_create:
                    Chapter.objects.bulk_create(chapters_to_create, batch_size=100)
                
                self.stdout.write(
                    f'  [{i}/11] {novel.title} - '
                    f'新增{num_chapters - existing_chapters}章'
                )
            else:
                self.stdout.write(
                    f'  [{i}/11] {novel.title} - '
                    f'已有{existing_chapters}章（跳过）'
                )
            
            # 更新小说字数
            word_count = novel.chapters.aggregate(total=Sum('word_count'))['total'] or 0
            novel.word_count = word_count
            novel.save()
        
        self.stdout.write(f'\n✅ 小说创建完成: {len(novels_data)} 部')
