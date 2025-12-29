#!/usr/bin/env python3
"""
数据库修复脚本
用于修复旧版本数据库缺少列的问题

使用方法:
    python fix_database.py

或者直接删除数据库文件重新开始:
    Windows: del data\basketball_training.db
    Linux/Mac: rm data/basketball_training.db
"""
import sqlite3
import os
from pathlib import Path

def fix_database():
    """修复数据库，添加缺失的列"""
    
    # 查找数据库文件
    db_paths = [
        'data/basketball_training.db',
        os.path.join(os.path.dirname(__file__), 'data', 'basketball_training.db'),
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ 找不到数据库文件，可能是首次运行")
        print("   请直接运行: python run.py")
        return
    
    print(f"📁 找到数据库文件: {os.path.abspath(db_path)}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取现有列
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"📋 现有列: {existing_columns}")
    
    # 需要添加的列
    new_columns = {
        'age': 'INTEGER',
        'student_level': 'TEXT',
        'school_name': 'TEXT',
        'full_name': 'TEXT',
        'email': 'TEXT',
        'last_login': 'TIMESTAMP',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
    
    # 添加缺失的列
    added = 0
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                print(f"✅ 添加列: {column_name}")
                added += 1
            except sqlite3.OperationalError as e:
                print(f"⚠️ 添加列 {column_name} 失败: {e}")
    
    conn.commit()
    conn.close()
    
    if added > 0:
        print(f"\n🎉 成功添加 {added} 个列！")
        print("   现在可以正常运行: python run.py")
    else:
        print("\n✅ 数据库结构正常，无需修复")
        print("   如果仍有问题，请尝试删除数据库文件重新开始:")
        print(f"   Windows: del {db_path}")
        print(f"   Linux/Mac: rm {db_path}")

def delete_database():
    """删除数据库文件"""
    db_paths = [
        'data/basketball_training.db',
        os.path.join(os.path.dirname(__file__), 'data', 'basketball_training.db'),
    ]
    
    for path in db_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"✅ 已删除数据库文件: {path}")
            except Exception as e:
                print(f"❌ 删除失败: {e}")
                print("   请手动删除该文件")

if __name__ == '__main__':
    import sys
    
    print("=" * 50)
    print("🏀 YOLOv8篮球训练辅助系统 - 数据库修复工具")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--delete':
        print("⚠️ 将删除数据库文件（所有数据将丢失）")
        confirm = input("确认删除？(y/n): ")
        if confirm.lower() == 'y':
            delete_database()
        else:
            print("取消删除")
    else:
        fix_database()
        print()
        print("提示: 如果要完全重置数据库，请运行:")
        print("      python fix_database.py --delete")
