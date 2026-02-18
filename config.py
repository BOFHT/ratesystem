# config.py - 兼容性文件（指向 config_cloud.py）
"""
这个文件是为了兼容性而存在的。
实际配置在 config_cloud.py 中。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 从 config_cloud 导入所有内容
from config_cloud import *

print("注意：使用 config_cloud.py 作为配置源")
print(f"应用名称: {settings.APP_NAME}")
print(f"调试模式: {settings.DEBUG}")

# 导出 settings 对象
__all__ = ["settings"]