# app/services/stripe.py
"""Stripe payment service integration."""
import os
import stripe
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


class StripeService:
    """Service for Stripe payment operations."""

    @staticmethod
    def create_customer(email: str, name: str = "", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name or None,
                metadata=metadata or {}
            )
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def create_product(name: str, description: str = "", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new Stripe product."""
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )
            return {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "active": product.active,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def create_price(product_id: str, amount_cents: int, currency: str = "usd",
                     interval: str = None, interval_count: int = 1) -> Dict[str, Any]:
        """Create a price for a product."""
        try:
            price_data = {
                "product": product_id,
                "unit_amount": amount_cents,
                "currency": currency,
            }
            if interval:
                price_data["recurring"] = {
                    "interval": interval,
                    "interval_count": interval_count
                }
            price = stripe.Price.create(**price_data)
            return {
                "id": price.id,
                "product": price.product,
                "unit_amount": price.unit_amount,
                "currency": price.currency,
                "recurring": price.recurring,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def create_payment_link(price_id: str, success_url: str, cancel_url: str,
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a payment link for a price."""
        try:
            link = stripe.PaymentLink.create(
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {}
            )
            return {
                "id": link.id,
                "url": link.url,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def create_checkout_session(customer_id: str, price_id: str, success_url: str,
                                cancel_url: str, mode: str = "payment",
                                metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a checkout session."""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {}
            )
            return {
                "id": session.id,
                "url": session.url,
                "customer": session.customer,
                "payment_status": session.payment_status,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def retrieve_customer(customer_id: str) -> Dict[str, Any]:
        """Retrieve a customer."""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "balance": customer.balance,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def list_products(limit: int = 10) -> Dict[str, Any]:
        """List all products."""
        try:
            resp = stripe.Product.list(limit=limit)
            products = []
            for p in resp.data:
                products.append({
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "active": p.active,
                })
            return {"products": products, "has_more": resp.has_more, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get quick Stripe account stats."""
        try:
            subs = stripe.Subscription.list(status="active", limit=100)
            active_count = len(subs.data)

            charges = stripe.Charge.list(limit=30)
            total_revenue = sum(c.amount for c in charges.data if c.paid and not c.refunded)

            balance = stripe.Balance.retrieve()
            available = sum(a.amount for a in balance.available)
            currency = balance.available[0].currency if balance.available else "usd"

            return {
                "active_subscriptions": active_count,
                "recent_revenue_cents": total_revenue,
                "available_balance_cents": available,
                "currency": currency,
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
