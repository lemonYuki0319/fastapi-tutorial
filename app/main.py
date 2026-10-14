"""
FastAPI 主程序入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import engine, Base
from app.routers import users, products
from app.schemas import ResponseModel
from loguru import logger
import sys

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## FastAPI CRUD 进阶实战教程

### 功能特性
- ✅ 完整的 CRUD 操作
- ✅ SQLite 数据库持久化
- ✅ Pydantic 数据校验
- ✅ 统一响应格式
- ✅ 全局异常处理

### 业务模块
- **用户管理**：用户的增删改查
- **商品管理**：商品的增删改查
    """,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册路由
app.include_router(users.router)
app.include_router(products.router)


# 异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数校验异常处理"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content=ResponseModel(
            code=422,
            message="参数校验失败: " + "; ".join(errors),
            data={"errors": exc.errors()}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.exception(f"未处理的异常: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ResponseModel(
            code=500,
            message=f"服务器内部错误: {str(exc)}" if settings.DEBUG else "服务器内部错误",
            data=None
        ).model_dump()
    )


# 根路径
@app.get("/", response_model=ResponseModel, tags=["根路径"])
def root():
    """根路径"""
    return ResponseModel(
        message="FastAPI 服务运行正常",
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    )


# 健康检查
@app.get("/health", response_model=ResponseModel, tags=["健康检查"])
def health_check():
    """健康检查"""
    return ResponseModel(
        message="服务健康",
        data={"status": "healthy"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
