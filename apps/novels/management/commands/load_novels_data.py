"""
Django 管理命令：将导出的 JSON 数据导入数据库
使用方法：python manage.py load_novels_data data_export.json
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import json
import os


class Command(BaseCommand):
    help = '从 JSON 文件导入小说数据'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='导出的 JSON 数据文件路径'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空现有数据'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        # 检查文件是否存在
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'❌ 文件不存在: {json_file}'))
            return
        
        file_size = os.path.getsize(json_file) / (1024 * 1024)  # MB
        self.stdout.write(
            self.style.SUCCESS(f'\n📤 准备导入数据')
        )
        self.stdout.write(f'   文件: {json_file}')
        self.stdout.write(f'   大小: {file_size:.2f} MB\n')
        
        # 使用 Django 的 loaddata 命令
        try:
            call_command('loaddata', json_file, verbosity=2)
            self.stdout.write(
                self.style.SUCCESS('\n✅ 数据导入完成！')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ 导入失败: {str(e)}')
            )
