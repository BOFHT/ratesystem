"""
智能评分系统 - 设置验证脚本
验证项目结构和配置文件
"""

import os
import sys
import json
from pathlib import Path

def check_project_structure():
    """检查项目结构"""
    print("=" * 60)
    print("项目结构验证")
    print("=" * 60)
    
    required_dirs = [
        "backend",
        "backend/ml_models",
        "backend/routers",
        "scripts",
        "models",
        "utils",
        "data",
        "logs"
    ]
    
    required_files = [
        "README.md",
        "requirements.txt",
        "config.py",
        "backend/app.py",
        "backend/database.py",
        "backend/schemas.py",
        "backend/scoring.py",
        "backend/ml_models/__init__.py",
        "backend/ml_models/project_classifier.py",
        "backend/ml_models/tech_stack_analyzer.py",
        "backend/ml_models/feature_extractor.py",
        "backend/ml_models/nlp_processor.py",
        "backend/routers/projects.py",
        "backend/routers/scoring.py",
        "backend/routers/analysis.py",
        "scripts/init_database.py",
        "scripts/train_models.py",
        "scripts/integration_test.py"
    ]
    
    base_path = Path(__file__).parent
    
    # 检查目录
    print("\n📁 检查目录结构:")
    all_dirs_ok = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - 不存在")
            all_dirs_ok = False
    
    # 检查文件
    print("\n📄 检查核心文件:")
    all_files_ok = True
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✅ {file_path} ({size} bytes)")
        else:
            print(f"  ❌ {file_path} - 不存在")
            all_files_ok = False
    
    return all_dirs_ok and all_files_ok


def check_config_files():
    """检查配置文件"""
    print("\n" + "=" * 60)
    print("配置文件验证")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    config_files = {
        "config.py": base_path / "config.py",
        "requirements.txt": base_path / "requirements.txt"
    }
    
    all_configs_ok = True
    
    for name, path in config_files.items():
        if path.exists():
            try:
                content = path.read_text(encoding='utf-8')
                lines = len(content.split('\n'))
                print(f"  ✅ {name} - {lines} 行")
                
                # 特殊检查
                if name == "config.py":
                    if "class Settings" in content and "DATABASE_URL" in content:
                        print(f"    配置类正确")
                    else:
                        print(f"    ⚠️ 配置类可能不完整")
                        all_configs_ok = False
                
                elif name == "requirements.txt":
                    requirements = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    print(f"    依赖包: {len(requirements)} 个")
                    
            except Exception as e:
                print(f"  ❌ {name} - 读取失败: {e}")
                all_configs_ok = False
        else:
            print(f"  ❌ {name} - 不存在")
            all_configs_ok = False
    
    return all_configs_ok


def check_ml_models():
    """检查机器学习模型文件"""
    print("\n" + "=" * 60)
    print("机器学习模型验证")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    ml_dir = base_path / "backend" / "ml_models"
    
    if not ml_dir.exists():
        print("  ❌ ML模型目录不存在")
        return False
    
    model_files = list(ml_dir.glob("*.py"))
    
    print(f"  📊 找到 {len(model_files)} 个模型文件:")
    
    model_contents = {}
    all_models_ok = True
    
    for model_file in model_files:
        try:
            content = model_file.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            
            # 检查关键类
            if model_file.name == "project_classifier.py":
                if "class ProjectClassifier" in content:
                    status = "✅ 项目分类器"
                else:
                    status = "❌ 缺少ProjectClassifier类"
                    all_models_ok = False
                    
            elif model_file.name == "tech_stack_analyzer.py":
                if "class TechStackAnalyzer" in content:
                    status = "✅ 技术栈分析器"
                else:
                    status = "❌ 缺少TechStackAnalyzer类"
                    all_models_ok = False
                    
            elif model_file.name == "feature_extractor.py":
                if "class FeatureExtractor" in content:
                    status = "✅ 特征提取器"
                else:
                    status = "❌ 缺少FeatureExtractor类"
                    all_models_ok = False
                    
            elif model_file.name == "nlp_processor.py":
                if "class NLPProcessor" in content:
                    status = "✅ NLP处理器"
                else:
                    status = "❌ 缺少NLPProcessor类"
                    all_models_ok = False
                    
            else:
                status = "📄 其他模型文件"
            
            print(f"    {status} - {model_file.name} ({lines} 行)")
            model_contents[model_file.name] = lines
            
        except Exception as e:
            print(f"    ❌ {model_file.name} - 读取失败: {e}")
            all_models_ok = False
    
    return all_models_ok


