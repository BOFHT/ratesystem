"""
项目分类器
基于机器学习的项目类型分类
"""

import logging
import pickle
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from config import settings

logger = logging.getLogger(__name__)


class ProjectClassifier:
    """项目分类器"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.classes = []
        self.version = "1.0.0"
        self.model_path = Path(settings.MODEL_CACHE_DIR) / "project_classifier.pkl"
        self.metadata_path = Path(settings.MODEL_CACHE_DIR) / "classifier_metadata.json"
        
    async def load_model(self):
        """加载模型"""
        try:
            if self.model_path.exists():
                logger.info(f"从缓存加载分类器: {self.model_path}")
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.vectorizer = data['vectorizer']
                    self.label_encoder = data.get('label_encoder', None)
                    self.classes = data.get('classes', [])
                
                # 加载元数据
                if self.metadata_path.exists():
                    with open(self.metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        self.version = metadata.get('version', self.version)
                
                logger.info(f"分类器加载完成，支持 {len(self.classes)} 个类别")
                return True
                
            else:
                logger.warning("未找到缓存的分类器，将创建新模型")
                await self.train_model()
                return True
                
        except Exception as e:
            logger.error(f"加载分类器失败: {e}")
            logger.info("创建基础分类器...")
            self._create_basic_classifier()
            return True
    
    def _create_basic_classifier(self):
        """创建基础分类器"""
        logger.info("创建基础分类器...")
        
        # 定义类别
        self.classes = settings.PROJECT_CATEGORIES
        
        # 创建训练数据（基于关键词的简单分类）
        training_data = self._generate_training_data()
        
        # 创建向量器和分类器
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # 使用朴素贝叶斯作为基础分类器
        self.model = Pipeline([
            ('vectorizer', self.vectorizer),
            ('classifier', MultinomialNB())
        ])
        
        # 训练模型
        X = [item['text'] for item in training_data]
        y = [item['label'] for item in training_data]
        
        self.model.fit(X, y)
        
        # 保存模型
        self._save_model()
        
        logger.info(f"基础分类器创建完成，支持 {len(self.classes)} 个类别")
    
    def _generate_training_data(self):
        """生成训练数据"""
        training_data = []
        
        # 为每个类别生成示例文本
        category_keywords = {
            "web_development": [
                "web application", "website", "frontend", "backend", "api",
                "responsive design", "user interface", "browser", "server",
                "html", "css", "javascript", "react", "vue", "angular"
            ],
            "mobile_app": [
                "mobile application", "ios", "android", "flutter", "react native",
                "smartphone", "tablet", "app store", "google play", "mobile ui",
                "cross platform", "native app", "hybrid app"
            ],
            "data_science": [
                "data analysis", "data visualization", "statistics", "pandas",
                "numpy", "jupyter", "data cleaning", "exploratory analysis",
                "business intelligence", "dashboard", "reporting"
            ],
            "machine_learning": [
                "machine learning", "artificial intelligence", "neural network",
                "deep learning", "tensorflow", "pytorch", "model training",
                "prediction", "classification", "regression", "clustering"
            ],
            "iot": [
                "internet of things", "iot", "sensor", "smart device", "embedded",
                "arduino", "raspberry pi", "wireless", "bluetooth", "mqtt",
                "home automation", "smart home"
            ],
            "blockchain": [
                "blockchain", "cryptocurrency", "smart contract", "distributed ledger",
                "ethereum", "bitcoin", "web3", "defi", "nft", "dapp",
                "consensus algorithm", "mining"
            ],
            "game_development": [
                "game development", "video game", "unity", "unreal engine",
                "graphics", "3d modeling", "game engine", "game design",
                "virtual reality", "augmented reality", "game physics"
            ],
            "desktop_application": [
                "desktop application", "windows app", "mac app", "linux app",
                "electron", "qt", "java swing", "c# wpf", "native desktop",
                "standalone application"
            ],
            "embedded_systems": [
                "embedded system", "firmware", "microcontroller", "real-time",
                "embedded linux", "bare metal", "device driver", "hardware interface",
                "rtos", "embedded c", "assembly"
            ],
            "cloud_infrastructure": [
                "cloud infrastructure", "devops", "kubernetes", "docker",
                "microservices", "containerization", "cloud native", "ci/cd",
                "infrastructure as code", "terraform", "ansible"
            ]
        }
        
        # 为每个类别生成多个训练样本
        for category, keywords in category_keywords.items():
            # 每个关键词生成一个样本
            for keyword in keywords:
                training_data.append({
                    'text': f"This is a {keyword} project for {category}",
                    'label': category
                })
            
            # 组合关键词生成更多样本
            for i in range(len(keywords) - 1):
                combined_text = f"Project involving {keywords[i]} and {keywords[i+1]} for {category}"
                training_data.append({
                    'text': combined_text,
                    'label': category
                })
        
        return training_data
    
    async def train_model(self, training_data: Optional[List[Dict]] = None):
        """训练模型"""
        try:
            logger.info("开始训练项目分类器...")
            
            # 如果没有提供训练数据，使用生成的
            if training_data is None:
                training_data = self._generate_training_data()
            
            # 准备数据
            texts = [item['text'] for item in training_data]
            labels = [item['label'] for item in training_data]
            
            # 获取所有类别
            self.classes = list(set(labels))
            
            # 创建更复杂的模型
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.8
            )
            
            # 使用集成学习
            from sklearn.ensemble import VotingClassifier
            
            # 创建多个基础分类器
            nb_clf = MultinomialNB(alpha=0.1)
            rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
            svm_clf = SVC(probability=True, random_state=42, kernel='linear')
            
            voting_clf = VotingClassifier(
                estimators=[
                    ('nb', nb_clf),
                    ('rf', rf_clf),
                    ('svm', svm_clf)
                ],
                voting='soft'
            )
            
            self.model = Pipeline([
                ('vectorizer', self.vectorizer),
                ('classifier', voting_clf)
            ])
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # 训练模型
            self.model.fit(X_train, y_train)
            
            # 评估模型
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"模型训练完成，测试集准确率: {accuracy:.4f}")
            logger.debug(f"分类报告:\n{classification_report(y_test, y_pred)}")
            
            # 保存模型
            self._save_model()
            
            return {
                "accuracy": accuracy,
                "classes": self.classes,
                "training_samples": len(texts),
                "version": self.version
            }
            
        except Exception as e:
            logger.error(f"训练分类器失败: {e}")
            # 回退到基础分类器
            self._create_basic_classifier()
            return {"accuracy": 0.0, "error": str(e)}
    
    def _save_model(self):
        """保存模型"""
        try:
            # 确保目录存在
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存模型
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'classes': self.classes
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            # 保存元数据
            metadata = {
                'version': self.version,
                'classes': self.classes,
                'created_at': np.datetime64('now').astype(str),
                'model_type': str(type(self.model)),
                'feature_count': self.vectorizer.max_features if hasattr(self.vectorizer, 'max_features') else 'unknown'
            }
            
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"模型保存到: {self.model_path}")
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    async def predict(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测项目类别"""
        try:
            if self.model is None:
                await self.load_model()
            
            # 提取文本特征
            text_features = self._extract_text_features(project_data)
            
            # 预测类别
            if text_features.strip():
                predicted_class = self.model.predict([text_features])[0]
                probabilities = self.model.predict_proba([text_features])[0]
                
                # 创建概率字典
                class_probs = {}
                for i, class_name in enumerate(self.classes):
                    if i < len(probabilities):
                        class_probs[class_name] = float(probabilities[i])
                
                # 获取置信度
                confidence = float(max(probabilities)) if len(probabilities) > 0 else 0.0
                
                return {
                    "name": predicted_class,
                    "confidence": confidence,
                    "category_probabilities": class_probs,
                    "top_categories": sorted(
                        [(k, v) for k, v in class_probs.items()],
                        key=lambda x: x[1],
                        reverse=True
                    )[:3]
                }
            else:
                # 如果没有文本特征，返回未知
                return {
                    "name": "unknown",
                    "confidence": 0.0,
                    "category_probabilities": {"unknown": 1.0},
                    "top_categories": [("unknown", 1.0)]
                }
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return {
                "name": "unknown",
                "confidence": 0.0,
                "category_probabilities": {"unknown": 1.0},
                "top_categories": [("unknown", 1.0)],
                "error": str(e)
            }
    
    def _extract_text_features(self, project_data: Dict[str, Any]) -> str:
        """从项目数据中提取文本特征"""
        text_parts = []
        
        # 添加项目名称
        if project_data.get("name"):
            text_parts.append(project_data["name"])
        
        # 添加项目描述
        if project_data.get("description"):
            text_parts.append(project_data["description"])
        
        # 添加技术栈
        if project_data.get("tech_stack"):
            tech_stack = project_data["tech_stack"]
            if isinstance(tech_stack, list):
                text_parts.append(" ".join(tech_stack))
            else:
                text_parts.append(str(tech_stack))
        
        # 添加元数据中的关键词
        if project_data.get("metadata"):
            metadata = project_data["metadata"]
            if isinstance(metadata, dict):
                # 提取所有字符串值
                for value in metadata.values():
                    if isinstance(value, str):
                        text_parts.append(value)
        
        # 组合所有文本
        text = " ".join(text_parts)
        
        # 清理文本
        text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除特殊字符（保留字母、数字、空格）
        import re
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 移除多余空格
        text = ' '.join(text.split())
        
        return text
    
    async def evaluate(self, test_data: List[Dict]) -> Dict[str, Any]:
        """评估模型性能"""
        try:
            if self.model is None:
                await self.load_model()
            
            # 准备测试数据
            texts = [self._extract_text_features(item) for item in test_data]
            true_labels = [item.get('category', 'unknown') for item in test_data]
            
            # 过滤掉没有文本的数据
            filtered_texts = []
            filtered_labels = []
            for text, label in zip(texts, true_labels):
                if text.strip():
                    filtered_texts.append(text)
                    filtered_labels.append(label)
            
            if not filtered_texts:
                return {"error": "没有有效的测试数据"}
            
            # 预测
            predictions = self.model.predict(filtered_texts)
            
            # 计算指标
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, 
                f1_score, confusion_matrix
            )
            
            accuracy = accuracy_score(filtered_labels, predictions)
            precision = precision_score(filtered_labels, predictions, average='weighted', zero_division=0)
            recall = recall_score(filtered_labels, predictions, average='weighted', zero_division=0)
            f1 = f1_score(filtered_labels, predictions, average='weighted', zero_division=0)
            
            # 混淆矩阵
            cm = confusion_matrix(filtered_labels, predictions)
            
            return {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "confusion_matrix": cm.tolist(),
                "test_samples": len(filtered_texts),
                "predictions": list(predictions),
                "true_labels": filtered_labels
            }
            
        except Exception as e:
            logger.error(f"评估模型失败: {e}")
            return {"error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "version": self.version,
            "classes": self.classes,
            "class_count": len(self.classes),
            "model_type": str(type(self.model)) if self.model else "未加载",
            "model_path": str(self.model_path),
            "is_trained": self.model is not None
        }