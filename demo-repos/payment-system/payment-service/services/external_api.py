"""
External Payment Gateway Integration
Handles communication with third-party payment processors
"""
import requests
import logging
from typing import Dict, Optional
import os
import time

logger = logging.getLogger(__name__)


class ExternalPaymentGateway:
    """
    Integration with external payment gateway (e.g., Stripe, PayPal)
    
    RISK: No circuit breaker pattern
    RISK: No timeout on HTTP requests
    RISK: Synchronous blocking calls
    """
    
    def __init__(self):
        self.gateway_url = os.getenv(
            "PAYMENT_GATEWAY_URL",
            "https://api.payment-gateway.example.com"
        )
        self.api_key = os.getenv("PAYMENT_GATEWAY_API_KEY", "test_key_12345")
        self.merchant_id = os.getenv("MERCHANT_ID", "merchant_67890")
        
        # RISK: No connection pooling configuration
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def charge(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        customer_id: str
    ) -> Dict:
        """
        Process a charge through the payment gateway
        
        RISK: No timeout specified - can hang indefinitely
        RISK: No retry logic with exponential backoff
        RISK: No circuit breaker to prevent cascading failures
        """
        endpoint = f"{self.gateway_url}/v1/charges"
        
        payload = {
            "amount": int(amount * 100),  # Convert to cents
            "currency": currency,
            "payment_method": payment_method,
            "customer": customer_id,
            "merchant_id": self.merchant_id,
            "capture": True
        }
        
        try:
            logger.info(f"Charging ${amount} for customer {customer_id}")
            
            # RISK: No timeout parameter - can block forever
            response = self.session.post(endpoint, json=payload)
            
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Charge successful: {result.get('id')}")
            
            return {
                "status": "completed",
                "transaction_id": result.get("id"),
                "payment_method": payment_method,
                "gateway_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment gateway error: {str(e)}")
            # RISK: No fallback or degraded mode
            raise Exception(f"Gateway communication failed: {str(e)}")
    
    def refund(
        self,
        transaction_id: str,
        amount: float
    ) -> Dict:
        """
        Process a refund through the payment gateway
        
        RISK: No timeout on request
        RISK: No idempotency handling
        """
        endpoint = f"{self.gateway_url}/v1/refunds"
        
        payload = {
            "charge": transaction_id,
            "amount": int(amount * 100),
            "merchant_id": self.merchant_id
        }
        
        try:
            logger.info(f"Processing refund of ${amount} for transaction {transaction_id}")
            
            # RISK: No timeout parameter
            response = self.session.post(endpoint, json=payload)
            
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Refund successful: {result.get('id')}")
            
            return {
                "status": "completed",
                "refund_id": result.get("id"),
                "gateway_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Refund gateway error: {str(e)}")
            raise Exception(f"Refund failed: {str(e)}")
    
    def verify_payment(self, transaction_id: str) -> Dict:
        """
        Verify payment status with gateway
        
        RISK: No caching of verification results
        RISK: No timeout
        """
        endpoint = f"{self.gateway_url}/v1/charges/{transaction_id}"
        
        try:
            # RISK: No timeout parameter
            response = self.session.get(endpoint)
            
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "status": result.get("status"),
                "amount": result.get("amount", 0) / 100,
                "paid": result.get("paid", False)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Verification error: {str(e)}")
            raise Exception(f"Verification failed: {str(e)}")
    
    def get_customer_payment_methods(self, customer_id: str) -> list:
        """
        Retrieve saved payment methods for a customer
        
        RISK: No pagination for large result sets
        RISK: No timeout
        """
        endpoint = f"{self.gateway_url}/v1/customers/{customer_id}/payment_methods"
        
        try:
            # RISK: No timeout parameter
            response = self.session.get(endpoint)
            
            response.raise_for_status()
            
            result = response.json()
            
            return result.get("data", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch payment methods: {str(e)}")
            return []
    
    def health_check(self) -> bool:
        """
        Check if payment gateway is reachable
        
        RISK: Even health check has no timeout
        """
        endpoint = f"{self.gateway_url}/health"
        
        try:
            # RISK: No timeout even for health check
            response = self.session.get(endpoint)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Gateway health check failed: {str(e)}")
            return False

# Made with Bob
