"""
智能评分系统 - 简化测试（无emoji版本）
不依赖完整环境的快速验证
"""

def test_project_structure():
    """测试项目结构"""
    print("=" * 60)
    print("项目结构快速验证")
    print("=" * 60)
    
    import os
    import sys
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 核心文件检查
    core_files = [
        "backend/app.py",
        "backend/database.py",
        "backend/schemas.py",
        "backend/scoring.py",
        "backend/ml_models/project_classifier.py",
        "backend/ml_models/tech_stack_analyzer.py",
        "backend/ml_models/feature_extractor.py",
        "backend/ml_models/nlp_processor.py",
        "backend/routers/projects.py",
        "backend/routers/scoring.py",
        "backend/routers/analysis.py",
        "config.py",
        "requirements.txt"
    ]
    
    print("\n核心文件检查:")
    all_ok = True
    
    for file_path in core_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"  OK {file_path} ({size:,} bytes)")
        else:
            print(f"  X {file_path} - 缺失")
            all_ok = False
    
    return all_ok


def test_config_content():
    """测试配置文件内容"""
    print("\n" + "=" * 60)
    print("配置文件内容验证")
    print("=" * 60)
    
    import os
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.py")
    
    if not os.path.exists(config_path):
        print("  X config.py 不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键配置项
        checks = [
            ("数据库配置", "DATABASE_URL" in content),
            ("模型配置", "MODEL_CACHE_DIR" in content),
            ("评分权重", "SCORE_WEIGHTS" in content),
            ("项目分类", "PROJECT_CATEGORIES" in content),
            ("技术栈配置", "TECH_STACKS" in content)
        ]
        
        print("  关键配置项检查:")
        all_ok = True
        
        for name, exists in checks:
            if exists:
                print(f"    OK {name}")
            else:
                print(f"    X {name}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"  X 读取配置文件失败: {e}")
        return False


def main():
    """主函数"""
    try:
        print("智能评分系统 - 验证")
        print("=" * 60)
        
        # 运行测试
        test1 = test_project_structure()
        test2 = test_config_content()
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("验证汇总")
        print("=" * 60)
        
        tests = [("项目结构", test1), ("配置文件", test2)]
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        print(f"  通过检查: {passed}/{total}")
        
        if passed == total:
            print("\n完成！所有核心文件已创建，结构完整。")
            print("\n下一步:")
            print("  1. 激活conda环境: conda activate your_env")
            print("  2. 安装依赖: pip install -r requirements.txt")
        else:
            print("\n部分检查未通过:")
            for test_name, result in tests:
                if not result:
                    print(f"  - {test_name}")
        
        return passed == total
        
    except Exception as e:
        print(f"验证过程中出错: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)