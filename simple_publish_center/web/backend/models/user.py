from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, Enum
import enum
from datetime import datetime
import uuid

from core.database import Base
from core.security import get_password_hash

# 用户角色枚举
class UserRole(str, enum.Enum):
    ADMIN = "admin"    # 管理员
    USER = "user"      # 普通用户
    VIEWER = "viewer"  # 只读用户

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @classmethod
    def create(cls, username, email, password, role=UserRole.USER):
        """创建新用户"""
        hashed_password = get_password_hash(password)
        return cls(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        ) 