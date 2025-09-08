import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app.core.database import get_db
from app.schemas.order import OrderOut, PaymentOut
from app.schemas.order import OrderCreate  # For direct purchase
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger(__name__)

from pydantic import BaseModel, model_validator, ValidationError

class CartPurchase(BaseModel):
    user_id: int

class DirectPurchase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class OrderBuyRequest(BaseModel):
    cart_purchase: Optional[CartPurchase] = None
    direct_purchase: Optional[DirectPurchase] = None
    provider: Optional[str] = "razorpay"

    @model_validator(mode="after")
    def check_one_of(self) -> "OrderBuyRequest":
        if not (self.cart_purchase or self.direct_purchase):
            raise ValueError("Either cart_purchase or direct_purchase must be provided.")
        if self.cart_purchase and self.direct_purchase:
            raise ValueError("Only one of cart_purchase or direct_purchase should be provided.")
        return self

class OrderBuyResponse(BaseModel):
    order: OrderOut
    payment_meta: Dict[str, Any]

@router.post("/buy", response_model=OrderBuyResponse, status_code=status.HTTP_201_CREATED)
def buy_order(request: OrderBuyRequest, db: Session = Depends(get_db)):
    """
    Create an order from cart or direct purchase, then prepare payment.
    """
    try:
        if request.cart_purchase:
            logger.info(f"User {request.cart_purchase.user_id} is buying from cart.")
            order = order_service.create_order_from_cart(db, request.cart_purchase.user_id)
        elif request.direct_purchase:
            logger.info(f"User {request.direct_purchase.user_id} is buying product {request.direct_purchase.product_id} x{request.direct_purchase.quantity} direct.")
            order = order_service.create_order_direct(
                db,
                user_id=request.direct_purchase.user_id,
                product_id=request.direct_purchase.product_id,
                quantity=request.direct_purchase.quantity
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid request: must provide cart_purchase or direct_purchase.")

        payment_meta = order_service.prepare_payment(db, order, provider=request.provider or "razorpay")
        logger.info(f"Order {order.id} created for user {order.user_id}. Payment prepared.")

        # Convert Decimal to float for total_amount
        order_out = OrderOut.from_orm(order)
        if isinstance(order_out.total_amount, Decimal):
            order_out.total_amount = float(order_out.total_amount)

        return {"order": order_out, "payment_meta": payment_meta}

    except order_service.InsufficientStockError as e:
        logger.warning(f"Order creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except order_service.NotFoundError as e:
        logger.warning(f"Order creation failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during order creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/{user_id}", response_model=List[OrderOut])
def list_orders(user_id: int, db: Session = Depends(get_db)):
    """
    List all orders for a user.
    """
    try:
        orders = order_service.get_orders_by_user(db, user_id)
        # Convert Decimal to float for total_amount
        result = []
        for order in orders:
            order_out = OrderOut.from_orm(order)
            if isinstance(order_out.total_amount, Decimal):
                order_out.total_amount = float(order_out.total_amount)
            result.append(order_out)
        return result
    except order_service.NotFoundError as e:
        logger.warning(f"Orders not found for user {user_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/details/{order_id}", response_model=OrderOut)
def order_details(order_id: int, db: Session = Depends(get_db)):
    """
    Get order details including related payments.
    """
    try:
        order = order_service.get_order_details(db, order_id)
        order_out = OrderOut.from_orm(order)
        if isinstance(order_out.total_amount, Decimal):
            order_out.total_amount = float(order_out.total_amount)
        return order_out
    except order_service.NotFoundError as e:
        logger.warning(f"Order {order_id} not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting order details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

