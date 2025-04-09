from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn

from api.user import router as user_router
from api.workflow import router as workflow_router
from api.script import router as script_router
from api.instance import router as instance_router
from core.config import settings
from core.security import create_access_token, get_current_user

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 设置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户登录认证
@app.post("/api/v1/auth/login", tags=["认证"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    """
    # 简化示例，实际应用中需要查询数据库验证用户
    if form_data.username != "admin" or form_data.password != "admin123":
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "accessToken": access_token,
            "tokenType": "bearer",
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }

# 获取当前用户信息
@app.get("/api/v1/users/current", tags=["用户"])
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "userId": "1",
            "username": current_user.username,
            "email": f"{current_user.username}@example.com",
            "role": "admin",
            "createdAt": "2023-01-01T00:00:00Z"
        }
    }

# 注册路由
app.include_router(
    user_router,
    prefix="/api/v1",
    tags=["用户管理"]
)
app.include_router(
    workflow_router,
    prefix="/api/v1",
    tags=["工作流管理"]
)
app.include_router(
    script_router,
    prefix="/api/v1",
    tags=["脚本管理"]
)
app.include_router(
    instance_router, 
    prefix="/api/v1",
    tags=["执行实例"]
)

# 根路径响应
@app.get("/")
async def root():
    return {"message": "工作流管理系统API服务"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 