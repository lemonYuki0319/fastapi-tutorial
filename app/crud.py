"""
CRUD 数据库操作函数
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import app.models as models
import app.schemas as schemas


def create_user(db: Session, user: schemas.UserCreate):
    """创建用户"""
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password,
        phone=user.phone,
        status=user.status,
        remark=user.remark
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int):
    """根据 ID 查询用户"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """根据用户名查询用户"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """根据邮箱查询用户"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, keyword: Optional[str] = None):
    """查询用户列表"""
    query = db.query(models.User)
    
    if status:
        query = query.filter(models.User.status == status)
    
    if keyword:
        query = query.filter(
            or_(
                models.User.username.like(f"%{keyword}%"),
                models.User.email.like(f"%{keyword}%")
            )
        )
    
    query = query.order_by(models.User.created_at.desc())
    return query.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    """更新用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    """删除用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db.delete(db_user)
    db.commit()
    return db_user


def create_product(db: Session, product: schemas.ProductCreate):
    """创建商品"""
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        status=product.status
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product_by_id(db: Session, product_id: int):
    """根据 ID 查询商品"""
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, keyword: Optional[str] = None, min_price: Optional[int] = None, max_price: Optional[int] = None):
    """查询商品列表"""
    query = db.query(models.Product)
    
    if status:
        query = query.filter(models.Product.status == status)
    
    if keyword:
        query = query.filter(models.Product.name.like(f"%{keyword}%"))
    
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    
    query = query.order_by(models.Product.created_at.desc())
    return query.offset(skip).limit(limit).all()


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    """更新商品"""
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return None
    
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    """删除商品"""
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return None
    
    db.delete(db_product)
    db.commit()
    return db_product
