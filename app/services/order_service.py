
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from typing import Any, Dict, List, Optional
from ..models.cart import Cart
from app.models.order import Order, Payment
from app.models.product import Product
from app.schemas.order import OrderOut, PaymentOut
import logging

logger = logging.getLogger(__name__)

# --- Exception Classes ---
class InsufficientStockError(Exception):
	pass

class NotFoundError(Exception):
	pass

class IdempotencyError(Exception):
	def __init__(self, message, payment_out=None):
		super().__init__(message)
		self.payment_out = payment_out

# --- Service Functions ---
def create_order_from_cart(db: Session, user_id: int) -> Order:
	cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
	if not cart_items:
		raise NotFoundError("Cart is empty.")
	total_amount = Decimal("0")
	try:
		for item in cart_items:
			product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
			if not product:
				db.rollback()
				raise NotFoundError(f"Product {item.product_id} not found.")
			if product.stock < item.quantity:
				db.rollback()
				raise InsufficientStockError(f"Insufficient stock for {product.name}. Requested: {item.quantity}, Available: {product.stock}")
			total_amount += Decimal(str(product.price)) * item.quantity
			product.stock -= item.quantity
		order = Order(user_id=user_id, total_amount=total_amount, status="PENDING_PAYMENT")
		db.add(order)
		for item in cart_items:
			db.delete(item)
		db.commit()
		db.refresh(order)
		logger.info(f"Order {order.id} created from cart for user {user_id}")
		return order
	except Exception as e:
		db.rollback()
		logger.error(f"Error creating order from cart: {e}")
		raise

def create_order_direct(db: Session, user_id: int, product_id: int, quantity: int) -> Order:
	product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
	if not product:
		raise NotFoundError(f"Product {product_id} not found.")
	if product.stock < quantity:
		raise InsufficientStockError(f"Insufficient stock for {product.name}. Requested: {quantity}, Available: {product.stock}")
	total_amount = Decimal(str(product.price)) * quantity
	try:
		product.stock -= quantity
		order = Order(user_id=user_id, total_amount=total_amount, status="PENDING_PAYMENT")
		db.add(order)
		db.commit()
		db.refresh(order)
		logger.info(f"Order {order.id} created direct for user {user_id}, product {product_id}")
		return order
	except Exception as e:
		db.rollback()
		logger.error(f"Error creating direct order: {e}")
		raise

def prepare_payment(db: Session, order: Order, provider: str = "razorpay") -> Dict[str, Any]:
	# In a real app, this would call the provider SDK or API to create a payment session
	# Here, we just return a mock payment meta
	payment_meta = {
		"provider": provider,
		"order_id": order.id,
		"amount": float(order.total_amount),
		"currency": "INR",
		"payment_id": f"{provider}_order_{order.id}"
	}
	logger.info(f"Payment prepared for order {order.id} with provider {provider}")
	return payment_meta

def get_orders_by_user(db: Session, user_id: int) -> List[Order]:
	orders = db.query(Order).filter(Order.user_id == user_id).all()
	if not orders:
		raise NotFoundError(f"No orders found for user {user_id}.")
	return orders

def get_order_details(db: Session, order_id: int) -> Order:
	order = db.query(Order).filter(Order.id == order_id).first()
	if not order:
		raise NotFoundError(f"Order {order_id} not found.")
	return order

def get_payments_for_order(db: Session, order_id: int) -> List[Payment]:
	payments = db.query(Payment).filter(Payment.order_id == order_id).all()
	if not payments:
		raise NotFoundError(f"No payments found for order {order_id}.")
	return payments

def process_payment_webhook(db: Session, provider: str, transaction_id: str, order_id: int, status: str, amount: Decimal, extra: Optional[dict] = None, x_signature: Optional[str] = None) -> Payment:
	# Idempotency: check if payment with transaction_id exists
	existing = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
	if existing:
		raise IdempotencyError("Payment already processed for this transaction_id.", payment_out=PaymentOut.from_orm(existing))
	order = db.query(Order).filter(Order.id == order_id).with_for_update().first()
	if not order:
		raise NotFoundError(f"Order {order_id} not found.")
	db_payment = Payment(
		order_id=order_id,
		amount=amount,
		provider=provider,
		status=status,
		transaction_id=transaction_id
	)
	try:
		db.add(db_payment)
		if status.upper() == "SUCCESS":
			order.status = "COMPLETED"
		elif status.upper() == "FAILED":
			order.status = "FAILED"
		db.commit()
		db.refresh(db_payment)
		logger.info(f"Payment webhook processed: order {order_id}, tx={transaction_id}, status={status}")
		return db_payment
	except Exception as e:
		db.rollback()
		logger.error(f"Error processing payment webhook: {e}")
		raise
