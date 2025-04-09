from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

from core.database import Base

# 脚本类型枚举
class ScriptType(str, enum.Enum):
    SHELL = "shell"    # Shell脚本
    PYTHON = "python"  # Python脚本
    SQL = "sql"        # SQL脚本

# 脚本模型
class Script(Base):
    __tablename__ = "scripts"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # 脚本内容
    type = Column(String(20), nullable=False)  # 脚本类型
    creator_id = Column(String(36), nullable=False)
    is_public = Column(Boolean, default=False)  # 是否公开脚本
    tags = Column(String(255), nullable=True)  # 逗号分隔的标签
    version = Column(Integer, default=1)  # 版本号
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Script {self.name}>"
    
    @property
    def tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]
    
    @tags_list.setter
    def tags_list(self, tags_list):
        if not tags_list:
            self.tags = None
        else:
            self.tags = ",".join(tags_list)
    
    @property
    def file_name(self):
        """生成脚本文件名"""
        extensions = {
            ScriptType.SHELL: ".sh",
            ScriptType.PYTHON: ".py",
            ScriptType.SQL: ".sql"
        }
        ext = extensions.get(self.type, "")
        return f"{self.name.replace(' ', '_')}_{self.id}{ext}" 