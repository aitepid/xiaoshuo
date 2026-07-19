#!/usr/bin/env python
"""
同步本地数据到 Render 生产数据库
使用 PostgreSQL 远程连接进行数据同步
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import django
from django.conf import settings

# 配置 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.novels.models import Category, Novel, Chapter
from apps.users.models import User
from django.db.models import Sum

def get_db_connection(db_config):
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(
            host=db_config['HOST'],
            port=db_config['PORT'],
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD']
        )
        return conn
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None

def get_render_db_config():
    """从环境变量获取 Render 数据库配置"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ 未找到 DATABASE_URL 环境变量")
        return None
    
    # 解析 postgresql:// URL
    # postgresql://user:password@host:port/dbname
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
        }
        return config
    except Exception as e:
        print(f"❌ 解析 DATABASE_URL 失败: {e}")
        return None

def export_novels_sql():
    """导出小说相关的 SQL 数据"""
    local_db = settings.DATABASES['default']
    conn = get_db_connection(local_db)
    
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        # 导出分类
        cursor.execute("""
            SELECT id, name, description, created_at 
            FROM novels_category 
            ORDER BY id
        """)
        categories = cursor.fetchall()
        print(f"📚 导出分类数: {len(categories)}")
        
        # 导出小说
        cursor.execute("""
            SELECT id, title, author_id, category_id, status, review_status, word_count, created_at
            FROM novels_novel
            WHERE author_id IS NOT NULL
            ORDER BY id
        """)
        novels = cursor.fetchall()
        print(f"📖 导出小说数: {len(novels)}")
        
        # 导出章节 (只导出前100章作为示例，避免数据太大)
        cursor.execute("""
            SELECT id, novel_id, chapter_number, title, content, publish_status, word_count, published_at
            FROM novels_chapter
            WHERE novel_id IN (SELECT id FROM novels_novel WHERE author_id IS NOT NULL)
            ORDER BY novel_id, chapter_number
            LIMIT 50000
        """)
        chapters = cursor.fetchall()
        print(f"📄 导出章节数: {len(chapters)}")
        
        return {
            'categories': categories,
            'novels': novels,
            'chapters': chapters
        }
    finally:
        cursor.close()
        conn.close()

def insert_to_render(data):
    """向 Render 数据库插入数据"""
    render_config = get_render_db_config()
    
    if not render_config:
        print("❌ 无法获取 Render 数据库配置")
        return False
    
    conn = get_db_connection(render_config)
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 插入分类
        print("\n📥 开始插入分类...")
        for cat_id, name, desc, created_at in data['categories']:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO novels_category (id, name, description, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET 
                        name = EXCLUDED.name,
                        description = EXCLUDED.description
                """),
                [cat_id, name, desc, created_at]
            )
        conn.commit()
        print(f"✅ 插入分类完成: {len(data['categories'])} 条")
        
        # 插入小说
        print("\n📥 开始插入小说...")
        for novel_id, title, author_id, category_id, status, review_status, word_count, created_at in data['novels']:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO novels_novel 
                    (id, title, author_id, category_id, status, review_status, word_count, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET 
                        title = EXCLUDED.title,
                        category_id = EXCLUDED.category_id,
                        word_count = EXCLUDED.word_count
                """),
                [novel_id, title, author_id, category_id, status, review_status, word_count, created_at]
            )
        conn.commit()
        print(f"✅ 插入小说完成: {len(data['novels'])} 条")
        
        # 插入章节
        print("\n📥 开始插入章节...")
        for ch_id, novel_id, chapter_num, title, content, pub_status, word_count, published_at in data['chapters']:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO novels_chapter 
                    (id, novel_id, chapter_number, title, content, publish_status, word_count, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET 
                        title = EXCLUDED.title,
                        word_count = EXCLUDED.word_count
                """),
                [ch_id, novel_id, chapter_num, title, content, pub_status, word_count, published_at]
            )
            if ch_id % 5000 == 0:
                conn.commit()
                print(f"  ⏳ 已插入 {ch_id} 章...")
        
        conn.commit()
        print(f"✅ 插入章节完成: {len(data['chapters'])} 条")
        
        return True
        
    except Exception as e:
        print(f"❌ 插入数据失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    print("=" * 70)
    print("Render 数据库同步工具")
    print("=" * 70)
    
    # 导出本地数据
    print("\n📤 正在从本地数据库导出数据...")
    data = export_novels_sql()
    
    if not data:
        print("❌ 导出失败，退出")
        return False
    
    # 检查是否有 Render 数据库配置
    render_url = os.getenv('DATABASE_URL')
    if not render_url:
        print("\n⚠️  未检测到 DATABASE_URL 环境变量")
        print("   需要设置 Render 数据库 URL 才能同步")
        print("   在本地测试时可跳过此步骤")
        return False
    
    # 插入到 Render
    print("\n📤 开始同步到 Render 数据库...")
    if insert_to_render(data):
        print("\n" + "=" * 70)
        print("✅ 数据同步完成！")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ 数据同步失败！")
        print("=" * 70)
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
