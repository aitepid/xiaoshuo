"""
Django 管理命令：启动 Agnes 智能体
使用方法: python manage.py start_agnes [--interval 30]
"""

from django.core.management.base import BaseCommand, CommandError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '启动 Agnes 智能体，自动生成小说'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='任务执行间隔（分钟，默认 30 分钟）'
        )
        
        parser.add_argument(
            '--now',
            action='store_true',
            help='立即执行一次任务，不等待间隔'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        run_now = options['now']
        
        try:
            from apps.agnes_agent import get_agnes_agent
            
            agent = get_agnes_agent()
            
            # 如果指定了 --now，立即执行一次
            if run_now:
                self.stdout.write(self.style.SUCCESS('🚀 立即执行一次小说生成任务...'))
                agent.auto_generate_task()
                self.stdout.write(self.style.SUCCESS('✅ 立即执行完成'))
            
            # 启动定时任务
            self.stdout.write(
                self.style.SUCCESS(f'🎯 启动 Agnes 定时任务，间隔: {interval} 分钟')
            )
            
            success = agent.schedule_auto_generation(interval_minutes=interval)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✨ Agnes 智能体已启动！\n'
                        f'   - 每 {interval} 分钟自动生成一部新小说\n'
                        f'   - 每部小说 3000+ 章，每章 3000+ 字\n'
                        f'   - 每次生成的小说类型不重复\n'
                        f'   - 小说自动发布到数据库\n'
                        f'\n💡 提示：小说会在以下位置显示：\n'
                        f'   - 前端首页: https://xiaoshuo-web.onrender.com/\n'
                        f'   - API: https://xiaoshuo-ng79.onrender.com/api/v1/novels/'
                    )
                )
                # 保持运行
                self.stdout.write(self.style.WARNING('⚙️  按 Ctrl+C 停止任务...'))
                try:
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stdout.write(self.style.WARNING('\n⛔ Agnes 已停止'))
            else:
                raise CommandError('无法启动定时任务，请检查 APScheduler 是否已安装')
        
        except ImportError as e:
            raise CommandError(f'导入模块失败: {str(e)}')
        except Exception as e:
            raise CommandError(f'启动失败: {str(e)}')
