from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # 项目信息
    PROJECT_NAME: str = "工作流管理系统"
    PROJECT_DESCRIPTION: str = "用于管理和执行工作流的API服务"
    VERSION: str = "0.1.0"
    
    # API设置
    API_PREFIX: str = "/api/v1"
    
    # 安全设置
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 生产环境应替换为更安全的密钥
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时过期
    
    # CORS设置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # 数据库设置
    DATABASE_URL: str = "sqlite:///./workflow.db"
    
    # 文件存储设置
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    SCRIPT_DIR: Path = BASE_DIR / "scripts"
    LOG_DIR: Path = BASE_DIR / "logs"
    WORKFLOW_DIR: Path = BASE_DIR / "workflows"
    
    # 执行设置
    MAX_CONCURRENT_EXECUTIONS: int = 5
    SCRIPT_EXECUTION_TIMEOUT: int = 300  # 秒

    class Config:
        env_file = ".env"
        case_sensitive = True

# 加载环境变量
settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.SCRIPT_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
os.makedirs(settings.WORKFLOW_DIR, exist_ok=True) 