from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.order import Order, Payment
from app.schemas.order import PaymentCreate, PaymentOut

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.post("/webhook", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def handle_payment_webhook(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    """
    Handles incoming webhooks from a payment provider.
    This endpoint is responsible for recording payment attempts and updating order statuses.
    It is designed to be idempotent based on the transaction_id.
    """
    # Idempotency check: prevent duplicate payment records for the same transaction
    if payment_in.transaction_id:
        existing_payment = db.query(Payment).filter(Payment.transaction_id == payment_in.transaction_id).first()
        if existing_payment:
            return existing_payment

    # Verify the order exists and lock it for update
    order = db.query(Order).filter(Order.id == payment_in.order_id).with_for_update().first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {payment_in.order_id} not found."
        )

    # Create the new payment record
    db_payment = Payment(**payment_in.dict())
    
    try:
        db.add(db_payment)

        # Update order status based on payment outcome
        if payment_in.status == "SUCCESS":
            order.status = "COMPLETED"
        elif payment_in.status == "FAILED":
            # Potentially revert stock here or handle in a separate refund/cancellation flow
            order.status = "FAILED"
        
        db.commit()
        db.refresh(db_payment)
        return db_payment
        
    except Exception as e:
        db.rollback()
        # In a real app, you would log the exception `e`
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the payment webhook."
        )

@router.get("/{order_id}", response_model=List[PaymentOut])
def get_payments_for_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all payment records associated with a specific order.
    """
    payments = db.query(Payment).filter(Payment.order_id == order_id).all()
    if not payments:
        # Check if the order itself exists to give a more accurate error
        order_exists = db.query(Order).filter(Order.id == order_id).first()
        if not order_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found."
            )
    return payments