def check_api_routers():
    """检查API路由"""
    print("\n" + "=" * 60)
    print("API路由验证")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    routers_dir = base_path / "backend" / "routers"
    
    if not routers_dir.exists():
        print("  ❌ 路由目录不存在")
        return False
    
    router_files = list(routers_dir.glob("*.py"))
    
    print(f"  📡 找到 {len(router_files)} 个路由文件:")
    
    all_routers_ok = True
    
    for router_file in router_files:
        try:
            content = router_file.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            
            # 检查关键内容
            if "APIRouter" in content and "@router" in content:
                # 统计端点数量
                endpoints = content.count("@router.")
                status = f"✅ {endpoints} 个端点"
            else:
                status = "❌ 不是有效的FastAPI路由"
                all_routers_ok = False
            
            print(f"    {status} - {router_file.name} ({lines} 行)")
            
        except Exception as e:
            print(f"    ❌ {router_file.name} - 读取失败: {e}")
            all_routers_ok = False
    
    return all_routers_ok


def check_scripts():
    """检查脚本文件"""
    print("\n" + "=" * 60)
    print("工具脚本验证")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    scripts_dir = base_path / "scripts"
    
    if not scripts_dir.exists():
        print("  ❌ 脚本目录不存在")
        return False
    
    script_files = list(scripts_dir.glob("*.py"))
    
    print(f"  🔧 找到 {len(script_files)} 个脚本文件:")
    
    all_scripts_ok = True
    
    for script_file in script_files:
        try:
            content = script_file.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            
            # 根据文件名识别脚本类型
            if script_file.name == "init_database.py":
                if "create_tables" in content:
                    status = "✅ 数据库初始化脚本"
                else:
                    status = "❌ 数据库脚本不完整"
                    all_scripts_ok = False
                    
            elif script_file.name == "train_models.py":
                if "train_project_classifier" in content:
                    status = "✅ 模型训练脚本"
                else:
                    status = "❌ 训练脚本不完整"
                    all_scripts_ok = False
                    
            elif script_file.name == "integration_test.py":
                if "IntegrationTest" in content:
                    status = "✅ 集成测试脚本"
                else:
                    status = "❌ 测试脚本不完整"
                    all_scripts_ok = False
                    
            else:
                status = "📄 其他脚本"
            
            print(f"    {status} - {script_file.name} ({lines} 行)")
            
        except Exception as e:
            print(f"    ❌ {script_file.name} - 读取失败: {e}")
            all_scripts_ok = False
    
    return all_scripts_ok


def generate_summary():
    """生成验证摘要"""
    print("\n" + "=" * 60)
    print("验证摘要")
    print("=" * 60)
    
    # 计算代码行数
    base_path = Path(__file__).parent
    
    total_lines = 0
    file_count = 0
    
    for py_file in base_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            total_lines += lines
            file_count += 1
        except:
            pass
    
    print(f"📊 项目规模统计:")
    print(f"   Python文件数: {file_count}")
    print(f"   总代码行数: {total_lines:,}")
    
    # 各模块统计
    modules = {
        "机器学习模型": base_path / "backend" / "ml_models",
        "API路由": base_path / "backend" / "routers",
        "工具脚本": base_path / "scripts",
        "核心模块": base_path / "backend"
    }
    
    for module_name, module_path in modules.items():
        if module_path.exists():
            module_lines = 0
            module_files = 0
            
            for py_file in module_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = len(content.split('\n'))
                    module_lines += lines
                    module_files += 1
                except:
                    pass
            
            if module_files > 0:
                print(f"  {module_name}: {module_files} 文件, {module_lines:,} 行")
    
    print("\n🎯 验证结论:")
    
    # 运行所有检查
    checks = [
        ("项目结构", check_project_structure()),
        ("配置文件", check_config_files()),
        ("ML模型", check_ml_models()),
        ("API路由", check_api_routers()),
        ("工具脚本", check_scripts())
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"  通过检查: {passed}/{total}")
    
    if passed == total:
        print("  ✅ 所有检查通过! 项目结构完整。")
        print("\n🚀 下一步:")
        print("  1. 设置Python虚拟环境")
        print("  2. 安装依赖: pip install -r requirements.txt")
        print("  3. 运行集成测试: python -m scripts.integration_test --full")
        print("  4. 训练模型: python -m scripts.train_models")
        print("  5. 启动服务: uvicorn backend.app:app --reload")
    else:
        print("  ⚠️ 部分检查未通过，需要修复。")
        
        for check_name, result in checks:
            if not result:
                print(f"    - {check_name} 检查失败")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = generate_summary()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"验证过程中出错: {e}")
        sys.exit(1)