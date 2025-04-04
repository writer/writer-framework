import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import shopify
import requests
from urllib.parse import urlparse
import pandas as pd
from ratelimit import limits, sleep_and_retry

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class ShopifyIntegration(WorkflowBlock):
    # Rate limit: 2 requests per second for API version 2024-01
    CALLS_PER_SECOND = 2
    
    def __init__(self):
        super().__init__()
        self.session = None
        
    @classmethod
    def register(cls, type: str):
        super(ShopifyIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Shopify Integration",
                "description": "Execute Shopify operations and manage store data",
                "category": "E-commerce",
                "fields": {
                    "shop_url": {
                        "name": "Shop URL",
                        "type": "Text",
                        "description": "Your Shopify shop URL"
                    },
                    "access_token": {
                        "name": "Access Token",
                        "type": "Text",
                        "description": "Shopify Admin API access token"
                    },
                    "api_version": {
                        "name": "API Version",
                        "type": "Text",
                        "description": "Shopify API version",
                        "default": "2024-01"
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            # Product Operations
                            "list_products": "List Products",
                            "get_product": "Get Product",
                            "create_product": "Create Product",
                            "update_product": "Update Product",
                            "delete_product": "Delete Product",
                            
                            # Order Operations
                            "list_orders": "List Orders",
                            "get_order": "Get Order",
                            "create_order": "Create Order",
                            "update_order": "Update Order",
                            "cancel_order": "Cancel Order",
                            
                            # Customer Operations
                            "list_customers": "List Customers",
                            "get_customer": "Get Customer",
                            "create_customer": "Create Customer",
                            "update_customer": "Update Customer",
                            
                            # Inventory Operations
                            "list_inventory": "List Inventory",
                            "adjust_inventory": "Adjust Inventory",
                            "get_inventory_level": "Get Inventory Level",
                            
                            # Collection Operations
                            "list_collections": "List Collections",
                            "create_collection": "Create Collection",
                            "add_to_collection": "Add to Collection",
                            
                            # Discount Operations
                            "create_discount": "Create Discount",
                            "list_discounts": "List Discounts",
                            
                            # Webhook Operations
                            "create_webhook": "Create Webhook",
                            "list_webhooks": "List Webhooks",
                            
                            # Analytics Operations
                            "get_shop_analytics": "Get Shop Analytics",
                            "get_product_analytics": "Get Product Analytics"
                        },
                        "default": "list_products"
                    },
                    "resource_id": {
                        "name": "Resource ID",
                        "type": "Text",
                        "description": "ID of the resource to operate on",
                        "required": False
                    },
                    "data": {
                        "name": "Data",
                        "type": "Key-Value",
                        "description": "Data for create/update operations",
                        "default": "{}",
                        "required": False
                    },
                    "filters": {
                        "name": "Filters",
                        "type": "Key-Value",
                        "description": "Filters for list operations",
                        "default": "{}",
                        "required": False
                    },
                    "page_size": {
                        "name": "Page Size",
                        "type": "Text",
                        "description": "Number of items per page",
                        "default": "50",
                        "required": False
                    },
                    "webhook_url": {
                        "name": "Webhook URL",
                        "type": "Text",
                        "description": "URL for webhook notifications",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation completed successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "An error occurred during the operation.",
                        "style": "error",
                    },
                    "auth_error": {
                        "name": "Authentication Error",
                        "description": "Authentication failed.",
                        "style": "error",
                    },
                    "rate_limit": {
                        "name": "Rate Limit",
                        "description": "Rate limit exceeded.",
                        "style": "error",
                    }
                },
            }
        ))

    @sleep_and_retry
    @limits(calls=CALLS_PER_SECOND, period=1)
    def _make_api_call(self, func, *args, **kwargs):
        """Make rate-limited API call"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e):
                self.outcome = "rate_limit"
                raise RuntimeError("Rate limit exceeded")
            raise e

    def _initialize_session(self, shop_url: str, access_token: str, api_version: str):
        """Initialize Shopify session"""
        try:
            shop_url = self._format_shop_url(shop_url)
            shopify.Session.setup(api_key=access_token, secret=None)
            session = shopify.Session(shop_url, api_version, access_token)
            shopify.ShopifyResource.activate_session(session)
            self.session = session
        except Exception as e:
            self.outcome = "auth_error"
            raise RuntimeError(f"Authentication failed: {str(e)}")

    def _format_shop_url(self, shop_url: str) -> str:
        """Format shop URL to standard format"""
        parsed = urlparse(shop_url)
        return parsed.netloc if parsed.netloc else parsed.path

    def _handle_product_operations(self, operation: str, data: Dict[str, Any] = None, 
                                 resource_id: str = None) -> Dict[str, Any]:
        """Handle product-related operations"""
        try:
            if operation == "list_products":
                products = self._make_api_call(shopify.Product.find, **data)
                return {
                    "products": [{
                        "id": p.id,
                        "title": p.title,
                        "handle": p.handle,
                        "variants": [vars(v) for v in p.variants],
                        "images": [vars(i) for i in p.images]
                    } for p in products]
                }
            
            elif operation == "create_product":
                product = self._make_api_call(shopify.Product.create, data)
                return vars(product)
            
            elif operation == "update_product":
                product = shopify.Product.find(resource_id)
                for key, value in data.items():
                    setattr(product, key, value)
                self._make_api_call(product.save)
                return vars(product)
            
            elif operation == "delete_product":
                product = shopify.Product.find(resource_id)
                self._make_api_call(product.destroy)
                return {"status": "deleted", "id": resource_id}
                
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Product operation error: {str(e)}")

    def _handle_order_operations(self, operation: str, data: Dict[str, Any] = None, 
                               resource_id: str = None) -> Dict[str, Any]:
        """Handle order-related operations"""
        try:
            if operation == "list_orders":
                orders = self._make_api_call(shopify.Order.find, **data)
                return {
                    "orders": [{
                        "id": o.id,
                        "order_number": o.order_number,
                        "total_price": o.total_price,
                        "customer": vars(o.customer) if o.customer else None,
                        "line_items": [vars(item) for item in o.line_items]
                    } for o in orders]
                }
            
            elif operation == "create_order":
                order = self._make_api_call(shopify.Order.create, data)
                return vars(order)
            
            elif operation == "update_order":
                order = shopify.Order.find(resource_id)
                for key, value in data.items():
                    setattr(order, key, value)
                self._make_api_call(order.save)
                return vars(order)
            
            elif operation == "cancel_order":
                order = shopify.Order.find(resource_id)
                self._make_api_call(order.cancel)
                return {"status": "cancelled", "id": resource_id}
                
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Order operation error: {str(e)}")

    def _handle_customer_operations(self, operation: str, data: Dict[str, Any] = None, 
                                  resource_id: str = None) -> Dict[str, Any]:
        """Handle customer-related operations"""
        try:
            if operation == "list_customers":
                customers = self._make_api_call(shopify.Customer.find, **data)
                return {
                    "customers": [{
                        "id": c.id,
                        "email": c.email,
                        "first_name": c.first_name,
                        "last_name": c.last_name,
                        "orders_count": c.orders_count,
                        "total_spent": c.total_spent
                    } for c in customers]
                }
            
            elif operation == "create_customer":
                customer = self._make_api_call(shopify.Customer.create, data)
                return vars(customer)
            
            elif operation == "update_customer":
                customer = shopify.Customer.find(resource_id)
                for key, value in data.items():
                    setattr(customer, key, value)
                self._make_api_call(customer.save)
                return vars(customer)
                
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Customer operation error: {str(e)}")

    def _handle_inventory_operations(self, operation: str, data: Dict[str, Any] = None,
                                   resource_id: str = None) -> Dict[str, Any]:
        """Handle inventory-related operations"""
        try:
            if operation == "list_inventory":
                locations = self._make_api_call(shopify.Location.find)
                inventory_levels = []
                for location in locations:
                    levels = self._make_api_call(
                        shopify.InventoryLevel.find,
                        location_id=location.id
                    )
                    inventory_levels.extend([{
                        "location_id": level.location_id,
                        "inventory_item_id": level.inventory_item_id,
                        "available": level.available
                    } for level in levels])
                return {"inventory_levels": inventory_levels}
            
            elif operation == "adjust_inventory":
                self._make_api_call(
                    shopify.InventoryLevel.adjust,
                    location_id=data['location_id'],
                    inventory_item_id=data['inventory_item_id'],
                    available_adjustment=data['adjustment']
                )
                return {"status": "adjusted", "data": data}
                
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Inventory operation error: {str(e)}")

    def run(self):
        try:
            # Get authentication fields
            shop_url = self._get_field("shop_url")
            access_token = self._get_field("access_token")
            api_version = self._get_field("api_version", False, "2024-01")

            # Initialize session
            self._initialize_session(shop_url, access_token, api_version)

            # Get operation details
            operation = self._get_field("operation")
            resource_id = self._get_field("resource_id", True)
            data = json.loads(self._get_field("data", True, "{}"))
            filters = json.loads(self._get_field("filters", True, "{}"))
            page_size = int(self._get_field("page_size", True, "50"))

            # Add pagination to filters if applicable
            if filters:
                filters['limit'] = page_size

            # Execute requested operation
            if operation.startswith("list_") or operation == "get_product":
                data.update(filters)

            if operation in ["list_products", "get_product", "create_product", 
                           "update_product", "delete_product"]:
                result = self._handle_product_operations(operation, data, resource_id)
            
            elif operation in ["list_orders", "get_order", "create_order", 
                             "update_order", "cancel_order"]:
                result = self._handle_order_operations(operation, data, resource_id)
            
            elif operation in ["list_customers", "get_customer", "create_customer", 
                             "update_customer"]:
                result = self._handle_customer_operations(operation, data, resource_id)
            
            elif operation in ["list_inventory", "adjust_inventory", "get_inventory_level"]:
                result = self._handle_inventory_operations(operation, data, resource_id)
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Store result and set success outcome
            self.result = {
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "data": result
            }
            self.outcome = "success"

        except ValueError as e:
            self.outcome = "error"
            raise RuntimeError(f"Validation error: {str(e)}")
        except Exception as e:
            if not self.outcome:
                self.outcome = "error"
            raise RuntimeError(f"Operation error: {str(e)}")

        finally:
            if self.session:
                shopify.ShopifyResource.clear_session()

