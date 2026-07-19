"""
Agnes 智能体 API 视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class AgnesViewSet(viewsets.ViewSet):
    """Agnes 智能体 API"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='generate-novel')
    def generate_novel(self, request):
        """手动触发生成一部小说"""
        try:
            from apps.agnes_agent import get_agnes_agent
            
            agent = get_agnes_agent()
            
            # 获取参数
            chapters = int(request.data.get('chapters', 3000))
            
            novel = agent.generate_novel(max_chapters=chapters)
            
            if novel:
                return Response({
                    'status': 'success',
                    'message': f'成功生成小说: {novel.title}',
                    'data': {
                        'novel_id': novel.id,
                        'title': novel.title,
                        'category': novel.category.name if novel.category else None,
                        'chapters_count': novel.chapters.count(),
                        'word_count': novel.word_count,
                        'created_at': novel.created_at.isoformat(),
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': '无法生成小说，请检查 AI 生成器配置'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"生成小说失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'生成失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='status')
    def status_view(self, request):
        """获取 Agnes 系统状态"""
        try:
            from apps.agnes_agent import get_agnes_agent
            from apps.novels.models import Novel
            from apps.users.models import User
            
            agent = get_agnes_agent()
            
            # 统计 Agnes 生成的小说
            agnes_user = User.objects.filter(username='agnes_ai_author').first()
            agnes_novels_count = 0
            agnes_chapters_count = 0
            agnes_total_words = 0
            
            if agnes_user:
                agnes_novels = Novel.objects.filter(author=agnes_user)
                agnes_novels_count = agnes_novels.count()
                for novel in agnes_novels:
                    agnes_chapters_count += novel.chapters.count()
                    agnes_total_words += novel.word_count
            
            return Response({
                'status': 'online',
                'message': 'Agnes 智能体在线',
                'data': {
                    'agent_name': 'Agnes AI',
                    'agent_version': '1.0',
                    'agent_status': 'active',
                    'ai_generator_available': agent.generator is not None,
                    'statistics': {
                        'total_novels': agnes_novels_count,
                        'total_chapters': agnes_chapters_count,
                        'total_words': agnes_total_words,
                    },
                    'features': {
                        'auto_generation': True,
                        'types_count': 11,
                        'chapters_per_novel': '3000+',
                        'words_per_chapter': '3000+',
                    }
                }
            })
        
        except Exception as e:
            logger.error(f"获取状态失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'获取状态失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='start-scheduler')
    def start_scheduler(self, request):
        """启动定时任务"""
        try:
            from apps.agnes_agent import get_agnes_agent
            
            agent = get_agnes_agent()
            interval = int(request.data.get('interval', 30))
            
            success = agent.schedule_auto_generation(interval_minutes=interval)
            
            if success:
                return Response({
                    'status': 'success',
                    'message': f'Agnes 定时任务已启动，间隔: {interval} 分钟',
                    'data': {
                        'interval_minutes': interval,
                        'started_at': timezone.now().isoformat(),
                    }
                })
            else:
                return Response({
                    'status': 'error',
                    'message': '无法启动定时任务'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"启动定时任务失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'启动失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
