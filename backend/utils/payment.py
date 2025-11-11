import logging
from datetime import datetime, timezone
from database import db

from enum import Enum

logger = logging.getLogger(__name__)

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentService:
    @staticmethod
    async def create_payment(
        order_id: str,
        amount: float,
        payment_method: str,
        user_id: str
    ):
        """Create a payment record"""
        try:
            payment = {
                "order_id": order_id,
                "amount": amount,
                "payment_method": payment_method,
                "user_id": user_id,
                "status": PaymentStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            
            result = await db.payments.insert_one(payment)
            logger.info(f"Payment created for order {order_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return None
    
    @staticmethod
    async def process_payment(
        payment_id: str,
        payment_method: str,
        payment_details: dict
    ):
        """Process payment through payment gateway"""
        try:
            from bson import ObjectId
            
            payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
            if not payment:
                raise Exception("Payment not found")
            
            # TODO: Integrate with actual payment gateway (Stripe, Razorpay, etc.)
            # For now, simulate successful payment for UPI and Wallet
            # Credit card and COD require additional handling
            
            if payment_method in ["upi", "wallet"]:
                # Simulate payment processing
                await db.payments.update_one(
                    {"_id": ObjectId(payment_id)},
                    {
                        "$set": {
                            "status": PaymentStatus.SUCCESS.value,
                            "updated_at": datetime.now(timezone.utc),
                            "transaction_id": f"TXN-{ObjectId()}",
                        }
                    }
                )
                return {
                    "status": "success",
                    "payment_id": payment_id,
                    "message": "Payment processed successfully"
                }
            elif payment_method == "cod":
                # Cash on Delivery - mark as pending
                await db.payments.update_one(
                    {"_id": ObjectId(payment_id)},
                    {
                        "$set": {
                            "status": PaymentStatus.PENDING.value,
                            "updated_at": datetime.now(timezone.utc),
                        }
                    }
                )
                return {
                    "status": "pending",
                    "payment_id": payment_id,
                    "message": "Payment will be collected on delivery"
                }
            else:
                # Card payment - requires gateway integration
                await db.payments.update_one(
                    {"_id": ObjectId(payment_id)},
                    {
                        "$set": {
                            "status": PaymentStatus.PROCESSING.value,
                            "updated_at": datetime.now(timezone.utc),
                        }
                    }
                )
                return {
                    "status": "processing",
                    "payment_id": payment_id,
                    "message": "Payment processing"
                }
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    @staticmethod
    async def refund_payment(payment_id: str, reason: str = ""):
        """Refund a payment"""
        try:
            from bson import ObjectId
            
            await db.payments.update_one(
                {"_id": ObjectId(payment_id)},
                {
                    "$set": {
                        "status": PaymentStatus.REFUNDED.value,
                        "refund_reason": reason,
                        "updated_at": datetime.now(timezone.utc),
                    }
                }
            )
            logger.info(f"Payment {payment_id} refunded")
            return True
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            return False
    
    @staticmethod
    async def get_payment(payment_id: str):
        """Get payment details"""
        try:
            from bson import ObjectId
            payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
            if payment:
                payment["_id"] = str(payment["_id"])
            return payment
        except Exception as e:
            logger.error(f"Error fetching payment: {e}")
            return None
