#!/usr/bin/env python3
"""
Product Manager API Lab

Models a small REST API for a product catalog and demonstrates:
- HTTP-style requests and responses
- REST endpoint design
- authentication
- validation
- status codes
- pagination and filtering
- optimistic concurrency with ETags
- rate limiting
- API documentation generated from endpoint metadata
- failure handling
- product-manager-oriented API evaluation
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import secrets
import time
from typing import Any, Callable


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    price: float
    active: bool
    version: int
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class APIRequest:
    method: HTTPMethod
    path: str
    headers: dict[str, str]
    body: dict[str, Any] | None = None
    query: dict[str, str] | None = None


@dataclass
class APIResponse:
    status: int
    headers: dict[str, str]
    body: dict[str, Any] | list[Any] | None

    def display(self) -> None:
        print(f"HTTP {self.status}")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        print(json.dumps(self.body, indent=2))
        print()


class AuthenticationError(Exception):
    pass


class ValidationError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class RateLimitError(Exception):
    pass


class ProductAPI:
    """
    In-memory REST service.

    The class deliberately separates:
    - authentication
    - resource validation
    - business operations
    - HTTP-like request routing

    A production implementation would persist products in a database and
    delegate authentication to an identity provider.
    """

    def __init__(self) -> None:
        self.products: dict[int, Product] = {
            1: Product(
                1, "Analytics Pro", "analytics", 49.99, True, 1, utc_now()
            ),
            2: Product(
                2, "Team Workspace", "collaboration", 19.99, True, 1, utc_now()
            ),
            3: Product(
                3, "Legacy Reports", "analytics", 9.99, False, 3, utc_now()
            ),
        }

        self.next_id = 4

        # Demo credentials only. Production systems should never store
        # plaintext API secrets in application source code.
        self.api_keys = {
            "pm-demo-key": "product-manager",
            "admin-demo-key": "administrator",
        }

        self.rate_limit_window = 60
        self.rate_limit_max = 5
        self.request_log: dict[str, list[float]] = {}

    def authenticate(self, request: APIRequest) -> str:
        authorization = request.headers.get("Authorization", "")

        if not authorization.startswith("Bearer "):
            raise AuthenticationError("Bearer authentication is required")

        token = authorization.removeprefix("Bearer ").strip()

        if token not in self.api_keys:
            raise AuthenticationError("Invalid API token")

        return self.api_keys[token]

    def check_rate_limit(self, token: str) -> None:
        now = time.time()
        timestamps = self.request_log.setdefault(token, [])

        timestamps[:] = [
            timestamp
            for timestamp in timestamps
            if now - timestamp < self.rate_limit_window
        ]

        if len(timestamps) >= self.rate_limit_max:
            raise RateLimitError("Rate limit exceeded")

        timestamps.append(now)

    @staticmethod
    def validate_product_payload(
        payload: dict[str, Any],
        partial: bool = False,
    ) -> None:
        allowed = {"name", "category", "price", "active"}

        unknown = set(payload) - allowed
        if unknown:
            raise ValidationError(
                f"Unknown fields: {sorted(unknown)}"
            )

        required = {"name", "category", "price"}
        if not partial:
            missing = required - set(payload)
            if missing:
                raise ValidationError(
                    f"Missing required fields: {sorted(missing)}"
                )

        if "name" in payload:
            if not isinstance(payload["name"], str) or not payload["name"].strip():
                raise ValidationError("name must be a non-empty string")

        if "category" in payload:
            if not isinstance(payload["category"], str) or not payload["category"].strip():
                raise ValidationError("category must be a non-empty string")

        if "price" in payload:
            price = payload["price"]
            if not isinstance(price, (int, float)) or isinstance(price, bool):
                raise ValidationError("price must be numeric")
            if price < 0:
                raise ValidationError("price cannot be negative")

        if "active" in payload and not isinstance(payload["active"], bool):
            raise ValidationError("active must be boolean")

    @staticmethod
    def etag(product: Product) -> str:
        payload = f"{product.product_id}:{product.version}:{product.updated_at}"
        digest = hashlib.sha256(payload.encode()).hexdigest()
        return f'"{digest[:16]}"'

    def list_products(self, request: APIRequest) -> APIResponse:
        query = request.query or {}

        category = query.get("category")
        active = query.get("active")
        try:
            limit = min(max(int(query.get("limit", "10")), 1), 50)
            offset = max(int(query.get("offset", "0")), 0)
        except ValueError as exc:
            raise ValidationError("limit and offset must be integers") from exc

        products = list(self.products.values())

        if category:
            products = [
                product for product in products
                if product.category.lower() == category.lower()
            ]

        if active is not None:
            if active.lower() not in {"true", "false"}:
                raise ValidationError("active must be true or false")
            requested_active = active.lower() == "true"
            products = [
                product for product in products
                if product.active == requested_active
            ]

        selected = products[offset:offset + limit]

        return APIResponse(
            status=200,
            headers={
                "Content-Type": "application/json",
                "X-Total-Count": str(len(products)),
            },
            body={
                "items": [product.to_dict() for product in selected],
                "limit": limit,
                "offset": offset,
                "total": len(products),
            },
        )

    def get_product(self, product_id: int) -> APIResponse:
        product = self.products.get(product_id)

        if product is None:
            raise NotFoundError("Product not found")

        return APIResponse(
            status=200,
            headers={
                "Content-Type": "application/json",
                "ETag": self.etag(product),
            },
            body=product.to_dict(),
        )

    def create_product(self, payload: dict[str, Any]) -> APIResponse:
        self.validate_product_payload(payload)

        product = Product(
            product_id=self.next_id,
            name=payload["name"].strip(),
            category=payload["category"].strip().lower(),
            price=float(payload["price"]),
            active=payload.get("active", True),
            version=1,
            updated_at=utc_now(),
        )

        self.products[product.product_id] = product
        self.next_id += 1

        return APIResponse(
            status=201,
            headers={
                "Content-Type": "application/json",
                "Location": f"/api/v1/products/{product.product_id}",
                "ETag": self.etag(product),
            },
            body=product.to_dict(),
        )

    def update_product(
        self,
        product_id: int,
        payload: dict[str, Any],
        request: APIRequest,
    ) -> APIResponse:
        self.validate_product_payload(payload, partial=True)

        product = self.products.get(product_id)
        if product is None:
            raise NotFoundError("Product not found")

        supplied_etag = request.headers.get("If-Match")
        current_etag = self.etag(product)

        # If-Match prevents a stale client from silently overwriting a
        # newer version of the resource.
        if supplied_etag != current_etag:
            raise ConflictError(
                "Resource changed since it was retrieved; refresh and retry"
            )

        for field in ("name", "category", "price", "active"):
            if field in payload:
                value = payload[field]
                if field in {"name", "category"}:
                    value = value.strip()
                if field == "category":
                    value = value.lower()
                if field == "price":
                    value = float(value)
                setattr(product, field, value)

        product.version += 1
        product.updated_at = utc_now()

        return APIResponse(
            status=200,
            headers={
                "Content-Type": "application/json",
                "ETag": self.etag(product),
            },
            body=product.to_dict(),
        )

    def delete_product(self, product_id: int) -> APIResponse:
        if product_id not in self.products:
            raise NotFoundError("Product not found")

        del self.products[product_id]

        return APIResponse(
            status=204,
            headers={},
            body=None,
        )

    def dispatch(self, request: APIRequest) -> APIResponse:
        try:
            role = self.authenticate(request)

            token = request.headers["Authorization"].removeprefix("Bearer ").strip()
            self.check_rate_limit(token)

            segments = [
                segment for segment in request.path.split("/") if segment
            ]

            if segments[:2] != ["api", "v1"]:
                raise NotFoundError("API version or path not found")

            if len(segments) == 3 and segments[2] == "products":
                if request.method == HTTPMethod.GET:
                    return self.list_products(request)

                if request.method == HTTPMethod.POST:
                    if role not in {"product-manager", "administrator"}:
                        return APIResponse(
                            403,
                            {"Content-Type": "application/json"},
                            {"error": "Insufficient permissions"},
                        )
                    return self.create_product(request.body or {})

            if len(segments) == 4 and segments[2] == "products":
                try:
                    product_id = int(segments[3])
                except ValueError as exc:
                    raise ValidationError("Product ID must be numeric") from exc

                if request.method == HTTPMethod.GET:
                    return self.get_product(product_id)

                if request.method == HTTPMethod.PATCH:
                    if role not in {"product-manager", "administrator"}:
                        return APIResponse(
                            403,
                            {"Content-Type": "application/json"},
                            {"error": "Insufficient permissions"},
                        )
                    return self.update_product(
                        product_id,
                        request.body or {},
                        request,
                    )

                if request.method == HTTPMethod.DELETE:
                    if role != "administrator":
                        return APIResponse(
                            403,
                            {"Content-Type": "application/json"},
                            {"error": "Administrator role required"},
                        )
                    return self.delete_product(product_id)

            return APIResponse(
                405,
                {"Content-Type": "application/json"},
                {"error": "Method or endpoint not supported"},
            )

        except AuthenticationError as exc:
            return APIResponse(
                401,
                {"Content-Type": "application/json"},
                {"error": str(exc)},
            )
        except ValidationError as exc:
            return APIResponse(
                400,
                {"Content-Type": "application/json"},
                {"error": str(exc)},
            )
        except NotFoundError as exc:
            return APIResponse(
                404,
                {"Content-Type": "application/json"},
                {"error": str(exc)},
            )
        except ConflictError as exc:
            return APIResponse(
                409,
                {"Content-Type": "application/json"},
                {"error": str(exc)},
            )
        except RateLimitError as exc:
            return APIResponse(
                429,
                {"Content-Type": "application/json"},
                {
                    "error": str(exc),
                    "retry_after_seconds": self.rate_limit_window,
                },
            )
        except Exception:
            # A production API should log the exception internally but
            # avoid returning implementation details to clients.
            return APIResponse(
                500,
                {"Content-Type": "application/json"},
                {"error": "Internal server error"},
            )


ENDPOINTS = [
    {
        "method": "GET",
        "path": "/api/v1/products",
        "purpose": "List products with optional filtering and pagination",
        "success": 200,
    },
    {
        "method": "GET",
        "path": "/api/v1/products/{id}",
        "purpose": "Retrieve one product",
        "success": 200,
    },
    {
        "method": "POST",
        "path": "/api/v1/products",
        "purpose": "Create a product",
        "success": 201,
    },
    {
        "method": "PATCH",
        "path": "/api/v1/products/{id}",
        "purpose": "Partially update a product using optimistic concurrency",
        "success": 200,
    },
    {
        "method": "DELETE",
        "path": "/api/v1/products/{id}",
        "purpose": "Delete a product",
        "success": 204,
    },
]


def generate_api_documentation() -> str:
    lines = [
        "# Product Catalog API",
        "",
        "Authentication: `Authorization: Bearer <API key>`",
        "",
        "| Method | Endpoint | Purpose | Success |",
        "|---|---|---|---|",
    ]

    for endpoint in ENDPOINTS:
        lines.append(
            f"| `{endpoint['method']}` | `{endpoint['path']}` | "
            f"{endpoint['purpose']} | `{endpoint['success']}` |"
        )

    return "\n".join(lines)


def run_demo() -> None:
    api = ProductAPI()
    auth = {"Authorization": "Bearer pm-demo-key"}

    print("=== Product list ===")
    api.dispatch(
        APIRequest(
            HTTPMethod.GET,
            "/api/v1/products",
            auth,
            query={"category": "analytics", "limit": "2"},
        )
    ).display()

    print("=== Create product ===")
    created = api.dispatch(
        APIRequest(
            HTTPMethod.POST,
            "/api/v1/products",
            auth,
            body={
                "name": "Customer Insights",
                "category": "analytics",
                "price": 79.0,
            },
        )
    )
    created.display()

    product_id = created.body["product_id"]
    etag = created.headers["ETag"]

    print("=== Update product with ETag ===")
    api.dispatch(
        APIRequest(
            HTTPMethod.PATCH,
            f"/api/v1/products/{product_id}",
            auth | {"If-Match": etag},
            body={"price": 89.0},
        )
    ).display()

    print("=== Invalid request ===")
    api.dispatch(
        APIRequest(
            HTTPMethod.POST,
            "/api/v1/products",
            auth,
            body={"name": "", "price": -10},
        )
    ).display()

    print("=== Missing resource ===")
    api.dispatch(
        APIRequest(
            HTTPMethod.GET,
            "/api/v1/products/9999",
            auth,
        )
    ).display()

    print("=== API documentation ===")
    print(generate_api_documentation())


if __name__ == "__main__":
    run_demo()
