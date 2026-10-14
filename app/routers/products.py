"""
商品路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
import app.crud as crud
import app.schemas as schemas
from app.schemas import ResponseModel

router = APIRouter(prefix="/products", tags=["商品管理"])


@router.post("/", response_model=ResponseModel, summary="创建商品")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """创建商品"""
    new_product = crud.create_product(db, product)
    
    return ResponseModel(
        message="商品创建成功",
        data=schemas.ProductResponse.model_validate(new_product).model_dump()
    )


@router.get("/{product_id}", response_model=ResponseModel, summary="查询单个商品")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """查询单个商品"""
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return ResponseModel(
        data=schemas.ProductResponse.model_validate(product).model_dump()
    )


@router.get("/", response_model=ResponseModel, summary="查询商品列表")
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, ge=0, description="最低价格（分）"),
    max_price: Optional[int] = Query(None, ge=0, description="最高价格（分）"),
    db: Session = Depends(get_db)
):
    """查询商品列表"""
    products = crud.get_products(
        db, skip=skip, limit=limit, status=status,
        keyword=keyword, min_price=min_price, max_price=max_price
    )
    products_data = [schemas.ProductResponse.model_validate(p).model_dump() for p in products]
    
    return ResponseModel(
        message=f"查询成功，共 {len(products_data)} 条记录",
        data=products_data
    )


@router.put("/{product_id}", response_model=ResponseModel, summary="更新商品")
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """更新商品"""
    db_product = crud.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return ResponseModel(
        message="商品更新成功",
        data=schemas.ProductResponse.model_validate(db_product).model_dump()
    )


@router.delete("/{product_id}", response_model=ResponseModel, summary="删除商品")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除商品"""
    product = crud.delete_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return ResponseModel(
        message="商品删除成功",
        data={"deleted_product_id": product_id}
    )
