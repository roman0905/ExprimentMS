#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建数据库表和初始化数据
"""

from database import create_tables, drop_tables, SessionLocal
from models import Batch, Person, Experiment, CompetitorFile, FingerBloodFile, Sensor
from datetime import datetime
import sys

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    try:
        # 创建表
        create_tables()
        print("✓ 数据库表创建成功")
        
        # 添加示例数据
        add_sample_data()
        print("✓ 示例数据添加成功")
        
        print("\n数据库初始化完成！")
        
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        sys.exit(1)

def add_sample_data():
    """添加示例数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(Batch).first():
            print("数据库中已有数据，跳过示例数据添加")
            return
        
        # 添加示例批次
        batch1 = Batch(
            batch_number="BATCH001",
            start_time=datetime(2024, 1, 1, 9, 0, 0),
            end_time=datetime(2024, 1, 1, 17, 0, 0)
        )
        batch2 = Batch(
            batch_number="BATCH002",
            start_time=datetime(2024, 1, 2, 9, 0, 0),
            end_time=None
        )
        
        db.add_all([batch1, batch2])
        db.commit()
        
        # 添加示例人员
        person1 = Person(
            person_name="张三",
            gender="Male",
            height_cm=175.5,
            weight_kg=70.2,
            age=25
        )
        person2 = Person(
            person_name="李四",
            gender="Female",
            height_cm=165.0,
            weight_kg=55.8,
            age=28
        )
        
        db.add_all([person1, person2])
        db.commit()
        
        # 添加示例实验
        experiment1 = Experiment(
            batch_id=batch1.batch_id,
            person_id=person1.person_id,
            experiment_content="血糖监测实验 - 第一阶段"
        )
        
        db.add(experiment1)
        db.commit()
        
        # 添加示例指尖血数据
        blood_data1 = FingerBloodFile(
            person_id=person1.person_id,
            batch_id=batch1.batch_id,
            collection_time=datetime(2024, 1, 1, 10, 0, 0),
            blood_glucose_value=5.6
        )
        blood_data2 = FingerBloodFile(
            person_id=person1.person_id,
            batch_id=batch1.batch_id,
            collection_time=datetime(2024, 1, 1, 14, 0, 0),
            blood_glucose_value=7.2
        )
        
        db.add_all([blood_data1, blood_data2])
        db.commit()
        
        # 添加示例传感器
        sensor1 = Sensor(
            sensor_name="血糖传感器-001",
            person_id=person1.person_id,
            batch_id=batch1.batch_id,
            start_time=datetime(2024, 1, 1, 9, 30, 0),
            end_time=datetime(2024, 1, 1, 16, 30, 0)
        )
        
        db.add(sensor1)
        db.commit()
        
        print("示例数据添加完成:")
        print(f"  - 批次: {db.query(Batch).count()} 条")
        print(f"  - 人员: {db.query(Person).count()} 条")
        print(f"  - 实验: {db.query(Experiment).count()} 条")
        print(f"  - 指尖血数据: {db.query(FingerBloodFile).count()} 条")
        print(f"  - 传感器: {db.query(Sensor).count()} 条")
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    print("警告：这将删除所有数据！")
    confirm = input("确认重置数据库？(yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            drop_tables()
            print("✓ 数据库表删除成功")
            
            create_tables()
            print("✓ 数据库表重新创建成功")
            
            add_sample_data()
            print("✓ 示例数据添加成功")
            
            print("\n数据库重置完成！")
            
        except Exception as e:
            print(f"✗ 数据库重置失败: {e}")
            sys.exit(1)
    else:
        print("操作已取消")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="重置数据库（删除所有数据）"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()