from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.order import Order
from app.dependencies import get_current_user
from app.models.order import OrderItem
from app.models.product import Product
from app.schemas.order_item import OrderItemCreate
from app.utils import success_response

router = APIRouter(prefix="/orders", tags=["orders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_order(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_order = Order(owner=current_user)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.owner == current_user
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order topilmadi")

    items = (
        db.query(OrderItem)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    result_items = []
    total = 0

    for item in items:
        product = item.product
        subtotal = product.price * item.quantity
        total += subtotal

        result_items.append({
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return {
        "id": order.id,
        "owner": order.owner,
        "total_price": total,
        "items": result_items,
        "items_count": len(result_items)
    }

@router.post("/{order_id}/add-product")
def add_product_to_order(
    order_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.owner == current_user
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order topilmadi")

    product = db.query(Product).filter(Product.id == item.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product topilmadi")

    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == order.id,
        OrderItem.product_id == product.id
    ).first()

    if existing_item:
        
        existing_item.quantity += item.quantity
    else:
        
        existing_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity
        )
        db.add(existing_item)

    
    order.total_price = (
    (order.total_price or 0)
    + product.price * item.quantity
)

    db.commit()
    db.refresh(order)

    return success_response({
    "order_id": order.id,
    "product_id": product.id
})