"""
Agnes 智能体 - 自动生成小说的后台任务系统
"""

import os
import logging
from datetime import datetime
from typing import Optional
from django.db import transaction
from django.utils import timezone

from apps.novels.models import Novel, Category, Chapter
from apps.users.models import User

logger = logging.getLogger(__name__)


class AgnesAgent:
    """Agnes 智能体 - 自动生成小说"""
    
    def __init__(self):
        """初始化 Agnes 智能体"""
        try:
            from apps.ai_content_generator import AIContentGenerator
            self.generator = AIContentGenerator()
        except ImportError:
            logger.error("AI 内容生成器模块未加载，请检查 anthropic 包是否安装")
            self.generator = None
        except Exception as e:
            logger.error(f"初始化 AI 内容生成器失败: {str(e)}")
            self.generator = None
    
    def ensure_author_exists(self) -> User:
        """确保系统作者存在"""
        author, created = User.objects.get_or_create(
            username='agnes_ai_author',
            defaults={
                'email': 'agnes@xiaoshuo.local',
                'first_name': 'Agnes',
                'last_name': 'AI',
                'is_active': True,
            }
        )
        if created:
            logger.info(f"创建 Agnes 作者账户: {author.username}")
        return author
    
    def ensure_category_exists(self, category_name: str) -> Category:
        """确保分类存在"""
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'{category_name}类型小说'}
        )
        if created:
            logger.info(f"创建新分类: {category.name}")
        return category
    
    def generate_novel(self, max_chapters: int = 3000) -> Optional[Novel]:
        """
        生成一部新小说
        
        参数:
            max_chapters: 最大生成章节数（演示版本实际可能少于这个数）
        
        返回:
            创建的 Novel 对象，或 None 如果失败
        """
        if not self.generator:
            logger.error("AI 生成器不可用，无法生成小说")
            return None
        
        try:
            # 生成小说数据
            logger.info("🚀 Agnes 开始生成新小说...")
            novel_data = self.generator.generate_novel_batch(chapters_count=max_chapters)
            
            # 获取或创建作者
            author = self.ensure_author_exists()
            
            # 获取或创建分类
            category = self.ensure_category_exists(novel_data['category'])
            
            with transaction.atomic():
                # 创建小说
                novel = Novel.objects.create(
                    author=author,
                    title=novel_data['title'],
                    summary=novel_data['summary'],
                    category=category,
                    status=Novel.PublishStatus.ONGOING,
                    review_status=Novel.ReviewStatus.APPROVED,  # 自动批准 AI 生成的小说
                    word_count=0,
                )
                
                logger.info(f"✨ 创建小说: {novel.title} (ID: {novel.id})")
                
                # 批量创建章节
                chapters_to_create = []
                total_words = 0
                
                for chapter_data in novel_data['chapters']:
                    chapter = Chapter(
                        novel=novel,
                        chapter_number=chapter_data['chapter_number'],
                        title=chapter_data['title'],
                        content=chapter_data['content'],
                        word_count=chapter_data['word_count'],
                        publish_status=Chapter.PublishStatus.PUBLISHED,
                        review_status=Chapter.ReviewStatus.APPROVED,
                        published_at=timezone.now(),
                    )
                    chapters_to_create.append(chapter)
                    total_words += chapter_data['word_count']
                    
                    # 每 500 章批量插入一次
                    if len(chapters_to_create) >= 500:
                        Chapter.objects.bulk_create(chapters_to_create, batch_size=100)
                        logger.info(f"  已创建 {len(chapters_to_create)} 章")
                        chapters_to_create = []
                
                # 创建剩余章节
                if chapters_to_create:
                    Chapter.objects.bulk_create(chapters_to_create, batch_size=100)
                    logger.info(f"  已创建 {len(chapters_to_create)} 章")
                
                # 更新小说字数
                novel.word_count = total_words
                novel.save()
                
                chapters_count = novel.chapters.count()
                logger.info(f"📊 小说完成: {chapters_count} 章，{total_words} 字")
                
                return novel
        
        except Exception as e:
            logger.error(f"❌ 生成小说失败: {str(e)}", exc_info=True)
            return None
    
    def auto_generate_task(self):
        """定时任务：自动生成小说"""
        logger.info(f"[{datetime.now().isoformat()}] Agnes 开始自动生成任务...")
        
        try:
            novel = self.generate_novel()
            if novel:
                logger.info(f"✅ 任务完成: 成功创建小说 '{novel.title}'")
            else:
                logger.error("⚠️  任务失败: 无法创建小说")
        
        except Exception as e:
            logger.error(f"❌ 自动生成任务异常: {str(e)}", exc_info=True)
    
    def schedule_auto_generation(self, interval_minutes: int = 30):
        """
        启动定时自动生成任务
        
        参数:
            interval_minutes: 执行间隔（分钟）
        """
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
        except ImportError:
            logger.error("APScheduler 未安装，请运行: pip install APScheduler")
            return False
        
        try:
            scheduler = BackgroundScheduler()
            
            # 检查是否已经有相同的任务
            if scheduler.get_job('agnes_novel_generation'):
                logger.info("Agnes 自动生成任务已在运行")
                return True
            
            # 添加定时任务
            scheduler.add_job(
                self.auto_generate_task,
                IntervalTrigger(minutes=interval_minutes),
                id='agnes_novel_generation',
                name='Agnes 自动生成小说',
                replace_existing=True
            )
            
            if not scheduler.running:
                scheduler.start()
                logger.info(f"✅ Agnes 智能体已启动，每 {interval_minutes} 分钟生成一部小说")
            
            return True
        
        except Exception as e:
            logger.error(f"启动定时任务失败: {str(e)}")
            return False


# 全局 Agnes 实例
agnes_agent: Optional[AgnesAgent] = None


def get_agnes_agent() -> AgnesAgent:
    """获取或创建 Agnes 智能体实例"""
    global agnes_agent
    if agnes_agent is None:
        agnes_agent = AgnesAgent()
    return agnes_agent


def start_agnes_scheduler(interval_minutes: int = 30) -> bool:
    """启动 Agnes 自动生成任务"""
    agent = get_agnes_agent()
    return agent.schedule_auto_generation(interval_minutes)
