"""
高效的数据同步脚本 - 直接创建模型对象，避免大文件 JSON 导入
"""

import json
import os
import sys
import django
from pathlib import Path

# 配置 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.novels.models import Category, Novel, Chapter
from apps.users.models import User
from django.db.models import Sum
from django.db import transaction

def check_render_env():
    """检查是否在 Render 环境中运行"""
    return os.getenv('RENDER') == 'true'

def get_existing_count():
    """获取数据库中已有的数据量"""
    return {
        'categories': Category.objects.count(),
        'novels': Novel.objects.count(),
        'chapters': Chapter.objects.count(),
    }

def create_categories():
    """创建分类"""
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
    
    return categories

def create_novels_and_chapters(categories):
    """创建小说和章节"""
    
    # 获取或创建作者用户
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
    
    created_novels = []
    
    for i, novel_data in enumerate(novels_data, 1):
        print(f"  [{i}/{len(novels_data)}] {novel_data['title']}")
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
            # 创建3000章
            chapters_to_create = []
            for chapter_num in range(1, 3001):
                chapter = Chapter(
                    novel=novel,
                    chapter_number=chapter_num,
                    title=f'第{chapter_num}章',
                    content=f'这是第{chapter_num}章的内容。' * 500,  # 填充内容到约2000字
                    publish_status=Chapter.PublishStatus.PUBLISHED,
                    review_status=Chapter.ReviewStatus.APPROVED,
                    word_count=2000,
                )
                chapters_to_create.append(chapter)
                
                # 每500章批量创建
                if len(chapters_to_create) >= 500:
                    Chapter.objects.bulk_create(chapters_to_create, batch_size=100)
                    chapters_to_create = []
            
            # 创建剩余章节
            if chapters_to_create:
                Chapter.objects.bulk_create(chapters_to_create, batch_size=100)
            
            # 更新小说字数
            word_count = novel.chapters.aggregate(total=Sum('word_count'))['total'] or 0
            novel.word_count = word_count
            novel.save()
        
        created_novels.append(novel)
    
    return created_novels

def sync_to_render():
    """同步数据到 Render"""
    print("\n" + "=" * 70)
    print("小说数据同步到生产环境")
    print("=" * 70)
    
    # 检查环境
    if not check_render_env():
        print("⚠️  未检测到 Render 环境标志")
        print("   本脚本可在本地或 Render 上运行")
    
    # 显示当前数据
    counts_before = get_existing_count()
    print("\n📊 同步前数据统计:")
    print(f"   分类: {counts_before['categories']}")
    print(f"   小说: {counts_before['novels']}")
    print(f"   章节: {counts_before['chapters']}")
    
    # 创建分类
    print("\n📝 创建分类...")
    categories = create_categories()
    print(f"✅ 分类已创建/更新: {len(categories)} 个")
    
    # 创建小说和章节
    print("\n📝 创建小说和章节...")
    with transaction.atomic():
        novels = create_novels_and_chapters(categories)
    
    print(f"✅ 小说已创建: {len(novels)} 部")
    
    # 显示同步后数据
    counts_after = get_existing_count()
    print("\n📊 同步后数据统计:")
    print(f"   分类: {counts_after['categories']}")
    print(f"   小说: {counts_after['novels']}")
    print(f"   章节: {counts_after['chapters']}")
    
    print("\n" + "=" * 70)
    print("✅ 数据同步完成!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    sync_to_render()
