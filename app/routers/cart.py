from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.models.CartWithProductOut import CartWithProductOut

from app.core.database import get_db
from app.models.cart import Cart
from app.models.product import Product
from app.schemas.cart import CartCreate, CartOut, CartUpdate

router = APIRouter(
    prefix="/shop/cart",
    tags=["cart"]
)

@router.post("/", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(cart: CartCreate, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(Product).filter(Product.id == cart.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {cart.product_id} not found"
        )

    # Check if item is already in the cart for that user
    existing_item = db.query(Cart).filter(
        Cart.user_id == cart.user_id,
        Cart.product_id == cart.product_id
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already in cart. Use PUT to update quantity."
        )

    db_cart_item = Cart(**cart.dict())
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item
@router.get("/{user_id}", response_model=List[CartWithProductOut])
def get_cart_items(user_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart not found")
    result = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            result.append(CartWithProductOut(
                id=item.id,
                user_id=item.user_id,
                product_id=item.product_id,
                quantity=item.quantity,
                product_name=product.name,
                price=product.price
            ))
    return result
@router.put("/{cart_id}", response_model=CartOut)
def update_cart_item_quantity(cart_id: int, cart_update: CartUpdate, db: Session = Depends(get_db)):
    db_cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
    if not db_cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if cart_update.quantity is not None:
        db_cart_item.quantity = cart_update.quantity
        db.commit()
        db.refresh(db_cart_item)

    return db_cart_item

@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_cart(cart_id: int, db: Session = Depends(get_db)):
    db_cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
    if not db_cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    db.delete(db_cart_item)
    db.commit()
    return

