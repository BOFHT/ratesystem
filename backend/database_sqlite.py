# backend/database_sqlite.py - 简化的SQLite数据库模块（云端部署版）
import os
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "projects.db")
DB_DIR = os.path.join(os.path.dirname(__file__), "database")

# 确保数据库目录存在
os.makedirs(DB_DIR, exist_ok=True)

class SQLiteDatabase:
    """简化的SQLite数据库操作类"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建项目表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            repo_url TEXT,
            tags TEXT,  -- 逗号分隔的标签
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建项目分析表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            analysis_data TEXT,  -- JSON格式的分析数据
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        ''')
        
        # 创建评分日志表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scoring_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            algorithm_type TEXT NOT NULL,
            score REAL NOT NULL,
            score_breakdown TEXT,  -- JSON格式的分数明细
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """创建新项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        project_id = project_data.get('id') or f"proj_{datetime.now().timestamp()}"
        
        cursor.execute('''
        INSERT INTO projects (id, name, description, repo_url, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            project_data.get('name', ''),
            project_data.get('description', ''),
            project_data.get('repo_url', ''),
            ','.join(project_data.get('tags', [])),
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        
        if row:
            project = dict(row)
            # 转换tags回列表
            if project.get('tags'):
                project['tags'] = project['tags'].split(',')
            else:
                project['tags'] = []
            conn.close()
            return project
        
        conn.close()
        return None
    
    def update_project_rating(self, project_id: str, rating_data: Dict[str, Any]) -> bool:
        """更新项目评分（简化版，实际存储到评分日志表）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 将评分数据存储到scoring_logs表
        cursor.execute('''
        INSERT INTO scoring_logs (project_id, algorithm_type, score, score_breakdown)
        VALUES (?, ?, ?, ?)
        ''', (
            project_id,
            rating_data.get('algorithm_type', 'simple'),
            rating_data.get('overall_score', 0.0),
            json.dumps(rating_data) if rating_data else '{}'
        ))
        
        # 更新项目表的updated_at时间
        cursor.execute('''
        UPDATE projects SET updated_at = ? WHERE id = ?
        ''', (datetime.now(), project_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_project_rating(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目最新评分"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM scoring_logs 
        WHERE project_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
        ''', (project_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 解析JSON格式的score_breakdown
            import json
            rating_data = {
                'id': row[0],
                'project_id': row[1],
                'algorithm_type': row[2],
                'score': row[3],
                'score_breakdown': json.loads(row[4]) if row[4] else {},
                'created_at': row[5]
            }
            return rating_data
        
        return None
    
    def list_projects(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出所有项目"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        
        projects = []
        for row in rows:
            project = dict(row)
            if project.get('tags'):
                project['tags'] = project['tags'].split(',')
            else:
                project['tags'] = []
            projects.append(project)
        
        conn.close()
        return projects

# 全局数据库实例
db_instance = SQLiteDatabase()

# FastAPI依赖函数
def get_db():
    """获取数据库连接（FastAPI依赖）"""
    return db_instance

# SQLAlchemy兼容的模型类（简化版）
class Project:
    """项目模型（简化版）"""
    pass

class ProjectAnalysis:
    """项目分析模型（简化版）"""
    pass

class ScoringLog:
    """评分日志模型（简化版）"""
    pass

# 辅助函数
def json_dumps(data: Any) -> str:
    """JSON序列化辅助函数"""
    import json
    return json.dumps(data, ensure_ascii=False, default=str)

def json_loads(data: str) -> Any:
    """JSON反序列化辅助函数"""
    import json
    return json.loads(data) if data else {}