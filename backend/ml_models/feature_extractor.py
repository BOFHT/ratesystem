"""
特征提取器
从项目数据中提取量化特征
"""

import logging
import re
import math
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from config import settings

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.model_path = Path(settings.MODEL_CACHE_DIR) / "feature_extractor.pkl"
        
        # NLP工具初始化
        self.stop_words = set()
        self.lemmatizer = None
        
        # 统计模型
        self.vectorizer = None
        self.lda_model = None
        self.feature_names = []
        
        # 关键词词典
        self.quality_keywords = {
            "code": ["clean", "maintainable", "readable", "modular", "tested"],
            "architecture": ["scalable", "microservices", "modular", "decoupled", "layered"],
            "documentation": ["documented", "api docs", "readme", "comments", "tutorial"],
            "testing": ["unit test", "integration test", "coverage", "tdd", "bdd"],
            "security": ["secure", "encrypted", "authentication", "authorization", "ssl"]
        }
        
        self.innovation_keywords = {
            "novelty": ["innovative", "novel", "unique", "groundbreaking", "original"],
            "complexity": ["complex", "sophisticated", "advanced", "cutting-edge", "state-of-art"],
            "automation": ["automated", "ai", "machine learning", "intelligent", "smart"]
        }
        
        self.business_keywords = {
            "market": ["market", "business", "commercial", "revenue", "profit"],
            "user": ["user", "customer", "audience", "demand", "need"],
            "scale": ["scalable", "growth", "expansion", "large-scale", "enterprise"]
        }
        
    async def load_model(self):
        """加载模型"""
        try:
            if self.model_path.exists():
                logger.info(f"从缓存加载特征提取器: {self.model_path}")
                import pickle
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectorizer = data.get('vectorizer', None)
                    self.lda_model = data.get('lda_model', None)
                    self.feature_names = data.get('feature_names', [])
                
                logger.info("特征提取器加载完成")
            
            # 初始化NLP工具
            self._init_nlp_tools()
            
            return True
            
        except Exception as e:
            logger.error(f"加载特征提取器失败: {e}")
            logger.info("创建基础特征提取器...")
            self._create_model()
            return True
    
    def _init_nlp_tools(self):
        """初始化NLP工具"""
        try:
            # 下载NLTK数据
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet', quiet=True)
            
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            
        except Exception as e:
            logger.warning(f"NLP工具初始化失败: {e}")
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            self.lemmatizer = None
    
    def _create_model(self):
        """创建模型"""
        try:
            logger.info("创建特征提取模型...")
            
            # 创建向量器
            self.vectorizer = CountVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            # 创建LDA主题模型
            self.lda_model = LatentDirichletAllocation(
                n_components=10,
                random_state=42,
                max_iter=10,
                learning_method='online'
            )
            
            # 初始化NLP工具
            self._init_nlp_tools()
            
            logger.info("特征提取模型创建完成")
            
        except Exception as e:
            logger.error(f"创建特征提取模型失败: {e}")
            self.vectorizer = None
            self.lda_model = None
    
    async def extract_features(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取特征"""
        try:
            features = {}
            
            # 提取文本特征
            text_features = self._extract_text_features(project_data)
            features.update(text_features)
            
            # 提取技术特征
            tech_features = self._extract_tech_features(project_data)
            features.update(tech_features)
            
            # 提取元数据特征
            metadata_features = self._extract_metadata_features(project_data)
            features.update(metadata_features)
            
            # 提取关键词特征
            keyword_features = self._extract_keyword_features(project_data)
            features.update(keyword_features)
            
            # 提取复杂度特征
            complexity_features = self._extract_complexity_features(project_data, features)
            features.update(complexity_features)
            
            # 添加衍生特征
            derived_features = self._calculate_derived_features(features)
            features.update(derived_features)
            
            # 确保所有特征都是可序列化的
            features = self._make_serializable(features)
            
            logger.debug(f"提取了 {len(features)} 个特征")
            
            return features
            
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return {
                "feature_extraction_error": str(e),
                "text_length": 0,
                "tech_count": 0
            }
    
    def _extract_text_features(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取文本特征"""
        features = {}
        
        # 获取所有文本
        text_parts = []
        
        if project_data.get("name"):
            text_parts.append(project_data["name"])
        
        if project_data.get("description"):
            text_parts.append(project_data["description"])
        
        if project_data.get("metadata"):
            metadata = project_data["metadata"]
            if isinstance(metadata, dict):
                for value in metadata.values():
                    if isinstance(value, str):
                        text_parts.append(value)
        
        # 合并所有文本
        full_text = " ".join(text_parts)
        
        # 基础文本特征
        features["text_length"] = len(full_text)
        features["word_count"] = len(full_text.split())
        features["sentence_count"] = len(re.split(r'[.!?]+', full_text))
        
        # 词汇特征
        words = full_text.lower().split()
        unique_words = set(words)
        features["vocabulary_size"] = len(unique_words)
        
        if words:
            features["lexical_diversity"] = len(unique_words) / len(words)
            features["avg_word_length"] = np.mean([len(word) for word in words])
        else:
            features["lexical_diversity"] = 0.0
            features["avg_word_length"] = 0.0
        
        # 可读性特征（简化版Flesch-Kincaid）
        if features["sentence_count"] > 0 and features["word_count"] > 0:
            features["readability_score"] = 206.835 - 1.015 * (features["word_count"] / features["sentence_count"]) - 84.6 * (features["avg_word_length"] if features["avg_word_length"] else 5)
        else:
            features["readability_score"] = 0.0
        
        # 主题特征（如果有足够的文本）
        if len(full_text) > 100 and self.vectorizer and self.lda_model:
            try:
                # 向量化文本
                X = self.vectorizer.fit_transform([full_text])
                feature_names = self.vectorizer.get_feature_names_out()
                self.feature_names = list(feature_names)
                
                # 应用LDA
                topic_distribution = self.lda_model.fit_transform(X)
                
                # 添加主题特征
                for i in range(min(5, topic_distribution.shape[1])):
                    features[f"topic_{i}_weight"] = float(topic_distribution[0, i])
                
                # 获取主要主题
                main_topic = np.argmax(topic_distribution[0])
                features["main_topic"] = int(main_topic)
                features["topic_entropy"] = float(self._calculate_entropy(topic_distribution[0]))
                
            except Exception as e:
                logger.debug(f"主题提取失败: {e}")
        
        return features
    
    def _extract_tech_features(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取技术特征"""
        features = {}
        
        # 技术栈特征
        tech_stack = project_data.get("tech_stack", [])
        if isinstance(tech_stack, list):
            features["tech_count"] = len(tech_stack)
            features["tech_diversity"] = min(len(set(tech_stack)) / max(len(tech_stack), 1), 1.0)
            
            # 技术类别分布
            tech_categories = self._categorize_technologies(tech_stack)
            features["tech_category_count"] = len(tech_categories)
            
            # 热门技术检测
            popular_tech = ["python", "javascript", "react", "docker", "postgresql"]
            popular_count = sum(1 for tech in tech_stack if isinstance(tech, str) and tech.lower() in popular_tech)
            features["popular_tech_ratio"] = popular_count / max(len(tech_stack), 1)
            
        else:
            features["tech_count"] = 0
            features["tech_diversity"] = 0.0
            features["tech_category_count"] = 0
            features["popular_tech_ratio"] = 0.0
        
        return features
    
    def _categorize_technologies(self, tech_stack: List[str]) -> Dict[str, List[str]]:
        """按类别分组技术"""
        categories = {}
        
        # 简单的类别映射（实际应用中应该更详细）
        category_map = {
            "language": ["python", "javascript", "java", "c++", "c#", "go", "rust", "ruby", "php", "swift"],
            "framework": ["django", "flask", "fastapi", "express", "react", "vue", "angular", "spring", "laravel"],
            "database": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra"],
            "cloud": ["aws", "azure", "google_cloud", "aliyun", "heroku"],
            "tool": ["docker", "kubernetes", "git", "jenkins", "terraform"]
        }
        
        for tech in tech_stack:
            if not isinstance(tech, str):
                continue
                
            tech_lower = tech.lower()
            assigned = False
            
            for category, techs in category_map.items():
                if tech_lower in techs:
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(tech)
                    assigned = True
                    break
            
            if not assigned:
                if "other" not in categories:
                    categories["other"] = []
                categories["other"].append(tech)
        
        return categories
    
    def _extract_metadata_features(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取元数据特征"""
        features = {}
        
        metadata = project_data.get("metadata", {})
        if not isinstance(metadata, dict):
            return features
        
        # 元数据大小特征
        features["metadata_field_count"] = len(metadata)
        
        # 元数据内容特征
        text_values = []
        numeric_values = []
        
        for key, value in metadata.items():
            if isinstance(value, str):
                text_values.append(value)
            elif isinstance(value, (int, float)):
                numeric_values.append(float(value))
            elif isinstance(value, bool):
                numeric_values.append(1.0 if value else 0.0)
            elif isinstance(value, list):
                features[f"metadata_list_{key}_count"] = len(value)
        
        features["metadata_text_length"] = sum(len(str(v)) for v in text_values)
        features["metadata_numeric_count"] = len(numeric_values)
        
        if numeric_values:
            features["metadata_numeric_mean"] = float(np.mean(numeric_values))
            features["metadata_numeric_std"] = float(np.std(numeric_values))
        
        return features
    
    def _extract_keyword_features(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键词特征"""
        features = {}
        
        # 获取所有文本
        text = ""
        if project_data.get("name"):
            text += " " + project_data["name"]
        if project_data.get("description"):
            text += " " + project_data["description"]
        
        text = text.lower()
        
        # 质量关键词
        quality_scores = {}
        for category, keywords in self.quality_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text)
            quality_scores[category] = count / max(len(keywords), 1)
        
        features["quality_score_code"] = quality_scores.get("code", 0.0)
        features["quality_score_architecture"] = quality_scores.get("architecture", 0.0)
        features["quality_score_documentation"] = quality_scores.get("documentation", 0.0)
        features["quality_score_testing"] = quality_scores.get("testing", 0.0)
        features["quality_score_security"] = quality_scores.get("security", 0.0)
        features["overall_quality_score"] = np.mean(list(quality_scores.values())) if quality_scores else 0.0
        
        # 创新关键词
        innovation_scores = {}
        for category, keywords in self.innovation_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text)
            innovation_scores[category] = count / max(len(keywords), 1)
        
        features["innovation_score_novelty"] = innovation_scores.get("novelty", 0.0)
        features["innovation_score_complexity"] = innovation_scores.get("complexity", 0.0)
        features["innovation_score_automation"] = innovation_scores.get("automation", 0.0)
        features["overall_innovation_score"] = np.mean(list(innovation_scores.values())) if innovation_scores else 0.0
        
        # 商业关键词
        business_scores = {}
        for category, keywords in self.business_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text)
            business_scores[category] = count / max(len(keywords), 1)
        
        features["business_score_market"] = business_scores.get("market", 0.0)
        features["business_score_user"] = business_scores.get("user", 0.0)
        features["business_score_scale"] = business_scores.get("scale", 0.0)
        features["overall_business_score"] = np.mean(list(business_scores.values())) if business_scores else 0.0
        
        return features
    
    def _extract_complexity_features(self, project_data: Dict[str, Any], existing_features: Dict[str, Any]) -> Dict[str, Any]:
        """提取复杂度特征"""
        features = {}
        
        # 基于技术栈的复杂度
        tech_count = existing_features.get("tech_count", 0)
        tech_category_count = existing_features.get("tech_category_count", 0)
        
        features["tech_complexity"] = min((tech_count * 0.2 + tech_category_count * 0.3), 1.0)
        
        # 基于文本的复杂度
        text_length = existing_features.get("text_length", 0)
        word_count = existing_features.get("word_count", 0)
        
        features["text_complexity"] = min((text_length / 10000 + word_count / 500) / 2, 1.0)
        
        # 基于元数据的复杂度
        metadata_count = existing_features.get("metadata_field_count", 0)
        features["metadata_complexity"] = min(metadata_count / 20, 1.0)
        
        # 综合复杂度
        complexities = [
            features.get("tech_complexity", 0.0),
            features.get("text_complexity", 0.0),
            features.get("metadata_complexity", 0.0)
        ]
        features["overall_complexity"] = float(np.mean(complexities))
        
        # 项目规模估计
        project_size = 0
        if tech_count > 10:
            project_size = 3  # 大型项目
        elif tech_count > 5:
            project_size = 2  # 中型项目
        elif tech_count > 0:
            project_size = 1  # 小型项目
        
        features["project_size"] = project_size
        
        return features
    
    def _calculate_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """计算衍生特征"""
        derived = {}
        
        # 项目成熟度评分
        quality_score = features.get("overall_quality_score", 0.0)
        tech_maturity = features.get("popular_tech_ratio", 0.0)
        derived["maturity_score"] = (quality_score + tech_maturity) / 2
        
        # 风险评估
        complexity = features.get("overall_complexity", 0.5)
        quality = features.get("overall_quality_score", 0.5)
        risk = complexity * (1 - quality)
        derived["risk_score"] = risk
        
        # 可行性评分
        tech_count = features.get("tech_count", 0)
        tech_diversity = features.get("tech_diversity", 0.0)
        
        # 技术栈越标准化，可行性越高
        standardization = features.get("popular_tech_ratio", 0.0)
        derived["feasibility_score"] = (standardization + (1 - tech_diversity)) / 2
        
        # 维护性评分
        documentation = features.get("quality_score_documentation", 0.0)
        code_quality = features.get("quality_score_code", 0.0)
        derived["maintainability_score"] = (documentation + code_quality) / 2
        
        # 创新潜力评分
        innovation = features.get("overall_innovation_score", 0.0)
        novelty = features.get("innovation_score_novelty", 0.0)
        derived["innovation_potential"] = (innovation + novelty) / 2
        
        return derived
    
    def _calculate_entropy(self, distribution: np.ndarray) -> float:
        """计算熵"""
        # 移除零值避免log(0)
        distribution = distribution[distribution > 0]
        if len(distribution) == 0:
            return 0.0
        return -np.sum(distribution * np.log2(distribution))
    
    def _make_serializable(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """确保特征可序列化"""
        serializable = {}
        
        for key, value in features.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                serializable[key] = value
            elif isinstance(value, (np.integer, np.floating)):
                serializable[key] = float(value)
            elif isinstance(value, np.ndarray):
                serializable[key] = value.tolist()
            else:
                try:
                    # 尝试转换为字符串
                    serializable[key] = str(value)
                except:
                    # 如果无法转换，跳过
                    logger.debug(f"无法序列化特征 {key}: {type(value)}")
        
        return serializable
    
    async def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """训练特征提取模型"""
        try:
            logger.info("训练特征提取模型...")
            
            # 提取所有项目的文本
            texts = []
            for project in training_data:
                text_parts = []
                if project.get("name"):
                    text_parts.append(project["name"])
                if project.get("description"):
                    text_parts.append(project["description"])
                texts.append(" ".join(text_parts))
            
            # 过滤空文本
            texts = [text for text in texts if text.strip()]
            
            if len(texts) < 10:
                logger.warning("训练数据不足，跳过训练")
                return {"error": "训练数据不足"}
            
            # 训练向量器
            self.vectorizer = CountVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.9
            )
            
            X = self.vectorizer.fit_transform(texts)
            self.feature_names = self.vectorizer.get_feature_names_out().tolist()
            
            # 训练LDA模型
            self.lda_model = LatentDirichletAllocation(
                n_components=min(20, len(texts) // 5),
                random_state=42,
                max_iter=20,
                learning_method='online',
                learning_offset=50.
            )
            
            self.lda_model.fit(X)
            
            # 计算模型质量指标
            perplexity = self.lda_model.perplexity(X)
            log_likelihood = self.lda_model.score(X)
            
            # 保存模型
            self._save_model()
            
            return {
                "perplexity": float(perplexity),
                "log_likelihood": float(log_likelihood),
                "feature_count": len(self.feature_names),
                "topic_count": self.lda_model.n_components,
                "training_samples": len(texts)
            }
            
        except Exception as e:
            logger.error(f"训练特征提取模型失败: {e}")
            return {"error": str(e)}
    
    def _save_model(self):
        """保存模型"""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            import pickle
            model_data = {
                'vectorizer': self.vectorizer,
                'lda_model': self.lda_model,
                'feature_names': self.feature_names
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"特征提取器保存到: {self.model_path}")
            
        except Exception as e:
            logger.error(f"保存特征提取器失败: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "version": self.version,
            "feature_count": len(self.feature_names) if hasattr(self, 'feature_names') else 0,
            "topic_count": self.lda_model.n_components if self.lda_model else 0,
            "model_type": "Feature Extractor",
            "is_loaded": self.vectorizer is not None
        }