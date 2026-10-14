"""
用户路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
import app.crud as crud
import app.schemas as schemas
from app.schemas import ResponseModel

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/", response_model=ResponseModel, summary="创建用户")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    new_user = crud.create_user(db, user)
    
    return ResponseModel(
        message="用户创建成功",
        data=schemas.UserResponse.model_validate(new_user).model_dump()
    )


@router.get("/{user_id}", response_model=ResponseModel, summary="查询单个用户")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """查询单个用户"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return ResponseModel(
        data=schemas.UserResponse.model_validate(user).model_dump()
    )


@router.get("/", response_model=ResponseModel, summary="查询用户列表")
def get_users(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    status: Optional[str] = Query(None, description="状态过滤"),
    keyword: Optional[str] = Query(None, description="关键字搜索"),
    db: Session = Depends(get_db)
):
    """查询用户列表"""
    users = crud.get_users(db, skip=skip, limit=limit, status=status, keyword=keyword)
    users_data = [schemas.UserResponse.model_validate(u).model_dump() for u in users]
    
    return ResponseModel(
        message=f"查询成功，共 {len(users_data)} 条记录",
        data=users_data
    )


@router.put("/{user_id}", response_model=ResponseModel, summary="更新用户")
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """更新用户"""
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.username:
        existing = crud.get_user_by_username(db, user.username)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user.email:
        existing = crud.get_user_by_email(db, user.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    updated_user = crud.update_user(db, user_id, user)
    
    return ResponseModel(
        message="用户更新成功",
        data=schemas.UserResponse.model_validate(updated_user).model_dump()
    )


@router.delete("/{user_id}", response_model=ResponseModel, summary="删除用户")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return ResponseModel(
        message="用户删除成功",
        data={"deleted_user_id": user_id}
    )
