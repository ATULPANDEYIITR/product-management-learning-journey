#!/usr/bin/env python3
"""
Technical Architecture simulator.

Models the relationship between:
- Monoliths
- Microservices
- Service boundaries
- Databases
- Caching
- Queues
- Horizontal scalability

The implementation is intentionally self-contained and uses only the Python
standard library. It simulates request routing, cache behavior, synchronous
service calls, asynchronous queue processing, database access, failures,
retries, and scaling decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import random
import time
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Tuple


class ArchitectureStyle(Enum):
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass(frozen=True)
class Request:
    request_id: str
    operation: str
    customer_id: int
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    request_id: str
    success: bool
    data: Dict[str, Any]
    latency_ms: float
    error: Optional[str] = None


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class Cache:
    """Simple TTL cache.

    A bounded cache avoids unbounded memory growth. Expired entries are removed
    lazily when accessed. Production systems usually need distributed cache
    consistency rules, eviction policies, metrics, and serialization limits.
    """

    def __init__(self, capacity: int = 100, ttl_seconds: float = 30.0):
        if capacity <= 0:
            raise ValueError("Cache capacity must be positive")
        if ttl_seconds <= 0:
            raise ValueError("Cache TTL must be positive")

        self.capacity = capacity
        self.ttl_seconds = ttl_seconds
        self._entries: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._entries.get(key)

        if entry is None:
            self.misses += 1
            return None

        if entry.expires_at <= time.monotonic():
            del self._entries[key]
            self.misses += 1
            return None

        self.hits += 1
        return entry.value

    def put(self, key: str, value: Any) -> None:
        if key not in self._entries and len(self._entries) >= self.capacity:
            # Deterministic FIFO eviction keeps this simulation simple.
            oldest_key = next(iter(self._entries))
            del self._entries[oldest_key]

        self._entries[key] = CacheEntry(
            value=value,
            expires_at=time.monotonic() + self.ttl_seconds,
        )

    def invalidate(self, key: str) -> None:
        self._entries.pop(key, None)

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


class Database:
    """In-memory database with a small transaction abstraction."""

    def __init__(self, name: str):
        self.name = name
        self._tables: Dict[str, Dict[Any, Dict[str, Any]]] = defaultdict(dict)
        self.reads = 0
        self.writes = 0
        self.fail_reads = False
        self.fail_writes = False

    def insert(self, table: str, key: Any, row: Dict[str, Any]) -> None:
        if self.fail_writes:
            raise RuntimeError(f"Database {self.name} write failure")
        if key in self._tables[table]:
            raise ValueError(f"Duplicate key {key} in {table}")
        self._tables[table][key] = dict(row)
        self.writes += 1

    def update(self, table: str, key: Any, updates: Dict[str, Any]) -> None:
        if self.fail_writes:
            raise RuntimeError(f"Database {self.name} write failure")
        if key not in self._tables[table]:
            raise KeyError(f"Unknown key {key} in {table}")
        self._tables[table][key].update(updates)
        self.writes += 1

    def get(self, table: str, key: Any) -> Optional[Dict[str, Any]]:
        if self.fail_reads:
            raise RuntimeError(f"Database {self.name} read failure")
        self.reads += 1
        row = self._tables[table].get(key)
        return dict(row) if row else None

    def all(self, table: str) -> List[Dict[str, Any]]:
        if self.fail_reads:
            raise RuntimeError(f"Database {self.name} read failure")
        self.reads += len(self._tables[table])
        return [dict(row) for row in self._tables[table].values()]


class MessageQueue:
    """At-least-once-style queue simulation.

    Messages remain queued until acknowledged. A real broker would persist
    messages and track visibility, consumer groups, retries, and dead letters.
    """

    def __init__(self, name: str, max_retries: int = 3):
        if max_retries < 1:
            raise ValueError("max_retries must be at least one")

        self.name = name
        self.max_retries = max_retries
        self._messages: Deque[Tuple[Dict[str, Any], int]] = deque()
        self.dead_letters: List[Dict[str, Any]] = []
        self.published = 0
        self.processed = 0

    def publish(self, message: Dict[str, Any]) -> None:
        self._messages.append((dict(message), 0))
        self.published += 1

    def consume(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        while self._messages:
            message, retries = self._messages.popleft()

            try:
                handler(message)
                self.processed += 1
            except Exception as exc:
                retries += 1
                if retries >= self.max_retries:
                    message["failure"] = str(exc)
                    self.dead_letters.append(message)
                else:
                    self._messages.append((message, retries))


class Service:
    def __init__(self, name: str, database: Database):
        self.name = name
        self.database = database
        self.status = ServiceStatus.HEALTHY
        self.requests = 0
        self.failures = 0

    def ensure_available(self) -> None:
        if self.status == ServiceStatus.DOWN:
            self.failures += 1
            raise RuntimeError(f"Service {self.name} is unavailable")

    def set_status(self, status: ServiceStatus) -> None:
        self.status = status


class CustomerService(Service):
    def __init__(self, database: Database, cache: Cache):
        super().__init__("customer-service", database)
        self.cache = cache

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        self.requests += 1
        self.ensure_available()

        key = f"customer:{customer_id}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        customer = self.database.get("customers", customer_id)
        if customer is None:
            raise KeyError(f"Customer {customer_id} does not exist")

        self.cache.put(key, customer)
        return customer

    def change_tier(self, customer_id: int, tier: str) -> None:
        allowed = {"standard", "premium", "enterprise"}
        if tier not in allowed:
            raise ValueError(f"Invalid tier: {tier}")

        self.requests += 1
        self.ensure_available()
        self.database.update("customers", customer_id, {"tier": tier})
        self.cache.invalidate(f"customer:{customer_id}")


class OrderService(Service):
    def __init__(self, database: Database, queue: MessageQueue):
        super().__init__("order-service", database)
        self.queue = queue

    def create_order(
        self,
        customer_id: int,
        amount: float,
        customer_service: CustomerService,
    ) -> int:
        if amount <= 0:
            raise ValueError("Order amount must be positive")

        self.requests += 1
        self.ensure_available()

        # The service boundary requires customer validation before persistence.
        customer_service.get_customer(customer_id)

        existing = self.database.all("orders")
        next_id = max((row["id"] for row in existing), default=0) + 1

        self.database.insert(
            "orders",
            next_id,
            {
                "id": next_id,
                "customer_id": customer_id,
                "amount": round(amount, 2),
                "status": "created",
            },
        )

        self.queue.publish(
            {
                "event": "order.created",
                "order_id": next_id,
                "customer_id": customer_id,
                "amount": round(amount, 2),
            }
        )
        return next_id


class Monolith:
    """Single deployable boundary containing customer and order behavior."""

    def __init__(self):
        self.database = Database("monolith-db")
        self.cache = Cache(capacity=100, ttl_seconds=60)
        self.queue = MessageQueue("monolith-events")
        self.customers = CustomerService(self.database, self.cache)
        self.orders = OrderService(self.database, self.queue)

    def seed(self) -> None:
        self.database.insert(
            "customers",
            1,
            {"id": 1, "name": "Asha", "tier": "premium"},
        )
        self.database.insert(
            "customers",
            2,
            {"id": 2, "name": "Ravi", "tier": "standard"},
        )

    def place_order(self, request: Request) -> Response:
        started = time.perf_counter()

        try:
            order_id = self.orders.create_order(
                request.customer_id,
                float(request.payload["amount"]),
                self.customers,
            )
            return Response(
                request.request_id,
                True,
                {"order_id": order_id, "architecture": "monolith"},
                (time.perf_counter() - started) * 1000,
            )
        except (KeyError, ValueError, RuntimeError) as exc:
            return Response(
                request.request_id,
                False,
                {},
                (time.perf_counter() - started) * 1000,
                str(exc),
            )


class MicroservicesPlatform:
    """Separate deployable service boundaries sharing no application database."""

    def __init__(self):
        self.customer_db = Database("customer-db")
        self.order_db = Database("order-db")
        self.customer_cache = Cache(capacity=100, ttl_seconds=60)
        self.events = MessageQueue("order-events")
        self.customers = CustomerService(self.customer_db, self.customer_cache)
        self.orders = OrderService(self.order_db, self.events)

    def seed(self) -> None:
        self.customer_db.insert(
            "customers",
            1,
            {"id": 1, "name": "Asha", "tier": "premium"},
        )
        self.customer_db.insert(
            "customers",
            2,
            {"id": 2, "name": "Ravi", "tier": "standard"},
        )

    def place_order(self, request: Request) -> Response:
        started = time.perf_counter()

        try:
            order_id = self.orders.create_order(
                request.customer_id,
                float(request.payload["amount"]),
                self.customers,
            )
            return Response(
                request.request_id,
                True,
                {"order_id": order_id, "architecture": "microservices"},
                (time.perf_counter() - started) * 1000,
            )
        except (KeyError, ValueError, RuntimeError) as exc:
            return Response(
                request.request_id,
                False,
                {},
                (time.perf_counter() - started) * 1000,
                str(exc),
            )

    def process_events(self) -> None:
        def handle_event(event: Dict[str, Any]) -> None:
            if event["event"] != "order.created":
                raise ValueError("Unsupported event")
            # A real consumer could trigger email, billing, fulfillment, etc.
            print(
                f"  async consumer processed order {event['order_id']} "
                f"for customer {event['customer_id']}"
            )

        self.events.consume(handle_event)


def simulate_scaling(service_count: int, requests_per_second: int) -> Dict[str, int]:
    """Simple capacity calculation.

    Each service instance is assumed to safely handle 50 requests/second.
    This is a planning model, not a benchmark.
    """
    if service_count < 1 or requests_per_second < 0:
        raise ValueError("Invalid scaling inputs")

    capacity_per_instance = 50
    required_instances = max(
        1,
        (requests_per_second + capacity_per_instance - 1)
        // capacity_per_instance,
    )
    return {
        "instances": required_instances,
        "nominal_capacity_rps": required_instances * capacity_per_instance,
    }


def demonstrate_cache() -> None:
    cache = Cache(capacity=2, ttl_seconds=60)
    cache.put("customer:1", {"name": "Asha"})
    cache.put("customer:2", {"name": "Ravi"})

    print("Cache first read:", cache.get("customer:1"))
    print("Cache second read:", cache.get("customer:1"))

    cache.put("customer:3", {"name": "Meera"})
    print("Evicted entry:", cache.get("customer:2"))
    print("Cache hit ratio:", round(cache.hit_ratio, 2))


def demonstrate_queue_failure() -> None:
    queue = MessageQueue("payment-events", max_retries=2)
    queue.publish({"event": "payment.capture", "payment_id": 101})

    attempts = {"count": 0}

    def failing_consumer(message: Dict[str, Any]) -> None:
        attempts["count"] += 1
        raise RuntimeError("Payment provider timeout")

    queue.consume(failing_consumer)

    print("Queue retry attempts:", attempts["count"])
    print("Dead-letter messages:", len(queue.dead_letters))


def run_demo() -> None:
    request = Request(
        request_id="req-1001",
        operation="create-order",
        customer_id=1,
        payload={"amount": 2499.50},
    )

    monolith = Monolith()
    monolith.seed()

    print("Monolith response:")
    print(monolith.place_order(request))

    microservices = MicroservicesPlatform()
    microservices.seed()

    print("\nMicroservices response:")
    print(microservices.place_order(request))

    print("\nProcessing asynchronous events:")
    microservices.process_events()

    print("\nCache behavior:")
    demonstrate_cache()

    print("\nQueue failure and dead-letter behavior:")
    demonstrate_queue_failure()

    print("\nScaling calculation:")
    for rps in (20, 50, 51, 150, 501):
        print(rps, "RPS ->", simulate_scaling(1, rps))

    print("\nFailure isolation:")
    microservices.customers.set_status(ServiceStatus.DOWN)
    failure_response = microservices.place_order(
        Request(
            request_id="req-1002",
            operation="create-order",
            customer_id=1,
            payload={"amount": 500},
        )
    )
    print(failure_response)

    print("\nDatabase statistics:")
    print(
        {
            "customer_db_reads": microservices.customer_db.reads,
            "customer_db_writes": microservices.customer_db.writes,
            "order_db_reads": microservices.order_db.reads,
            "order_db_writes": microservices.order_db.writes,
        }
    )


if __name__ == "__main__":
    run_demo()
