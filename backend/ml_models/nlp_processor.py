"""
NLP处理器
自然语言处理功能
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from pathlib import Path
import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from collections import Counter
import warnings
from config import settings

logger = logging.getLogger(__name__)


class NLPProcessor:
    """NLP处理器"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.model_path = Path(settings.MODEL_CACHE_DIR) / "nlp_processor.pkl"
        
        # NLP工具
        self.stop_words = set()
        self.lemmatizer = None
        self.sentiment_lexicon = {}
        
        # 关键词词典
        self.keyword_categories = {
            "technology": [
                "software", "application", "system", "platform", "solution",
                "framework", "library", "tool", "api", "sdk", "interface",
                "database", "server", "client", "network", "protocol"
            ],
            "development": [
                "develop", "build", "create", "implement", "design",
                "code", "program", "script", "test", "debug", "deploy",
                "maintain", "update", "refactor", "optimize", "integrate"
            ],
            "business": [
                "business", "market", "product", "service", "customer",
                "user", "client", "revenue", "profit", "growth", "scale",
                "competitive", "strategy", "plan", "goal", "objective"
            ],
            "quality": [
                "quality", "reliable", "stable", "secure", "efficient",
                "performant", "scalable", "maintainable", "readable",
                "documented", "tested", "robust", "resilient", "fault-tolerant"
            ],
            "innovation": [
                "innovative", "novel", "unique", "advanced", "cutting-edge",
                "state-of-art", "revolutionary", "disruptive", "breakthrough",
                "creative", "original", "pioneering", "groundbreaking"
            ]
        }
        
        # 情感词典（简化版）
        self._init_sentiment_lexicon()
    
    async def load_model(self):
        """加载模型"""
        try:
            # 初始化NLP工具
            self._init_nlp_tools()
            
            logger.info("NLP处理器加载完成")
            return True
            
        except Exception as e:
            logger.error(f"加载NLP处理器失败: {e}")
            # 即使失败也返回True，使用基础功能
            return True
    
    def _init_nlp_tools(self):
        """初始化NLP工具"""
        try:
            # 下载NLTK数据
            nltk_packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
            
            for package in nltk_packages:
                try:
                    if package == 'punkt':
                        nltk.data.find('tokenizers/punkt')
                    elif package == 'stopwords':
                        nltk.data.find('corpora/stopwords')
                    elif package == 'wordnet':
                        nltk.data.find('corpora/wordnet')
                    elif package == 'averaged_perceptron_tagger':
                        nltk.data.find('taggers/averaged_perceptron_tagger')
                except LookupError:
                    logger.info(f"下载NLTK数据包: {package}")
                    nltk.download(package, quiet=True)
            
            # 初始化工具
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            
            logger.info("NLP工具初始化完成")
            
        except Exception as e:
            logger.warning(f"NLP工具初始化失败: {e}")
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            self.lemmatizer = None
    
    def _init_sentiment_lexicon(self):
        """初始化情感词典"""
        # 积极词汇
        positive_words = [
            "good", "great", "excellent", "awesome", "amazing",
            "best", "perfect", "wonderful", "outstanding", "superb",
            "innovative", "creative", "efficient", "reliable", "secure",
            "fast", "easy", "simple", "powerful", "flexible"
        ]
        
        # 消极词汇
        negative_words = [
            "bad", "poor", "terrible", "awful", "horrible",
            "worst", "slow", "difficult", "complex", "hard",
            "buggy", "unstable", "insecure", "outdated", "limited",
            "broken", "failed", "error", "issue", "problem"
        ]
        
        # 构建词典
        for word in positive_words:
            self.sentiment_lexicon[word] = 1.0
        
        for word in negative_words:
            self.sentiment_lexicon[word] = -1.0
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析文本"""
        try:
            if not text or not isinstance(text, str):
                return self._empty_analysis_result()
            
            text = text.strip()
            if not text:
                return self._empty_analysis_result()
            
            # 基础文本分析
            basic_analysis = self._analyze_basic_text(text)
            
            # 关键词提取
            keyword_analysis = self._extract_keywords(text)
            
            # 情感分析
            sentiment_analysis = self._analyze_sentiment(text)
            
            # 实体提取（简化版）
            entity_analysis = self._extract_entities(text)
            
            # 主题分析
            topic_analysis = self._analyze_topics(text)
            
            # 可读性分析
            readability_analysis = self._analyze_readability(text)
            
            # 合并所有分析结果
            analysis_result = {
                "basic": basic_analysis,
                "keywords": keyword_analysis,
                "sentiment": sentiment_analysis,
                "entities": entity_analysis,
                "topics": topic_analysis,
                "readability": readability_analysis,
                "summary": self._generate_summary(text),
                "metadata": {
                    "text_length": len(text),
                    "processing_time": "real-time",
                    "model_version": self.version
                }
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"文本分析失败: {e}")
            return {
                "error": str(e),
                "basic": {"word_count": 0, "sentence_count": 0},
                "keywords": {"categories": {}},
                "sentiment": {"score": 0.0, "label": "neutral"},
                "entities": {"count": 0, "list": []},
                "topics": {"count": 0, "list": []},
                "readability": {"score": 0.0, "level": "unknown"}
            }
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """空分析结果"""
        return {
            "basic": {"word_count": 0, "sentence_count": 0},
            "keywords": {"categories": {}},
            "sentiment": {"score": 0.0, "label": "neutral"},
            "entities": {"count": 0, "list": []},
            "topics": {"count": 0, "list": []},
            "readability": {"score": 0.0, "level": "unknown"},
            "summary": "",
            "metadata": {"text_length": 0, "processing_time": "instant", "model_version": self.version}
        }
    
    def _analyze_basic_text(self, text: str) -> Dict[str, Any]:
        """基础文本分析"""
        try:
            # 句子分割
            sentences = sent_tokenize(text)
            
            # 单词分割
            words = word_tokenize(text.lower())
            
            # 移除标点和停用词
            filtered_words = []
            for word in words:
                if word.isalnum() and word not in self.stop_words:
                    filtered_words.append(word)
            
            # 词形还原
            lemmatized_words = []
            if self.lemmatizer:
                for word in filtered_words:
                    lemmatized = self.lemmatizer.lemmatize(word)
                    lemmatized_words.append(lemmatized)
            else:
                lemmatized_words = filtered_words
            
            # 词性标注
            pos_tags = []
            try:
                pos_tags = pos_tag(filtered_words)
            except Exception as e:
                logger.debug(f"词性标注失败: {e}")
            
            # 词频统计
            word_freq = Counter(lemmatized_words)
            top_words = word_freq.most_common(20)
            
            # 词性分布
            pos_dist = {}
            if pos_tags:
                for _, tag in pos_tags:
                    if tag not in pos_dist:
                        pos_dist[tag] = 0
                    pos_dist[tag] += 1
            
            return {
                "sentence_count": len(sentences),
                "word_count": len(words),
                "unique_word_count": len(set(lemmatized_words)),
                "avg_sentence_length": len(words) / max(len(sentences), 1),
                "avg_word_length": np.mean([len(w) for w in words]) if words else 0,
                "lexical_diversity": len(set(lemmatized_words)) / max(len(lemmatized_words), 1),
                "top_words": top_words,
                "pos_distribution": pos_dist,
                "filtered_word_count": len(lemmatized_words)
            }
            
        except Exception as e:
            logger.error(f"基础文本分析失败: {e}")
            return {
                "sentence_count": 0,
                "word_count": 0,
                "unique_word_count": 0,
                "avg_sentence_length": 0,
                "avg_word_length": 0,
                "lexical_diversity": 0,
                "top_words": [],
                "pos_distribution": {},
                "filtered_word_count": 0
            }
    
    def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """提取关键词"""
        try:
            text_lower = text.lower()
            words = word_tokenize(text_lower)
            
            # 统计每个类别的关键词出现次数
            category_counts = {}
            category_words = {}
            
            for category, keywords in self.keyword_categories.items():
                count = 0
                found_words = []
                
                for keyword in keywords:
                    # 简单的字符串匹配
                    if keyword in text_lower:
                        count += 1
                        found_words.append(keyword)
                
                category_counts[category] = count
                category_words[category] = found_words
            
            # 计算类别权重
            total_keywords = sum(category_counts.values())
            category_weights = {}
            if total_keywords > 0:
                for category, count in category_counts.items():
                    category_weights[category] = count / total_keywords
            
            # 提取高频名词（作为潜在关键词）
            try:
                pos_tags = pos_tag(words)
                nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
                noun_freq = Counter(nouns)
                top_nouns = noun_freq.most_common(10)
            except:
                top_nouns = []
            
            return {
                "categories": category_counts,
                "category_weights": category_weights,
                "category_words": category_words,
                "top_nouns": top_nouns,
                "total_keywords": total_keywords
            }
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return {
                "categories": {},
                "category_weights": {},
                "category_words": {},
                "top_nouns": [],
                "total_keywords": 0
            }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """情感分析"""
        try:
            text_lower = text.lower()
            words = word_tokenize(text_lower)
            
            # 计算情感分数
            sentiment_score = 0.0
            sentiment_words = []
            
            for word in words:
                if word in self.sentiment_lexicon:
                    sentiment_score += self.sentiment_lexicon[word]
                    sentiment_words.append(word)
            
            # 归一化到[-1, 1]
            word_count = len(words)
            if word_count > 0:
                normalized_score = sentiment_score / word_count
            else:
                normalized_score = 0.0
            
            # 确定情感标签
            if normalized_score > 0.1:
                label = "positive"
            elif normalized_score < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            # 情感强度
            intensity = abs(normalized_score)
            
            return {
                "score": float(normalized_score),
                "label": label,
                "intensity": float(intensity),
                "sentiment_words": sentiment_words,
                "sentiment_word_count": len(sentiment_words),
                "method": "lexicon_based"
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                "score": 0.0,
                "label": "neutral",
                "intensity": 0.0,
                "sentiment_words": [],
                "sentiment_word_count": 0,
                "method": "error"
            }
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """提取实体（简化版）"""
        try:
            entities = []
            
            # 提取技术栈实体（基于常见技术名称）
            tech_patterns = [
                r'\b(python|javascript|java|c\+\+|c#|go|rust|ruby|php|swift)\b',
                r'\b(react|vue|angular|django|flask|fastapi|express|spring|laravel)\b',
                r'\b(postgresql|mysql|mongodb|redis|elasticsearch|cassandra)\b',
                r'\b(aws|azure|google cloud|aliyun|heroku)\b',
                r'\b(docker|kubernetes|git|jenkins|terraform)\b'
            ]
            
            for pattern in tech_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = match.group().lower()
                    if entity not in entities:
                        entities.append(entity)
            
            # 提取项目相关实体
            project_entities = []
            project_patterns = [
                r'\b(project|application|system|platform|solution)\b',
                r'\b(api|sdk|library|framework|tool)\b',
                r'\b(database|server|client|interface|protocol)\b'
            ]
            
            for pattern in project_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # 获取上下文（前2个和后2个词）
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end].strip()
                    
                    project_entities.append({
                        "entity": match.group().lower(),
                        "context": context
                    })
            
            # 提取数字（版本号、数量等）
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
            
            # 提取URL
            urls = re.findall(r'https?://[^\s]+', text)
            
            # 提取电子邮件
            emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
            
            return {
                "count": len(entities) + len(project_entities),
                "technologies": entities,
                "project_entities": project_entities,
                "numbers": numbers,
                "urls": urls,
                "emails": emails,
                "has_technical_content": len(entities) > 0,
                "has_contact_info": len(emails) > 0 or len(urls) > 0
            }
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return {
                "count": 0,
                "technologies": [],
                "project_entities": [],
                "numbers": [],
                "urls": [],
                "emails": [],
                "has_technical_content": False,
                "has_contact_info": False
            }
    
    def _analyze_topics(self, text: str) -> Dict[str, Any]:
        """主题分析（简化版）"""
        try:
            # 基于关键词的主题分类
            text_lower = text.lower()
            
            # 定义主题和关键词
            topics = {
                "technology": ["software", "application", "system", "code", "program"],
                "business": ["business", "market", "product", "revenue", "profit"],
                "development": ["develop", "build", "create", "implement", "design"],
                "quality": ["quality", "reliable", "secure", "efficient", "test"],
                "innovation": ["innovative", "novel", "unique", "advanced", "cutting-edge"]
            }
            
            topic_scores = {}
            topic_keywords = {}
            
            for topic, keywords in topics.items():
                score = 0
                found_keywords = []
                
                for keyword in keywords:
                    if keyword in text_lower:
                        score += 1
                        found_keywords.append(keyword)
                
                topic_scores[topic] = score
                topic_keywords[topic] = found_keywords
            
            # 确定主要主题
            if topic_scores:
                main_topic = max(topic_scores.items(), key=lambda x: x[1])
                main_topic_name = main_topic[0]
                main_topic_score = main_topic[1]
            else:
                main_topic_name = "general"
                main_topic_score = 0
            
            # 主题分布
            total_score = sum(topic_scores.values())
            topic_distribution = {}
            if total_score > 0:
                for topic, score in topic_scores.items():
                    topic_distribution[topic] = score / total_score
            
            return {
                "count": len(topic_scores),
                "scores": topic_scores,
                "distribution": topic_distribution,
                "main_topic": main_topic_name,
                "main_topic_score": main_topic_score,
                "topic_keywords": topic_keywords
            }
            
        except Exception as e:
            logger.error(f"主题分析失败: {e}")
            return {
                "count": 0,
                "scores": {},
                "distribution": {},
                "main_topic": "unknown",
                "main_topic_score": 0,
                "topic_keywords": {}
            }
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """可读性分析"""
        try:
            # 句子数量
            sentences = sent_tokenize(text)
            sentence_count = len(sentences)
            
            # 单词数量
            words = word_tokenize(text)
            word_count = len(words)
            
            # 音节数量（估计）
            syllable_count = 0
            for word in words:
                # 简单的音节计数规则
                word_lower = word.lower()
                vowels = "aeiouy"
                
                if len(word_lower) <= 3:
                    syllable_count += 1
                else:
                    # 计算元音数量（简化）
                    prev_char = ''
                    syllable_in_word = 0
                    
                    for char in word_lower:
                        if char in vowels:
                            if prev_char not in vowels:
                                syllable_in_word += 1
                        prev_char = char
                    
                    # 至少一个音节
                    if syllable_in_word == 0:
                        syllable_in_word = 1
                    
                    syllable_count += syllable_in_word
            
            # 计算Flesch-Kincaid可读性分数
            if sentence_count > 0 and word_count > 0:
                # Flesch Reading Ease
                flesch_score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
                
                # Flesch-Kincaid Grade Level
                fk_grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
                
                # 确定可读性级别
                if flesch_score >= 90:
                    level = "Very Easy"
                elif flesch_score >= 80:
                    level = "Easy"
                elif flesch_score >= 70:
                    level = "Fairly Easy"
                elif flesch_score >= 60:
                    level = "Standard"
                elif flesch_score >= 50:
                    level = "Fairly Difficult"
                elif flesch_score >= 30:
                    level = "Difficult"
                else:
                    level = "Very Difficult"
            else:
                flesch_score = 0.0
                fk_grade = 0.0
                level = "Unknown"
            
            # 计算平均句子长度
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            # 计算平均单词长度
            avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
            
            return {
                "flesch_score": float(flesch_score),
                "flesch_kincaid_grade": float(fk_grade),
                "readability_level": level,
                "sentence_count": sentence_count,
                "word_count": word_count,
                "syllable_count": syllable_count,
                "avg_sentence_length": float(avg_sentence_length),
                "avg_word_length": float(avg_word_length),
                "complex_words": self._count_complex_words(words)  # 复杂词数量
            }
            
        except Exception as e:
            logger.error(f"可读性分析失败: {e}")
            return {
                "flesch_score": 0.0,
                "flesch_kincaid_grade": 0.0,
                "readability_level": "Unknown",
                "sentence_count": 0,
                "word_count": 0,
                "syllable_count": 0,
                "avg_sentence_length": 0.0,
                "avg_word_length": 0.0,
                "complex_words": 0
            }
    
    def _count_complex_words(self, words: List[str]) -> int:
        """计算复杂词数量（超过3个音节的词）"""
        complex_count = 0
        
        for word in words:
            word_lower = word.lower()
            vowels = "aeiouy"
            
            # 简单的音节计数
            syllable_count = 0
            prev_char = ''
            
            for char in word_lower:
                if char in vowels:
                    if prev_char not in vowels:
                        syllable_count += 1
                prev_char = char
            
            # 至少一个音节
            if syllable_count == 0:
                syllable_count = 1
            
            if syllable_count > 3:
                complex_count += 1
        
        return complex_count
    
    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """生成摘要（简化版）"""
        try:
            sentences = sent_tokenize(text)
            
            if not sentences:
                return ""
            
            # 简单的摘要：取前几个句子
            if len(sentences) <= max_sentences:
                return " ".join(sentences)
            
            # 对于长文本，取开头和结尾
            first_part = sentences[:max_sentences // 2 + 1]
            last_part = sentences[-(max_sentences // 2):]
            
            summary_sentences = first_part + last_part
            
            return " ".join(summary_sentences)
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    async def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """比较两个文本"""
        try:
            # 分析两个文本
            analysis1 = await self.analyze_text(text1)
            analysis2 = await self.analyze_text(text2)
            
            # 计算相似度
            similarity_score = self._calculate_text_similarity(text1, text2)
            
            # 比较关键词
            keywords1 = set(analysis1["keywords"].get("categories", {}).keys())
            keywords2 = set(analysis2["keywords"].get("categories", {}).keys())
            
            common_keywords = keywords1.intersection(keywords2)
            
            # 比较主题
            topic1 = analysis1["topics"].get("main_topic", "unknown")
            topic2 = analysis2["topics"].get("main_topic", "unknown")
            
            # 比较情感
            sentiment1 = analysis1["sentiment"].get("label", "neutral")
            sentiment2 = analysis2["sentiment"].get("label", "neutral")
            
            return {
                "similarity_score": similarity_score,
                "common_keywords": list(common_keywords),
                "topic_match": topic1 == topic2,
                "topic1": topic1,
                "topic2": topic2,
                "sentiment_match": sentiment1 == sentiment2,
                "sentiment1": sentiment1,
                "sentiment2": sentiment2,
                "analysis1": analysis1,
                "analysis2": analysis2
            }
            
        except Exception as e:
            logger.error(f"文本比较失败: {e}")
            return {"error": str(e)}
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版）"""
        try:
            if not text1 or not text2:
                return 0.0
            
            # 转换为小写并分词
            words1 = set(word_tokenize(text1.lower()))
            words2 = set(word_tokenize(text2.lower()))
            
            # 移除停用词
            words1 = words1 - self.stop_words
            words2 = words2 - self.stop_words
            
            # 计算Jaccard相似度
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "version": self.version,
            "model_type": "NLP Processor",
            "keyword_categories": len(self.keyword_categories),
            "sentiment_lexicon_size": len(self.sentiment_lexicon),
            "stop_words_size": len(self.stop_words),
            "is_loaded": True
        }