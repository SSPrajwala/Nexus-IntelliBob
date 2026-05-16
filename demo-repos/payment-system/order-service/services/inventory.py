"""
Inventory Service
Handles inventory management and reservation
"""
import requests
import logging
from typing import List, Dict
import os
import time

logger = logging.getLogger(__name__)


class InventoryService:
    """
    Manages inventory checks and reservations
    
    RISK: No circuit breaker for external inventory system
    RISK: Synchronous blocking calls
    """
    
    def __init__(self):
        self.inventory_service_url = os.getenv(
            "INVENTORY_SERVICE_URL",
            "http://inventory-service:8004"
        )
        
        # RISK: In-memory inventory cache without proper invalidation
        self._inventory_cache = {}
        self._reservation_cache = {}
    
    def check_availability(self, item_id: str, quantity: int) -> bool:
        """
        Check if item is available in requested quantity
        
        RISK: No timeout on HTTP request
        RISK: Cache without TTL
        """
        # Check cache first (RISK: stale data)
        cache_key = f"{item_id}:{quantity}"
        if cache_key in self._inventory_cache:
            cached_result = self._inventory_cache[cache_key]
            # RISK: No timestamp check, could be very old data
            return cached_result
        
        try:
            endpoint = f"{self.inventory_service_url}/api/v1/inventory/{item_id}"
            
            # RISK: No timeout specified
            response = requests.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            available = data.get("available_quantity", 0) >= quantity
            
            # Cache result (RISK: unbounded cache)
            self._inventory_cache[cache_key] = available
            
            return available
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Inventory check failed for {item_id}: {str(e)}")
            # RISK: Fail open - assume available on error
            return True
    
    def reserve_inventory(self, items: List[Dict]) -> bool:
        """
        Reserve inventory for order items
        
        RISK: No distributed transaction support
        RISK: Partial reservation possible if some items fail
        RISK: No timeout on requests
        """
        reservation_id = f"res_{int(time.time() * 1000)}"
        reserved_items = []
        
        try:
            for item in items:
                item_id = item.get("id")
                quantity = item.get("quantity", 1)
                
                # Check availability first
                if not self.check_availability(item_id, quantity):
                    logger.warning(f"Item {item_id} not available in quantity {quantity}")
                    # RISK: Need to rollback already reserved items
                    self._rollback_reservations(reserved_items)
                    return False
                
                # Reserve the item (RISK: no timeout)
                endpoint = f"{self.inventory_service_url}/api/v1/inventory/reserve"
                
                payload = {
                    "item_id": item_id,
                    "quantity": quantity,
                    "reservation_id": reservation_id
                }
                
                response = requests.post(endpoint, json=payload)
                response.raise_for_status()
                
                reserved_items.append({
                    "item_id": item_id,
                    "quantity": quantity,
                    "reservation_id": reservation_id
                })
                
                logger.info(f"Reserved {quantity} units of {item_id}")
            
            # Store reservation info (RISK: in-memory, lost on restart)
            self._reservation_cache[reservation_id] = reserved_items
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Inventory reservation failed: {str(e)}")
            # RISK: Partial reservations might not be rolled back
            self._rollback_reservations(reserved_items)
            return False
    
    def release_inventory(self, items: List[Dict]) -> bool:
        """
        Release reserved inventory (e.g., on order cancellation)
        
        RISK: No retry logic if release fails
        RISK: No timeout on requests
        """
        try:
            for item in items:
                item_id = item.get("id")
                quantity = item.get("quantity", 1)
                
                endpoint = f"{self.inventory_service_url}/api/v1/inventory/release"
                
                payload = {
                    "item_id": item_id,
                    "quantity": quantity
                }
                
                # RISK: No timeout specified
                response = requests.post(endpoint, json=payload)
                response.raise_for_status()
                
                logger.info(f"Released {quantity} units of {item_id}")
            
            # Invalidate cache
            self._inventory_cache.clear()
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Inventory release failed: {str(e)}")
            # RISK: Inventory might remain locked
            return False
    
    def _rollback_reservations(self, reserved_items: List[Dict]):
        """
        Rollback partial reservations
        
        RISK: Best-effort rollback, might fail
        RISK: No compensation if rollback fails
        """
        for item in reserved_items:
            try:
                endpoint = f"{self.inventory_service_url}/api/v1/inventory/release"
                
                payload = {
                    "item_id": item["item_id"],
                    "quantity": item["quantity"],
                    "reservation_id": item.get("reservation_id")
                }
                
                # RISK: No timeout
                response = requests.post(endpoint, json=payload)
                response.raise_for_status()
                
                logger.info(f"Rolled back reservation for {item['item_id']}")
                
            except Exception as e:
                logger.error(f"Rollback failed for {item['item_id']}: {str(e)}")
                # RISK: Continue trying other items even if one fails
    
    def get_inventory_status(self, item_id: str) -> Dict:
        """
        Get current inventory status for an item
        
        RISK: No timeout
        RISK: No caching
        """
        try:
            endpoint = f"{self.inventory_service_url}/api/v1/inventory/{item_id}"
            
            # RISK: No timeout specified
            response = requests.get(endpoint)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get inventory status: {str(e)}")
            return {
                "item_id": item_id,
                "available_quantity": 0,
                "error": str(e)
            }
    
    def bulk_check_availability(self, items: List[Dict]) -> Dict[str, bool]:
        """
        Check availability for multiple items
        
        RISK: Sequential checks, no parallelization
        RISK: No timeout on individual requests
        """
        results = {}
        
        for item in items:
            item_id = item.get("id")
            quantity = item.get("quantity", 1)
            
            # RISK: Sequential blocking calls
            results[item_id] = self.check_availability(item_id, quantity)
        
        return results

# Made with Bob
