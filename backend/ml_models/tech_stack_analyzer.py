"""
技术栈分析器
识别和分析项目中使用的技术栈
"""

import logging
import pickle
import re
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from collections import Counter
import requests
from config import settings

logger = logging.getLogger(__name__)


class TechStackAnalyzer:
    """技术栈分析器"""
    
    def __init__(self):
        self.tech_definitions = {}
        self.tech_categories = {}
        self.tech_aliases = {}
        self.popularity_scores = {}
        self.version = "1.0.0"
        self.model_path = Path(settings.MODEL_CACHE_DIR) / "tech_analyzer.pkl"
        self.definitions_path = Path(settings.MODEL_CACHE_DIR) / "tech_definitions.json"
        
    async def load_model(self):
        """加载模型"""
        try:
            # 先加载技术定义
            await self._load_tech_definitions()
            
            # 尝试加载缓存的模型
            if self.model_path.exists():
                logger.info(f"从缓存加载技术栈分析器: {self.model_path}")
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectorizer = data.get('vectorizer', None)
                    self.clustering_model = data.get('clustering_model', None)
                
                logger.info("技术栈分析器加载完成")
                return True
            else:
                logger.info("未找到缓存的技术栈分析器，将创建新模型")
                self._create_model()
                return True
                
        except Exception as e:
            logger.error(f"加载技术栈分析器失败: {e}")
            logger.info("创建基础技术栈分析器...")
            self._create_model()
            return True
    
    async def _load_tech_definitions(self):
        """加载技术栈定义"""
        try:
            # 从配置文件加载技术栈定义
            self.tech_definitions = {}
            self.tech_categories = {}
            self.tech_aliases = {}
            self.popularity_scores = {}
            
            # 从TECH_STACKS配置加载
            for category, tech_list in settings.TECH_STACKS.items():
                for tech in tech_list:
                    tech_lower = tech.lower()
                    self.tech_definitions[tech_lower] = {
                        'name': tech,
                        'category': category,
                        'aliases': self._get_tech_aliases(tech)
                    }
                    self.tech_categories[tech_lower] = category
            
            # 从数据库加载额外的技术栈定义
            try:
                from ..database import TechStackDefinition
                from sqlalchemy.ext.asyncio import AsyncSession
                from sqlalchemy import select
                
                # 这里需要数据库会话，暂时注释，实际使用时需要传入
                # async with AsyncSession() as session:
                #     result = await session.execute(select(TechStackDefinition))
                #     tech_records = result.scalars().all()
                    
                #     for tech in tech_records:
                #         tech_name = tech.name.lower()
                #         self.tech_definitions[tech_name] = {
                #             'name': tech.name,
                #             'category': tech.category,
                #             'aliases': tech.aliases or []
                #         }
                #         self.tech_categories[tech_name] = tech.category
                #         if tech.popularity_score:
                #             self.popularity_scores[tech_name] = tech.popularity_score
                pass
                
            except Exception as db_error:
                logger.warning(f"从数据库加载技术定义失败: {db_error}")
            
            # 创建别名映射
            self._build_alias_mapping()
            
            logger.info(f"加载了 {len(self.tech_definitions)} 个技术栈定义")
            
        except Exception as e:
            logger.error(f"加载技术栈定义失败: {e}")
            # 创建基础定义
            self._create_basic_definitions()
    
    def _get_tech_aliases(self, tech_name: str) -> List[str]:
        """获取技术别名"""
        aliases = []
        tech_lower = tech_name.lower()
        
        # 常见技术的别名映射
        common_aliases = {
            "javascript": ["js", "ecmascript"],
            "python": ["py"],
            "c++": ["cpp"],
            "c#": ["csharp"],
            "go": ["golang"],
            "react": ["reactjs"],
            "vue": ["vuejs"],
            "angular": ["angularjs"],
            "postgresql": ["postgres"],
            "elasticsearch": ["es"],
            "google_cloud": ["gcp"],
            "kubernetes": ["k8s"]
        }
        
        if tech_lower in common_aliases:
            aliases.extend(common_aliases[tech_lower])
        
        return aliases
    
    def _build_alias_mapping(self):
        """构建别名映射"""
        self.tech_aliases = {}
        for tech_name, tech_info in self.tech_definitions.items():
            # 主名称映射
            self.tech_aliases[tech_name] = tech_name
            
            # 别名映射
            for alias in tech_info.get('aliases', []):
                alias_lower = alias.lower()
                self.tech_aliases[alias_lower] = tech_name
            
            # 添加简写映射（如 "react" -> "reactjs"）
            if ' ' in tech_info['name']:
                # 对于多词技术名，创建首字母缩写
                words = tech_info['name'].split()
                if len(words) > 1:
                    acronym = ''.join(word[0].lower() for word in words)
                    self.tech_aliases[acronym] = tech_name
    
    def _create_basic_definitions(self):
        """创建基础技术定义"""
        logger.info("创建基础技术栈定义...")
        
        # 基础技术栈定义
        basic_tech = {
            # 编程语言
            "python": {"category": "language", "aliases": ["py"]},
            "javascript": {"category": "language", "aliases": ["js", "ecmascript"]},
            "java": {"category": "language", "aliases": []},
            "c++": {"category": "language", "aliases": ["cpp"]},
            "c#": {"category": "language", "aliases": ["csharp"]},
            "go": {"category": "language", "aliases": ["golang"]},
            "rust": {"category": "language", "aliases": []},
            "ruby": {"category": "language", "aliases": []},
            "php": {"category": "language", "aliases": []},
            "swift": {"category": "language", "aliases": []},
            
            # Web框架
            "django": {"category": "framework", "aliases": []},
            "flask": {"category": "framework", "aliases": []},
            "fastapi": {"category": "framework", "aliases": []},
            "express": {"category": "framework", "aliases": ["expressjs"]},
            "react": {"category": "framework", "aliases": ["reactjs"]},
            "vue": {"category": "framework", "aliases": ["vuejs"]},
            "angular": {"category": "framework", "aliases": ["angularjs"]},
            "spring": {"category": "framework", "aliases": ["spring boot"]},
            "laravel": {"category": "framework", "aliases": []},
            
            # 数据库
            "postgresql": {"category": "database", "aliases": ["postgres"]},
            "mysql": {"category": "database", "aliases": []},
            "mongodb": {"category": "database", "aliases": ["mongo"]},
            "redis": {"category": "database", "aliases": []},
            "elasticsearch": {"category": "database", "aliases": ["es"]},
            "cassandra": {"category": "database", "aliases": []},
            
            # 云平台
            "aws": {"category": "cloud", "aliases": ["amazon web services"]},
            "azure": {"category": "cloud", "aliases": ["microsoft azure"]},
            "google_cloud": {"category": "cloud", "aliases": ["gcp"]},
            "aliyun": {"category": "cloud", "aliases": ["alibaba cloud"]},
            "heroku": {"category": "cloud", "aliases": []},
            
            # 工具
            "docker": {"category": "tool", "aliases": []},
            "kubernetes": {"category": "tool", "aliases": ["k8s"]},
            "git": {"category": "tool", "aliases": ["github", "gitlab"]},
            "jenkins": {"category": "tool", "aliases": []},
            "terraform": {"category": "tool", "aliases": []},
        }
        
        for tech_name, tech_info in basic_tech.items():
            self.tech_definitions[tech_name] = {
                'name': tech_name,
                'category': tech_info['category'],
                'aliases': tech_info['aliases']
            }
            self.tech_categories[tech_name] = tech_info['category']
        
        self._build_alias_mapping()
        logger.info(f"创建了 {len(self.tech_definitions)} 个基础技术定义")
    
    def _create_model(self):
        """创建模型"""
        try:
            logger.info("创建技术栈分析模型...")
            
            # 创建向量器（用于相似度匹配）
            all_tech_names = list(self.tech_definitions.keys())
            all_tech_texts = []
            
            for tech_name in all_tech_names:
                tech_info = self.tech_definitions[tech_name]
                # 创建技术描述文本
                text_parts = [tech_name]
                text_parts.extend(tech_info.get('aliases', []))
                text_parts.append(tech_info.get('category', ''))
                all_tech_texts.append(" ".join(text_parts))
            
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=1.0
            )
            
            # 训练向量器
            tfidf_matrix = self.vectorizer.fit_transform(all_tech_texts)
            
            # 创建聚类模型（用于识别相关技术）
            self.clustering_model = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
            self.clustering_model.fit(tfidf_matrix.toarray())
            
            # 保存模型
            self._save_model()
            
            logger.info("技术栈分析模型创建完成")
            
        except Exception as e:
            logger.error(f"创建技术栈分析模型失败: {e}")
            self.vectorizer = None
            self.clustering_model = None
    
    def _save_model(self):
        """保存模型"""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'vectorizer': self.vectorizer,
                'clustering_model': self.clustering_model,
                'tech_definitions': self.tech_definitions,
                'tech_categories': self.tech_categories,
                'tech_aliases': self.tech_aliases
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"技术栈分析器保存到: {self.model_path}")
            
        except Exception as e:
            logger.error(f"保存技术栈分析器失败: {e}")
    
    async def analyze_tech_stack(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析技术栈"""
        try:
            if not self.tech_definitions:
                await self.load_model()
            
            # 提取技术栈信息
            detected_tech = self._detect_technologies(project_data)
            
            # 分析技术栈特征
            analysis = self._analyze_tech_features(detected_tech)
            
            # 获取技术栈详情
            tech_details = self._get_tech_details(detected_tech)
            
            # 计算总体置信度
            confidence = self._calculate_confidence(detected_tech, project_data)
            
            # 生成建议
            recommendations = self._generate_tech_recommendations(detected_tech, analysis)
            
            return {
                "detected_tech": detected_tech,
                "tech_details": tech_details,
                "analysis": analysis,
                "confidence": confidence,
                "recommendations": recommendations,
                "tech_categories": self._categorize_technologies(detected_tech)
            }
            
        except Exception as e:
            logger.error(f"分析技术栈失败: {e}")
            return {
                "detected_tech": [],
                "analysis": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _detect_technologies(self, project_data: Dict[str, Any]) -> List[str]:
        """检测技术栈"""
        detected = set()
        
        # 1. 从tech_stack字段直接获取
        if project_data.get("tech_stack"):
            tech_stack = project_data["tech_stack"]
            if isinstance(tech_stack, list):
                for tech in tech_stack:
                    if isinstance(tech, str):
                        normalized = self._normalize_tech_name(tech)
                        if normalized:
                            detected.add(normalized)
        
        # 2. 从项目描述中提取
        if project_data.get("description"):
            description = project_data["description"].lower()
            detected.update(self._extract_from_text(description))
        
        # 3. 从项目名称中提取
        if project_data.get("name"):
            name = project_data["name"].lower()
            detected.update(self._extract_from_text(name))
        
        # 4. 从元数据中提取
        if project_data.get("metadata"):
            metadata = project_data["metadata"]
            if isinstance(metadata, dict):
                for value in metadata.values():
                    if isinstance(value, str):
                        detected.update(self._extract_from_text(value.lower()))
        
        # 转换为列表并排序
        detected_list = list(detected)
        detected_list.sort()
        
        return detected_list
    
    def _normalize_tech_name(self, tech_name: str) -> Optional[str]:
        """标准化技术名称"""
        if not tech_name or not isinstance(tech_name, str):
            return None
        
        tech_lower = tech_name.strip().lower()
        
        # 1. 直接匹配
        if tech_lower in self.tech_definitions:
            return tech_lower
        
        # 2. 别名匹配
        if tech_lower in self.tech_aliases:
            return self.tech_aliases[tech_lower]
        
        # 3. 模糊匹配（移除版本号等）
        clean_name = self._clean_tech_name(tech_lower)
        if clean_name and clean_name in self.tech_definitions:
            return clean_name
        
        # 4. 部分匹配
        for defined_tech in self.tech_definitions.keys():
            if defined_tech in tech_lower or tech_lower in defined_tech:
                return defined_tech
        
        return None
    
    def _clean_tech_name(self, tech_name: str) -> str:
        """清理技术名称"""
        # 移除版本号（如 "python3.8" -> "python"）
        clean_name = re.sub(r'[\d\.]+', '', tech_name)
        
        # 移除特殊字符
        clean_name = re.sub(r'[^\w\s]', '', clean_name)
        
        # 移除多余空格
        clean_name = ' '.join(clean_name.split())
        
        return clean_name.strip()
    
    def _extract_from_text(self, text: str) -> Set[str]:
        """从文本中提取技术栈"""
        detected = set()
        
        if not text:
            return detected
        
        # 将文本拆分为单词
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 检查每个单词和双词组合
        for i in range(len(words)):
            # 单词检查
            single_word = words[i]
            normalized = self._normalize_tech_name(single_word)
            if normalized:
                detected.add(normalized)
            
            # 双词检查（如 "react native"）
            if i < len(words) - 1:
                double_word = f"{words[i]} {words[i+1]}"
                normalized = self._normalize_tech_name(double_word)
                if normalized:
                    detected.add(normalized)
        
        return detected
    
    def _analyze_tech_features(self, detected_tech: List[str]) -> Dict[str, Any]:
        """分析技术栈特征"""
        if not detected_tech:
            return {
                "diversity": 0.0,
                "maturity": 0.0,
                "complexity": 0.0,
                "cohesion": 0.0
            }
        
        # 技术多样性
        categories = []
        for tech in detected_tech:
            category = self.tech_categories.get(tech, "unknown")
            categories.append(category)
        
        unique_categories = set(categories)
        diversity = len(unique_categories) / max(len(self.tech_categories), 1)
        
        # 技术成熟度（基于流行度评分）
        maturity_scores = []
        for tech in detected_tech:
            score = self.popularity_scores.get(tech, 0.5)
            maturity_scores.append(score)
        
        maturity = np.mean(maturity_scores) if maturity_scores else 0.5
        
        # 技术复杂度（技术数量）
        complexity = min(len(detected_tech) / 10, 1.0)  # 最多10项技术
        
        # 技术内聚性（相关技术的比例）
        cohesion = self._calculate_cohesion(detected_tech)
        
        return {
            "diversity": float(diversity),
            "maturity": float(maturity),
            "complexity": float(complexity),
            "cohesion": float(cohesion),
            "category_distribution": dict(Counter(categories))
        }
    
    def _calculate_cohesion(self, detected_tech: List[str]) -> float:
        """计算技术内聚性"""
        if len(detected_tech) <= 1:
            return 1.0
        
        try:
            if self.vectorizer is None or self.clustering_model is None:
                return 0.5
            
            # 获取技术向量
            tech_vectors = []
            for tech in detected_tech:
                tech_info = self.tech_definitions.get(tech, {})
                text = f"{tech} {' '.join(tech_info.get('aliases', []))} {tech_info.get('category', '')}"
                vector = self.vectorizer.transform([text])
                tech_vectors.append(vector.toarray()[0])
            
            # 计算平均余弦相似度
            from sklearn.metrics.pairwise import cosine_similarity
            
            total_similarity = 0
            pair_count = 0
            
            for i in range(len(tech_vectors)):
                for j in range(i + 1, len(tech_vectors)):
                    similarity = cosine_similarity(
                        [tech_vectors[i]], 
                        [tech_vectors[j]]
                    )[0][0]
                    total_similarity += similarity
                    pair_count += 1
            
            return total_similarity / max(pair_count, 1)
            
        except Exception as e:
            logger.debug(f"计算内聚性失败: {e}")
            return 0.5
    
    def _get_tech_details(self, detected_tech: List[str]) -> List[Dict[str, Any]]:
        """获取技术详情"""
        details = []
        
        for tech in detected_tech:
            tech_info = self.tech_definitions.get(tech, {})
            category = self.tech_categories.get(tech, "unknown")
            popularity = self.popularity_scores.get(tech, 0.5)
            
            details.append({
                "name": tech_info.get("name", tech),
                "normalized_name": tech,
                "category": category,
                "popularity_score": popularity,
                "aliases": tech_info.get("aliases", []),
                "is_outdated": self._is_outdated_tech(tech)
            })
        
        # 按流行度排序
        details.sort(key=lambda x: x["popularity_score"], reverse=True)
        
        return details
    
    def _is_outdated_tech(self, tech_name: str) -> bool:
        """判断是否是过时技术"""
        outdated_tech = [
            "jquery", "backbone", "ember", "knockout",  # 旧JS框架
            "php5", "python2", "ruby1.8",  # 旧版本语言
            "mysql4", "mongodb2",  # 旧数据库版本
            "flash", "silverlight",  # 淘汰技术
        ]
        
        return tech_name in outdated_tech
    
    def _calculate_confidence(self, detected_tech: List[str], project_data: Dict[str, Any]) -> float:
        """计算置信度"""
        confidence = 0.0
        
        # 1. 基于明确指定的技术栈
        if project_data.get("tech_stack"):
            explicit_tech = project_data["tech_stack"]
            if isinstance(explicit_tech, list) and explicit_tech:
                # 如果有明确指定的技术栈，置信度较高
                confidence += 0.4
        
        # 2. 基于检测到的技术数量
        tech_count = len(detected_tech)
        if tech_count > 0:
            confidence += min(tech_count * 0.1, 0.3)  # 最多+0.3
        
        # 3. 基于项目描述的详细程度
        if project_data.get("description"):
            description = project_data["description"]
            if len(description) > 100:  # 详细描述
                confidence += 0.2
        
        # 4. 基于技术名称的标准化程度
        normalized_count = sum(1 for tech in detected_tech if tech in self.tech_definitions)
        if detected_tech:
            confidence += (normalized_count / len(detected_tech)) * 0.1
        
        return min(confidence, 1.0)
    
    def _categorize_technologies(self, detected_tech: List[str]) -> Dict[str, List[str]]:
        """按类别分组技术"""
        categories = {}
        
        for tech in detected_tech:
            category = self.tech_categories.get(tech, "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(tech)
        
        return categories
    
    def _generate_tech_recommendations(self, detected_tech: List[str], analysis: Dict[str, Any]) -> List[str]:
        """生成技术栈建议"""
        recommendations = []
        
        # 检查技术栈完整性
        categories = self._categorize_technologies(detected_tech)
        
        # 1. 缺少关键技术类别的建议
        essential_categories = ["language", "framework", "database"]
        for category in essential_categories:
            if category not in categories:
                if category == "language":
                    recommendations.append("建议指定主要编程语言（如Python、JavaScript等）")
                elif category == "framework":
                    recommendations.append("建议使用合适的框架以提高开发效率")
                elif category == "database":
                    recommendations.append("建议选择合适的数据库系统")
        
        # 2. 技术栈多样性建议
        diversity = analysis.get("diversity", 0.0)
        if diversity < 0.3:
            recommendations.append("技术栈过于单一，考虑引入互补技术")
        elif diversity > 0.8:
            recommendations.append("技术栈过于复杂，考虑简化架构")
        
        # 3. 过时技术建议
        outdated_tech = [tech for tech in detected_tech if self._is_outdated_tech(tech)]
        if outdated_tech:
            recommendations.append(f"发现过时技术: {', '.join(outdated_tech)}，建议升级或替换")
        
        # 4. 技术内聚性建议
        cohesion = analysis.get("cohesion", 0.5)
        if cohesion < 0.3:
            recommendations.append("技术栈内聚性较低，考虑选择更兼容的技术组合")
        
        # 5. 通用建议
        if len(recommendations) < 3:
            additional = [
                "考虑添加自动化测试框架",
                "建议实施CI/CD流程",
                "考虑添加监控和日志系统",
                "建议使用容器化技术（如Docker）"
            ]
            recommendations.extend(additional[:3 - len(recommendations)])
        
        return recommendations[:5]  # 最多5条建议
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "version": self.version,
            "tech_count": len(self.tech_definitions),
            "category_count": len(set(self.tech_categories.values())),
            "model_type": "Tech Stack Analyzer",
            "is_loaded": bool(self.tech_definitions)
        }