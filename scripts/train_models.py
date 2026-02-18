"""
模型训练脚本
自动化训练机器学习模型
"""

import asyncio
import logging
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from backend.ml_models.project_classifier import ProjectClassifier
from backend.ml_models.feature_extractor import FeatureExtractor
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(Path(settings.MODEL_CACHE_DIR).parent / "training.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def generate_training_data() -> List[Dict[str, Any]]:
    """生成训练数据"""
    logger.info("生成训练数据...")
    
    training_data = []
    
    # 项目分类训练数据
    category_examples = [
        {
            "name": "电商网站开发",
            "description": "使用React和Node.js构建的在线购物平台",
            "category": "web_development",
            "tech_stack": ["javascript", "react", "nodejs", "mongodb"]
        },
        {
            "name": "移动健康应用",
            "description": "基于Flutter的健康监测和运动追踪应用",
            "category": "mobile_app",
            "tech_stack": ["dart", "flutter", "firebase"]
        },
        {
            "name": "销售数据分析",
            "description": "使用Python和Pandas进行销售数据分析和可视化",
            "category": "data_science",
            "tech_stack": ["python", "pandas", "numpy", "matplotlib"]
        },
        {
            "name": "图像识别系统",
            "description": "基于深度学习的图像分类和物体识别系统",
            "category": "machine_learning",
            "tech_stack": ["python", "tensorflow", "opencv", "numpy"]
        },
        {
            "name": "智能家居控制",
            "description": "使用ESP32和MQTT协议的智能家居控制系统",
            "category": "iot",
            "tech_stack": ["c++", "arduino", "mqtt", "esp32"]
        },
        {
            "name": "区块链交易平台",
            "description": "基于以太坊的加密货币交易和智能合约平台",
            "category": "blockchain",
            "tech_stack": ["solidity", "ethereum", "web3", "javascript"]
        },
        {
            "name": "2D游戏开发",
            "description": "使用Unity引擎开发的2D平台跳跃游戏",
            "category": "game_development",
            "tech_stack": ["c#", "unity", "blender"]
        },
        {
            "name": "桌面文件管理",
            "description": "使用Electron开发的跨平台桌面文件管理工具",
            "category": "desktop_application",
            "tech_stack": ["javascript", "electron", "nodejs"]
        },
        {
            "name": "嵌入式控制系统",
            "description": "基于STM32的工业设备控制系统",
            "category": "embedded_systems",
            "tech_stack": ["c", "stm32", "freertos"]
        },
        {
            "name": "微服务架构",
            "description": "使用Kubernetes和Docker的微服务云平台",
            "category": "cloud_infrastructure",
            "tech_stack": ["docker", "kubernetes", "go", "postgresql"]
        }
    ]
    
    # 为每个类别生成更多变体
    for example in category_examples:
        # 原始示例
        training_data.append(example)
        
        # 变体1：简化描述
        variant1 = example.copy()
        variant1["description"] = f"这是一个{example['category']}项目"
        training_data.append(variant1)
        
        # 变体2：不同技术栈
        variant2 = example.copy()
        variant2["tech_stack"] = [tech + "-variant" for tech in example["tech_stack"][:2]]
        training_data.append(variant2)
        
        # 变体3：扩展描述
        variant3 = example.copy()
        variant3["description"] = f"这是一个高级{example['category']}项目，使用了现代技术栈和最佳实践"
        training_data.append(variant3)
    
    logger.info(f"生成了 {len(training_data)} 个训练样本")
    return training_data


async def train_project_classifier(training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """训练项目分类器"""
    try:
        logger.info("开始训练项目分类器...")
        
        classifier = ProjectClassifier()
        
        # 准备分类器训练数据
        classifier_training = []
        for item in training_data:
            text = f"{item['name']} {item['description']} {' '.join(item['tech_stack'])}"
            classifier_training.append({
                "text": text,
                "label": item["category"]
            })
        
        # 训练模型
        result = await classifier.train_model(classifier_training)
        
        logger.info(f"项目分类器训练完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"训练项目分类器失败: {e}")
        return {"error": str(e)}


async def train_feature_extractor(training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """训练特征提取器"""
    try:
        logger.info("开始训练特征提取器...")
        
        feature_extractor = FeatureExtractor()
        await feature_extractor.load_model()
        
        # 训练模型
        result = await feature_extractor.train_model(training_data)
        
        logger.info(f"特征提取器训练完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"训练特征提取器失败: {e}")
        return {"error": str(e)}


async def evaluate_models(training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """评估模型性能"""
    try:
        logger.info("开始评估模型性能...")
        
        from backend.ml_models import ProjectClassifier
        
        classifier = ProjectClassifier()
        await classifier.load_model()
        
        # 准备测试数据（使用后20%作为测试集）
        test_size = max(1, len(training_data) // 5)
        test_data = training_data[-test_size:]
        
        evaluation_results = []
        
        for test_item in test_data:
            try:
                # 测试分类器
                classification = await classifier.predict(test_item)
                
                evaluation_results.append({
                    "project": test_item["name"],
                    "true_category": test_item["category"],
                    "predicted_category": classification.get("name", "unknown"),
                    "confidence": classification.get("confidence", 0.0),
                    "correct": classification.get("name", "unknown") == test_item["category"]
                })
                
            except Exception as e:
                logger.error(f"评估项目失败 {test_item['name']}: {e}")
        
        # 计算准确率
        if evaluation_results:
            correct_count = sum(1 for r in evaluation_results if r["correct"])
            accuracy = correct_count / len(evaluation_results)
            
            logger.info(f"模型评估完成，准确率: {accuracy:.2%}")
            
            return {
                "accuracy": accuracy,
                "total_tests": len(evaluation_results),
                "correct_predictions": correct_count,
                "details": evaluation_results
            }
        else:
            return {"error": "没有有效的评估数据"}
        
    except Exception as e:
        logger.error(f"评估模型失败: {e}")
        return {"error": str(e)}


def save_training_report(results: Dict[str, Any], output_path: Path):
    """保存训练报告"""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"训练报告保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"保存训练报告失败: {e}")


async def main():
    """主函数"""
    try:
        logger.info("=" * 60)
        logger.info("开始自动化模型训练")
        logger.info("=" * 60)
        
        # 1. 生成训练数据
        training_data = generate_training_data()
        
        # 2. 训练项目分类器
        classifier_result = await train_project_classifier(training_data)
        
        # 3. 训练特征提取器
        feature_result = await train_feature_extractor(training_data)
        
        # 4. 评估模型性能
        evaluation_result = await evaluate_models(training_data)
        
        # 5. 生成训练报告
        results = {
            "training_summary": {
                "training_samples": len(training_data),
                "categories": list(set(item["category"] for item in training_data)),
                "training_timestamp": np.datetime64('now').astype(str)
            },
            "classifier_training": classifier_result,
            "feature_extractor_training": feature_result,
            "model_evaluation": evaluation_result,
            "system_info": {
                "model_cache_dir": str(settings.MODEL_CACHE_DIR),
                "config_version": settings.APP_VERSION
            }
        }
        
        # 保存报告
        report_path = Path(settings.MODEL_CACHE_DIR).parent / "training_report.json"
        save_training_report(results, report_path)
        
        # 输出摘要
        logger.info("=" * 60)
        logger.info("模型训练完成摘要")
        logger.info("=" * 60)
        
        if "accuracy" in evaluation_result:
            logger.info(f"📊 模型准确率: {evaluation_result['accuracy']:.2%}")
        
        if "perplexity" in feature_result:
            logger.info(f"📈 特征提取器困惑度: {feature_result['perplexity']:.2f}")
        
        logger.info(f"📁 训练报告: {report_path}")
        logger.info(f"📁 模型缓存: {settings.MODEL_CACHE_DIR}")
        
        logger.info("=" * 60)
        logger.info("模型训练流程完成!")
        logger.info("=" * 60)
        
        return results
        
    except Exception as e:
        logger.error(f"模型训练流程失败: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # 运行训练流程
    results = asyncio.run(main())
    
    # 输出最终状态
    if "error" in results:
        print(f"❌ 训练失败: {results['error']}")
        sys.exit(1)
    else:
        print("✅ 模型训练完成!")
        
        # 打印关键指标
        if "model_evaluation" in results and "accuracy" in results["model_evaluation"]:
            accuracy = results["model_evaluation"]["accuracy"]
            print(f"📊 准确率: {accuracy:.2%}")
        
        print(f"📁 查看完整报告: {Path(settings.MODEL_CACHE_DIR).parent / 'training_report.json'}")
        sys.exit(0)