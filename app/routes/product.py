from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut,ProductUpdate
from app.dependencies import get_current_user  

router = APIRouter(prefix="/products", tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  
):
    new_product = Product(
        name=product.name,
        price=product.price,
        description=product.description, 
        owner=current_user  
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product topilmadi")

    if product.owner != current_user:
        raise HTTPException(status_code=403, detail="Ruxsat yo‘q")

    db.delete(product)
    db.commit()

    return {"message": "Product o‘chirildi"}

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Topilmadi")

   
    if db_product.owner != current_user:
        raise HTTPException(status_code=403, detail="Ruxsat yo‘q")

    if product.name is not None:
        db_product.name = product.name

    if product.price is not None:
        db_product.price = product.price

    if product.description is not None:
        db_product.description = product.description

    db.commit()
    db.refresh(db_product)

    return db_product