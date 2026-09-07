"""
PRODUCT TYPES: A PRACTICAL PYTHON STUDY GUIDE

Topic coverage:
- B2B products
- B2C products
- B2B2C products
- SaaS products
- Marketplaces
- Platforms
- APIs as products
- Consumer applications
- Enterprise products
- Product discovery and company databases
- Product Hunt and Crunchbase as examples of product-information ecosystems

This script models product types using Python so that business and product
management concepts can be studied through executable examples.

The script uses only the Python standard library.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Callable, Dict, List, Optional, Set, Tuple
import json
import random


# ============================================================================
# 1. FUNDAMENTAL PRODUCT CONCEPTS
# ============================================================================

print("=" * 80)
print("1. FUNDAMENTAL PRODUCT CONCEPTS")
print("=" * 80)

print(
    """
A product is a solution designed to create value for one or more groups of
users or customers.

A product can be:
- Physical: a smartphone, machine, vehicle
- Digital: a mobile application, website, SaaS product
- Service-based: consulting software, cloud infrastructure
- Infrastructure: APIs, payment systems, developer platforms
- Multi-sided: marketplaces and platforms connecting different user groups

The same company can operate multiple product types simultaneously.
For example:
- A company can sell SaaS software to businesses.
- The same software can expose APIs.
- It can include a marketplace.
- It can provide a consumer application.

Product classification depends heavily on:
1. Who pays.
2. Who uses the product.
3. Who receives value.
4. How the product reaches users.
5. How the business earns revenue.
"""
)


class CustomerType(Enum):
    """Primary economic customer categories."""

    BUSINESS = "Business"
    CONSUMER = "Consumer"
    BUSINESS_AND_CONSUMER = "Business and Consumer"
    DEVELOPER = "Developer"
    GOVERNMENT = "Government"


class RevenueModel(Enum):
    """Common product monetization models."""

    SUBSCRIPTION = "Subscription"
    TRANSACTION_FEE = "Transaction Fee"
    COMMISSION = "Commission"
    LICENSING = "Licensing"
    USAGE_BASED = "Usage Based"
    ADVERTISING = "Advertising"
    FREEMIUM = "Freemium"
    ONE_TIME_PURCHASE = "One-Time Purchase"
    ENTERPRISE_CONTRACT = "Enterprise Contract"


class DistributionModel(Enum):
    """How a product reaches its users."""

    DIRECT = "Direct"
    SALES_LED = "Sales-Led"
    SELF_SERVICE = "Self-Service"
    PARTNER_LED = "Partner-Led"
    APP_STORE = "App Store"
    API_DISTRIBUTION = "API Distribution"
    MARKETPLACE = "Marketplace"


@dataclass
class Product:
    """
    Base representation of a product.

    A product is described independently from its implementation technology.
    This is important because product classification is primarily a business
    and value-delivery concept, not merely a technical concept.
    """

    name: str
    description: str
    customer_types: Set[CustomerType]
    revenue_models: Set[RevenueModel]
    distribution_models: Set[DistributionModel]
    target_users: List[str]
    price_per_month: float = 0.0

    def annual_recurring_revenue_per_customer(self) -> float:
        """
        Simplified annual recurring revenue calculation.

        This works primarily for recurring subscription products.
        """
        return self.price_per_month * 12

    def describe(self) -> None:
        print(f"\nProduct: {self.name}")
        print(f"Description: {self.description}")
        print("Customers:", ", ".join(customer.value for customer in self.customer_types))
        print("Revenue Models:", ", ".join(model.value for model in self.revenue_models))
        print(
            "Distribution:",
            ", ".join(model.value for model in self.distribution_models),
        )
        print("Target Users:", ", ".join(self.target_users))


# ============================================================================
# 2. B2B PRODUCTS
# ============================================================================

print("\n" + "=" * 80)
print("2. B2B PRODUCTS")
print("=" * 80)

print(
    """
B2B means Business-to-Business.

A B2B product is sold primarily to an organization rather than directly to an
individual consumer.

Important distinction:
- The buyer may be an organization.
- The end user may be an employee of that organization.
- The economic buyer and daily user may be different people.

Example:
A company purchases project management software.
- Economic buyer: Chief Technology Officer
- Decision maker: Engineering Manager
- Administrator: IT Administrator
- End users: Software engineers

This multi-stakeholder buying process is a major characteristic of B2B.
"""
)


@dataclass
class B2BProduct(Product):
    """A product whose primary customer is another organization."""

    sales_cycle_days: int = 30
    contract_value: float = 0.0
    requires_multiple_stakeholders: bool = True

    def estimate_sales_complexity(self) -> str:
        """
        Estimate sales complexity using simplified rules.

        Real B2B sales analysis would consider procurement, security review,
        legal review, integrations, implementation requirements, and company size.
        """
        if self.sales_cycle_days > 180 or self.contract_value >= 100_000:
            return "High complexity"
        if self.sales_cycle_days > 60 or self.contract_value >= 20_000:
            return "Medium complexity"
        return "Low complexity"


crm_product = B2BProduct(
    name="EnterpriseCRM",
    description="Customer relationship management software for sales organizations.",
    customer_types={CustomerType.BUSINESS},
    revenue_models={RevenueModel.SUBSCRIPTION, RevenueModel.ENTERPRISE_CONTRACT},
    distribution_models={DistributionModel.SALES_LED},
    target_users=["Sales Representatives", "Sales Managers", "Administrators"],
    price_per_month=5000,
    sales_cycle_days=120,
    contract_value=60_000,
)

crm_product.describe()
print("Sales Complexity:", crm_product.estimate_sales_complexity())
print(
    "Annual Recurring Revenue per Customer:",
    crm_product.annual_recurring_revenue_per_customer(),
)


# ============================================================================
# 3. B2C PRODUCTS
# ============================================================================

print("\n" + "=" * 80)
print("3. B2C PRODUCTS")
print("=" * 80)

print(
    """
B2C means Business-to-Consumer.

A B2C product is offered directly to individual consumers.

Examples include:
- Streaming applications
- Food delivery applications
- Consumer banking applications
- E-commerce applications
- Fitness applications
- Social networking applications

Typical B2C characteristics:
- Large user populations
- Lower price per customer than enterprise products
- Faster purchasing decisions
- Strong emphasis on user experience
- Marketing and brand can strongly affect growth
- Self-service onboarding is common

A B2C product can still have high complexity behind the interface. The user
experience should usually hide unnecessary operational complexity.
"""
)


@dataclass
class B2CProduct(Product):
    """A product primarily designed for individual consumers."""

    monthly_active_users: int = 0
    acquisition_cost_per_user: float = 0.0

    def estimated_monthly_revenue(self) -> float:
        return self.monthly_active_users * self.price_per_month

    def estimate_monthly_acquisition_cost(self, new_users: int) -> float:
        return new_users * self.acquisition_cost_per_user


fitness_app = B2CProduct(
    name="FitTrack",
    description="A consumer mobile application for fitness tracking.",
    customer_types={CustomerType.CONSUMER},
    revenue_models={RevenueModel.SUBSCRIPTION, RevenueModel.FREEMIUM},
    distribution_models={DistributionModel.APP_STORE, DistributionModel.SELF_SERVICE},
    target_users=["Individual Fitness Users"],
    price_per_month=9.99,
    monthly_active_users=100_000,
    acquisition_cost_per_user=4.50,
)

fitness_app.describe()
print("Estimated Monthly Revenue:", round(fitness_app.estimated_monthly_revenue(), 2))
print(
    "Cost to acquire 1,000 new users:",
    fitness_app.estimate_monthly_acquisition_cost(1000),
)


# ============================================================================
# 4. B2B VS B2C COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("4. B2B VS B2C")
print("=" * 80)

comparison = {
    "Primary Customer": {
        "B2B": "Organization",
        "B2C": "Individual consumer",
    },
    "Typical Buyer Count": {
        "B2B": "Often multiple stakeholders",
        "B2C": "Usually one individual",
    },
    "Sales Cycle": {
        "B2B": "Often longer",
        "B2C": "Usually shorter",
    },
    "Contract Value": {
        "B2B": "Often higher",
        "B2C": "Often lower per customer",
    },
    "Distribution": {
        "B2B": "Sales, partners, procurement",
        "B2C": "App stores, websites, advertising",
    },
    "Product Requirements": {
        "B2B": "Integrations, administration, controls",
        "B2C": "Usability, convenience, engagement",
    },
}

for category, values in comparison.items():
    print(f"\n{category}")
    for product_type, value in values.items():
        print(f"  {product_type}: {value}")


# ============================================================================
# 5. B2B2C PRODUCTS
# ============================================================================

print("\n" + "=" * 80)
print("5. B2B2C PRODUCTS")
print("=" * 80)

print(
    """
B2B2C means Business-to-Business-to-Consumer.

A company creates value for consumers but reaches them through another business.

Structure:

Product Company -> Partner Business -> Consumer

Example:
A payment technology company provides infrastructure to a bank.
The bank exposes the payment experience to its customers.

The technology company may earn money from the business partner, while the
consumer receives the final service.

B2B2C introduces an important product challenge:
the product must satisfy both the partner organization and the end consumer.
"""
)


@dataclass
class B2B2CProduct(Product):
    """A product delivered to consumers through a business intermediary."""

    partner_count: int = 0
    consumers_reached_per_partner: int = 0

    def estimated_consumer_reach(self) -> int:
        return self.partner_count * self.consumers_reached_per_partner


payment_network = B2B2CProduct(
    name="PaymentConnect",
    description="Payment infrastructure used by financial institutions.",
    customer_types={CustomerType.BUSINESS, CustomerType.CONSUMER},
    revenue_models={RevenueModel.TRANSACTION_FEE},
    distribution_models={DistributionModel.PARTNER_LED, DistributionModel.API_DISTRIBUTION},
    target_users=["Banks", "Merchants", "Consumers"],
    partner_count=50,
    consumers_reached_per_partner=200_000,
)

payment_network.describe()
print("Estimated Consumer Reach:", payment_network.estimated_consumer_reach())


# ============================================================================
# 6. SAAS PRODUCTS
# ============================================================================

print("\n" + "=" * 80)
print("6. SOFTWARE AS A SERVICE (SAAS)")
print("=" * 80)

print(
    """
SaaS means Software as a Service.

A SaaS product delivers software over a network, commonly through a browser
or application, and typically charges recurring fees.

SaaS can be:
- B2B SaaS
- B2C SaaS
- B2B2C SaaS

Examples of SaaS categories:
- Customer relationship management
- Human resources software
- Accounting software
- Project management software
- Communication software
- Cybersecurity software
- Analytics software

Important SaaS characteristics:
- Recurring revenue
- Centralized software updates
- Shared infrastructure
- Account management
- Authentication and authorization
- Usage measurement
- Customer retention requirements

A major business concept in SaaS is churn.
"""
)


@dataclass
class SaaSProduct(Product):
    """
    SaaS-specific product metrics.

    churn_rate is represented as a decimal.
    Example:
        0.05 means 5% monthly churn.
    """

    customer_count: int = 0
    monthly_churn_rate: float = 0.0

    def validate_churn_rate(self) -> None:
        if not 0 <= self.monthly_churn_rate <= 1:
            raise ValueError("Churn rate must be between 0 and 1.")

    def customers_after_one_month(self) -> int:
        self.validate_churn_rate()
        return round(self.customer_count * (1 - self.monthly_churn_rate))

    def monthly_recurring_revenue(self) -> float:
        return self.customer_count * self.price_per_month

    def annual_recurring_revenue(self) -> float:
        return self.monthly_recurring_revenue() * 12

    def simulate_customer_retention(self, months: int) -> List[int]:
        """
        Simulates customer decline without new customer acquisition.

        This demonstrates why retention is important for subscription businesses.
        """
        if months < 0:
            raise ValueError("Months cannot be negative.")

        self.validate_churn_rate()

        customers = self.customer_count
        history = [customers]

        for _ in range(months):
            customers = round(customers * (1 - self.monthly_churn_rate))
            history.append(customers)

        return history


analytics_saas = SaaSProduct(
    name="DataInsight",
    description="Cloud analytics software for business teams.",
    customer_types={CustomerType.BUSINESS},
    revenue_models={RevenueModel.SUBSCRIPTION},
    distribution_models={DistributionModel.SELF_SERVICE, DistributionModel.SALES_LED},
    target_users=["Analysts", "Managers", "Executives"],
    price_per_month=250,
    customer_count=500,
    monthly_churn_rate=0.03,
)

analytics_saas.describe()
print("Monthly Recurring Revenue:", analytics_saas.monthly_recurring_revenue())
print("Annual Recurring Revenue:", analytics_saas.annual_recurring_revenue())
print(
    "Customers After One Month:",
    analytics_saas.customers_after_one_month(),
)
print(
    "Retention Simulation:",
    analytics_saas.simulate_customer_retention(6),
)


# ============================================================================
# 7. MARKETPLACES
# ============================================================================

print("\n" + "=" * 80)
print("7. MARKETPLACES")
print("=" * 80)

print(
    """
A marketplace connects two or more groups so that transactions can occur.

Typical marketplace structure:

Sellers <-> Marketplace <-> Buyers

Examples:
- Buyers and sellers
- Freelancers and clients
- Drivers and riders
- Hosts and guests

The marketplace operator often does not own all inventory.

A marketplace must solve a difficult problem called the liquidity problem:
both sides of the market need enough active participants.

Without enough sellers:
buyers find limited choice.

Without enough buyers:
sellers receive limited demand.

This is often called the chicken-and-egg problem.
"""
)


@dataclass
class Marketplace(Product):
    """A simplified two-sided marketplace."""

    buyers: int = 0
    sellers: int = 0
    average_transaction_value: float = 0.0
    commission_rate: float = 0.0

    def validate_commission_rate(self) -> None:
        if not 0 <= self.commission_rate <= 1:
            raise ValueError("Commission rate must be between 0 and 1.")

    def estimate_gross_merchandise_value(
        self,
        transactions_per_buyer: float,
    ) -> float:
        """
        Gross Merchandise Value (GMV) estimates the total transaction value
        occurring through the marketplace.
        """
        if transactions_per_buyer < 0:
            raise ValueError("Transactions per buyer cannot be negative.")

        return (
            self.buyers
            * transactions_per_buyer
            * self.average_transaction_value
        )

    def estimate_marketplace_revenue(
        self,
        transactions_per_buyer: float,
    ) -> float:
        self.validate_commission_rate()

        gmv = self.estimate_gross_merchandise_value(transactions_per_buyer)

        return gmv * self.commission_rate

    def participant_balance(self) -> str:
        """
        Extremely simplified marketplace health indicator.

        Real marketplaces evaluate geography, category coverage,
        transaction frequency, matching success, supply quality,
        pricing, wait times, and repeat behavior.
        """
        if self.buyers == 0 and self.sellers == 0:
            return "No active marketplace"
        if self.sellers == 0:
            return "Demand exists but supply is missing"
        if self.buyers == 0:
            return "Supply exists but demand is missing"

        ratio = self.buyers / self.sellers

        if ratio < 2:
            return "Supply-heavy"
        if ratio > 100:
            return "Demand-heavy"
        return "Potentially balanced"


freelance_marketplace = Marketplace(
    name="TalentMarket",
    description="Marketplace connecting businesses with independent professionals.",
    customer_types={CustomerType.BUSINESS, CustomerType.CONSUMER},
    revenue_models={RevenueModel.COMMISSION, RevenueModel.TRANSACTION_FEE},
    distribution_models={DistributionModel.MARKETPLACE},
    target_users=["Clients", "Freelancers"],
    buyers=20_000,
    sellers=2_000,
    average_transaction_value=500,
    commission_rate=0.15,
)

freelance_marketplace.describe()
print("Participant Balance:", freelance_marketplace.participant_balance())
print(
    "Estimated GMV:",
    freelance_marketplace.estimate_gross_merchandise_value(2),
)
print(
    "Estimated Marketplace Revenue:",
    freelance_marketplace.estimate_marketplace_revenue(2),
)


# ============================================================================
# 8. MARKETPLACE NETWORK EFFECTS
# ============================================================================

print("\n" + "=" * 80)
print("8. NETWORK EFFECTS")
print("=" * 80)

print(
    """
A network effect occurs when a product becomes more valuable as more
participants join.

Direct network effect:
More users directly increase value for other users.

Example:
A communication network.

Cross-side network effect:
More participants on one side increase value for another side.

Example:
More sellers attract buyers.
More buyers attract sellers.

Network effects can be positive or negative.

Negative network effects can occur when:
- Too many sellers create intense competition.
- Too many users reduce service quality.
- Spam increases.
- Congestion increases.
"""
)


def estimate_possible_connections(users: int) -> int:
    """
    Calculate possible pairwise relationships.

    Formula:
        n * (n - 1) / 2

    This does not measure actual economic value, but demonstrates how the
    number of potential relationships grows rapidly.
    """
    if users < 0:
        raise ValueError("User count cannot be negative.")

    return users * (users - 1) // 2


for user_count in [1, 10, 100, 1000]:
    print(
        f"Users: {user_count:4} | "
        f"Possible pairwise connections: "
        f"{estimate_possible_connections(user_count):,}"
    )


# ============================================================================
# 9. PLATFORMS
# ============================================================================

print("\n" + "=" * 80)
print("9. PLATFORMS")
print("=" * 80)

print(
    """
A platform provides a foundation on which other participants can build,
interact, create, distribute, or transact.

A platform can support:
- Developers
- Businesses
- Consumers
- Content creators
- Partners
- Third-party service providers

Important distinction:

A marketplace primarily focuses on facilitating transactions between sides.

A platform provides capabilities that allow other participants to create or
extend value.

Some products are both platforms and marketplaces.
"""
)


@dataclass
class Platform(Product):
    """A platform supporting external participants."""

    active_developers: int = 0
    third_party_integrations: int = 0

    def ecosystem_health_score(self) -> float:
        """
        A simple illustrative score.

        This is not an industry-standard metric.
        It demonstrates that platform value depends on ecosystem participation.
        """
        return (
            self.active_developers * 0.6
            + self.third_party_integrations * 0.4
        )


developer_platform = Platform(
    name="BuildCloud",
    description="Cloud platform for developers to build and deploy applications.",
    customer_types={CustomerType.BUSINESS, CustomerType.DEVELOPER},
    revenue_models={RevenueModel.USAGE_BASED, RevenueModel.SUBSCRIPTION},
    distribution_models={DistributionModel.SELF_SERVICE, DistributionModel.API_DISTRIBUTION},
    target_users=["Developers", "Engineering Teams"],
    active_developers=50_000,
    third_party_integrations=2_000,
)

developer_platform.describe()
print(
    "Illustrative Ecosystem Health Score:",
    developer_platform.ecosystem_health_score(),
)


# ============================================================================
# 10. API PRODUCTS
# ============================================================================

print("\n" + "=" * 80)
print("10. APIS AS PRODUCTS")
print("=" * 80)

print(
    """
API means Application Programming Interface.

An API product allows one software system to interact with another software
system through defined interfaces.

An API can be:
- A technical component inside a company
- A public developer product
- A commercial product
- Infrastructure for a platform

API product design requires attention to:
- Authentication
- Authorization
- Documentation
- Versioning
- Rate limiting
- Reliability
- Error responses
- Backward compatibility
- Security
- Pricing

An API is not automatically a product merely because an endpoint exists.
It becomes a product when it has identifiable users, value, usability,
documentation, lifecycle management, and operational expectations.
"""
)


class APIError(Exception):
    """Base exception for the API simulation."""


class AuthenticationError(APIError):
    """Raised when credentials are invalid."""


class RateLimitError(APIError):
    """Raised when a client exceeds allowed request volume."""


@dataclass
class SimpleAPIProduct(Product):
    """
    Simplified API product.

    The implementation is intentionally small but demonstrates product-level
    concerns such as authentication, rate limiting, and structured responses.
    """

    valid_api_keys: Set[str] = field(default_factory=set)
    requests_per_key: Dict[str, int] = field(default_factory=dict)
    rate_limit: int = 5

    def authenticate(self, api_key: str) -> None:
        if api_key not in self.valid_api_keys:
            raise AuthenticationError("Invalid API key.")

    def enforce_rate_limit(self, api_key: str) -> None:
        request_count = self.requests_per_key.get(api_key, 0)

        if request_count >= self.rate_limit:
            raise RateLimitError(
                f"Rate limit exceeded. Maximum: {self.rate_limit} requests."
            )

        self.requests_per_key[api_key] = request_count + 1

    def get_product_data(
        self,
        api_key: str,
        product_name: str,
    ) -> Dict[str, str]:
        """
        Simulates an API request.

        A real API would receive HTTP requests and return JSON responses.
        """
        self.authenticate(api_key)
        self.enforce_rate_limit(api_key)

        return {
            "status": "success",
            "product": product_name,
            "source": self.name,
        }


catalog_api = SimpleAPIProduct(
    name="ProductCatalogAPI",
    description="API providing structured product information.",
    customer_types={CustomerType.BUSINESS, CustomerType.DEVELOPER},
    revenue_models={RevenueModel.USAGE_BASED},
    distribution_models={DistributionModel.API_DISTRIBUTION},
    target_users=["Developers", "Software Companies"],
    valid_api_keys={"demo-key"},
    rate_limit=3,
)

print("\nAPI Request Simulation")

for request_number in range(1, 5):
    try:
        response = catalog_api.get_product_data(
            api_key="demo-key",
            product_name=f"Product {request_number}",
        )
        print(response)
    except APIError as error:
        print(f"Request {request_number} failed: {error}")


# ============================================================================
# 11. API VERSIONING
# ============================================================================

print("\n" + "=" * 80)
print("11. API VERSIONING")
print("=" * 80)

print(
    """
APIs require careful versioning because external customers may depend on them.

Breaking changes include:
- Removing fields
- Renaming fields
- Changing data types
- Changing authentication behavior
- Changing endpoint semantics

A safer strategy is to maintain versions temporarily.

Examples:
- /v1/products
- /v2/products

Versioning has trade-offs:
- Maintaining old versions increases operational complexity.
- Removing versions too quickly can break customers.
"""
)


@dataclass
class VersionedAPI:
    """A minimal API versioning example."""

    supported_versions: Dict[str, Callable[[str], Dict[str, object]]]

    def request(self, version: str, product_name: str) -> Dict[str, object]:
        if version not in self.supported_versions:
            raise ValueError(f"Unsupported API version: {version}")

        return self.supported_versions[version](product_name)


def api_v1(product_name: str) -> Dict[str, object]:
    return {
        "name": product_name,
        "version": "v1",
    }


def api_v2(product_name: str) -> Dict[str, object]:
    return {
        "product": {
            "name": product_name,
        },
        "metadata": {
            "version": "v2",
        },
    }


versioned_api = VersionedAPI(
    supported_versions={
        "v1": api_v1,
        "v2": api_v2,
    }
)

print(versioned_api.request("v1", "Analytics Tool"))
print(versioned_api.request("v2", "Analytics Tool"))

try:
    versioned_api.request("v3", "Analytics Tool")
except ValueError as error:
    print("Version Error:", error)


# ============================================================================
# 12. CONSUMER APPLICATIONS
# ============================================================================

print("\n" + "=" * 80)
print("12. CONSUMER APPLICATIONS")
print("=" * 80)

print(
    """
A consumer application is designed primarily for individual users.

Consumer applications often focus heavily on:
- User experience
- Onboarding
- Retention
- Engagement
- Accessibility
- Performance
- Privacy
- Personalization

Important distinction:

B2C describes the commercial relationship.

Consumer application describes the primary type of user.

Many consumer applications are B2C, but terminology can differ depending on
whether the emphasis is on business model or product design.
"""
)


@dataclass
class ConsumerApp(B2CProduct):
    """Consumer application metrics."""

    daily_active_users: int = 0
    notifications_enabled_users: int = 0

    def engagement_ratio(self) -> float:
        """
        DAU / MAU is a commonly used engagement indicator.

        Edge case:
        MAU of zero would cause division by zero.
        """
        if self.monthly_active_users == 0:
            return 0.0

        return self.daily_active_users / self.monthly_active_users

    def notification_opt_in_rate(self) -> float:
        if self.monthly_active_users == 0:
            return 0.0

        return (
            self.notifications_enabled_users
            / self.monthly_active_users
        )


social_app = ConsumerApp(
    name="CommunityConnect",
    description="Consumer application for community interaction.",
    customer_types={CustomerType.CONSUMER},
    revenue_models={RevenueModel.ADVERTISING, RevenueModel.FREEMIUM},
    distribution_models={DistributionModel.APP_STORE},
    target_users=["Consumers"],
    monthly_active_users=1_000_000,
    daily_active_users=250_000,
    notifications_enabled_users=600_000,
)

social_app.describe()
print("DAU/MAU Engagement Ratio:", round(social_app.engagement_ratio(), 3))
print(
    "Notification Opt-In Rate:",
    round(social_app.notification_opt_in_rate(), 3),
)


# ============================================================================
# 13. ENTERPRISE PRODUCTS
# ============================================================================

print("\n" + "=" * 80)
print("13. ENTERPRISE PRODUCTS")
print("=" * 80)

print(
    """
Enterprise products are designed for large or complex organizations.

Enterprise product requirements commonly include:
- Role-based access control
- Single sign-on
- Audit logs
- Compliance requirements
- Administrative controls
- High availability
- Integration capabilities
- Data governance
- Security reviews
- Service-level agreements

A product can be B2B without being enterprise.

Small businesses may purchase B2B products with simple self-service plans.

Enterprise products usually require greater operational and organizational
capabilities.
"""
)


class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    AUDITOR = "auditor"


PERMISSIONS = {
    Role.ADMIN: {
        "read",
        "write",
        "delete",
        "manage_users",
        "view_audit_logs",
    },
    Role.MANAGER: {
        "read",
        "write",
    },
    Role.USER: {
        "read",
    },
    Role.AUDITOR: {
        "read",
        "view_audit_logs",
    },
}


@dataclass
class EnterpriseUser:
    """Represents a user in an enterprise product."""

    username: str
    role: Role


class AccessControlSystem:
    """
    Simplified role-based access control.

    RBAC is important because enterprise software often has users with
    different responsibilities and permissions.
    """

    def can_perform(
        self,
        user: EnterpriseUser,
        action: str,
    ) -> bool:
        return action in PERMISSIONS.get(user.role, set())


access_control = AccessControlSystem()

enterprise_users = [
    EnterpriseUser("alice", Role.ADMIN),
    EnterpriseUser("bob", Role.MANAGER),
    EnterpriseUser("charlie", Role.USER),
    EnterpriseUser("diana", Role.AUDITOR),
]

for user in enterprise_users:
    print(
        f"{user.username:7} ({user.role.value:7}) "
        f"can delete: {access_control.can_perform(user, 'delete')}"
    )


# ============================================================================
# 14. MULTI-TENANCY
# ============================================================================

print("\n" + "=" * 80)
print("14. MULTI-TENANCY")
print("=" * 80)

print(
    """
Many SaaS and enterprise products are multi-tenant.

Tenant:
An organization or customer whose data and users must be logically separated
from those of other organizations.

Example:
Tenant A should not be able to access Tenant B's information.

Tenant isolation is a major security requirement.

Common approaches:
- Shared database with tenant identifiers
- Separate schemas
- Separate databases
- Separate infrastructure

The correct approach depends on security, scale, regulation, operational cost,
and customer requirements.
"""
)


@dataclass
class TenantRecord:
    tenant_id: str
    data: Dict[str, object]


class MultiTenantStore:
    """
    Simplified in-memory tenant-aware storage.

    Important security rule:
    Every query must be scoped to the correct tenant.

    Forgetting tenant filtering is a common and serious multi-tenant security
    vulnerability.
    """

    def __init__(self) -> None:
        self.records: List[TenantRecord] = []

    def add_record(
        self,
        tenant_id: str,
        data: Dict[str, object],
    ) -> None:
        self.records.append(
            TenantRecord(
                tenant_id=tenant_id,
                data=data,
            )
        )

    def get_records_for_tenant(
        self,
        tenant_id: str,
    ) -> List[Dict[str, object]]:
        return [
            record.data
            for record in self.records
            if record.tenant_id == tenant_id
        ]


tenant_store = MultiTenantStore()

tenant_store.add_record(
    "company-a",
    {"employee": "Alice", "department": "Engineering"},
)

tenant_store.add_record(
    "company-b",
    {"employee": "Bob", "department": "Finance"},
)

print("Company A records:", tenant_store.get_records_for_tenant("company-a"))
print("Company B records:", tenant_store.get_records_for_tenant("company-b"))


# ============================================================================
# 15. PRODUCT CLASSIFICATION ENGINE
# ============================================================================

print("\n" + "=" * 80)
print("15. PRODUCT CLASSIFICATION ENGINE")
print("=" * 80)

print(
    """
Product categories can overlap.

Examples:
- A SaaS product can be B2B and enterprise.
- A platform can expose APIs.
- A marketplace can also be a platform.
- A B2B2C company can provide SaaS infrastructure.
- A consumer app can use a marketplace model.

Therefore, product classification should not assume one product belongs to
exactly one category.
"""
)


class ProductClassifier:
    """
    Rule-based educational classifier.

    Real product classification often requires qualitative analysis.
    """

    @staticmethod
    def classify(product: Product) -> Set[str]:
        categories: Set[str] = set()

        if CustomerType.BUSINESS in product.customer_types:
            categories.add("B2B")

        if CustomerType.CONSUMER in product.customer_types:
            categories.add("B2C")

        if (
            CustomerType.BUSINESS in product.customer_types
            and CustomerType.CONSUMER in product.customer_types
            and DistributionModel.PARTNER_LED in product.distribution_models
        ):
            categories.add("B2B2C")

        if RevenueModel.SUBSCRIPTION in product.revenue_models:
            categories.add("Potential SaaS")

        if DistributionModel.MARKETPLACE in product.distribution_models:
            categories.add("Marketplace")

        if DistributionModel.API_DISTRIBUTION in product.distribution_models:
            categories.add("API Product")

        if CustomerType.DEVELOPER in product.customer_types:
            categories.add("Developer Platform")

        return categories


products_to_classify = [
    crm_product,
    fitness_app,
    payment_network,
    analytics_saas,
    freelance_marketplace,
    catalog_api,
    developer_platform,
]

classifier = ProductClassifier()

for product in products_to_classify:
    print(
        f"{product.name:20} -> "
        f"{', '.join(sorted(classifier.classify(product)))}"
    )


# ============================================================================
# 16. PRODUCT BUSINESS MODEL ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("16. BUSINESS MODEL ANALYSIS")
print("=" * 80)

print(
    """
A product business model explains how value is captured economically.

Common models:

Subscription:
Customer pays repeatedly.

Usage-based:
Customer pays according to consumption.

Transaction fee:
A fee is charged for processing activity.

Commission:
The product receives a percentage of a transaction.

Advertising:
Advertisers pay for access to an audience.

Freemium:
Basic functionality is free and advanced functionality is paid.

Licensing:
Rights to use software or technology are purchased.
"""
)


def calculate_subscription_revenue(
    customers: int,
    monthly_price: float,
    months: int,
) -> float:
    if customers < 0 or monthly_price < 0 or months < 0:
        raise ValueError("Inputs cannot be negative.")

    return customers * monthly_price * months


def calculate_usage_revenue(
    units_used: int,
    price_per_unit: float,
) -> float:
    if units_used < 0 or price_per_unit < 0:
        raise ValueError("Inputs cannot be negative.")

    return units_used * price_per_unit


def calculate_commission_revenue(
    transaction_value: float,
    commission_rate: float,
) -> float:
    if transaction_value < 0:
        raise ValueError("Transaction value cannot be negative.")

    if not 0 <= commission_rate <= 1:
        raise ValueError("Commission rate must be between 0 and 1.")

    return transaction_value * commission_rate


print(
    "Subscription Revenue:",
    calculate_subscription_revenue(
        customers=1000,
        monthly_price=25,
        months=12,
    ),
)

print(
    "Usage-Based Revenue:",
    calculate_usage_revenue(
        units_used=500_000,
        price_per_unit=0.02,
    ),
)

print(
    "Commission Revenue:",
    calculate_commission_revenue(
        transaction_value=1_000_000,
        commission_rate=0.10,
    ),
)


# ============================================================================
# 17. UNIT ECONOMICS
# ============================================================================

print("\n" + "=" * 80)
print("17. UNIT ECONOMICS")
print("=" * 80)

print(
    """
Unit economics measures the economics associated with one customer,
transaction, user, or unit.

Important metrics include:

CAC:
Customer Acquisition Cost.

ARPU:
Average Revenue Per User.

LTV:
Lifetime Value.

A simplified LTV model can be:

LTV = ARPU / churn rate

This formula has limitations and should not be used blindly.
It assumes relatively stable revenue and churn behavior.
"""
)


def calculate_cac(
    marketing_cost: float,
    sales_cost: float,
    new_customers: int,
) -> float:
    if new_customers <= 0:
        raise ValueError("New customers must be greater than zero.")

    return (marketing_cost + sales_cost) / new_customers


def calculate_arpu(
    revenue: float,
    active_users: int,
) -> float:
    if active_users <= 0:
        raise ValueError("Active users must be greater than zero.")

    return revenue / active_users


def calculate_simple_ltv(
    monthly_arpu: float,
    monthly_churn_rate: float,
) -> float:
    if monthly_arpu < 0:
        raise ValueError("ARPU cannot be negative.")

    if not 0 < monthly_churn_rate <= 1:
        raise ValueError(
            "Churn rate must be greater than zero and at most one."
        )

    return monthly_arpu / monthly_churn_rate


cac = calculate_cac(
    marketing_cost=50_000,
    sales_cost=30_000,
    new_customers=400,
)

arpu = calculate_arpu(
    revenue=25_000,
    active_users=1_000,
)

ltv = calculate_simple_ltv(
    monthly_arpu=arpu,
    monthly_churn_rate=0.05,
)

print("CAC:", cac)
print("ARPU:", arpu)
print("Simplified LTV:", ltv)
print("LTV/CAC Ratio:", round(ltv / cac, 2))


# ============================================================================
# 18. PRODUCT METRICS BY PRODUCT TYPE
# ============================================================================

print("\n" + "=" * 80)
print("18. PRODUCT METRICS BY TYPE")
print("=" * 80)

metrics_by_product_type = {
    "B2B": [
        "Annual contract value",
        "Sales cycle length",
        "Customer retention",
        "Expansion revenue",
        "Implementation success",
    ],
    "B2C": [
        "Monthly active users",
        "Daily active users",
        "Retention",
        "Conversion rate",
        "Customer acquisition cost",
    ],
    "SaaS": [
        "Monthly recurring revenue",
        "Annual recurring revenue",
        "Churn",
        "Net revenue retention",
        "Customer lifetime value",
    ],
    "Marketplace": [
        "Liquidity",
        "Gross merchandise value",
        "Take rate",
        "Match rate",
        "Repeat transactions",
    ],
    "API Product": [
        "API calls",
        "Active developers",
        "Error rate",
        "Latency",
        "Customer retention",
    ],
    "Enterprise": [
        "Contract value",
        "Renewal rate",
        "System availability",
        "Implementation time",
        "Support resolution time",
    ],
}

for product_type, metrics in metrics_by_product_type.items():
    print(f"\n{product_type}")
    for metric in metrics:
        print(" -", metric)


# ============================================================================
# 19. RETENTION COHORT SIMULATION
# ============================================================================

print("\n" + "=" * 80)
print("19. RETENTION COHORT SIMULATION")
print("=" * 80)

print(
    """
Retention analysis measures how many users remain active over time.

A cohort is a group of users who share a characteristic, commonly the time
when they joined a product.

Example:
100 users join in January.
After one month, 70 remain active.
Retention = 70%.

Retention often provides more insight than total user growth because total
growth can hide the loss of existing users.
"""
)


def simulate_retention(
    initial_users: int,
    monthly_retention_rate: float,
    months: int,
) -> List[int]:
    if initial_users < 0:
        raise ValueError("Initial users cannot be negative.")

    if not 0 <= monthly_retention_rate <= 1:
        raise ValueError("Retention rate must be between 0 and 1.")

    if months < 0:
        raise ValueError("Months cannot be negative.")

    remaining_users = initial_users
    history = [remaining_users]

    for _ in range(months):
        remaining_users = round(
            remaining_users * monthly_retention_rate
        )
        history.append(remaining_users)

    return history


retention_history = simulate_retention(
    initial_users=1000,
    monthly_retention_rate=0.85,
    months=6,
)

for month, users in enumerate(retention_history):
    retention_percentage = (
        users / retention_history[0] * 100
        if retention_history[0] > 0
        else 0
    )

    print(
        f"Month {month}: "
        f"{users} users, "
        f"{retention_percentage:.1f}% retained"
    )


# ============================================================================
# 20. PRODUCT PRICING STRATEGIES
# ============================================================================

print("\n" + "=" * 80)
print("20. PRODUCT PRICING STRATEGIES")
print("=" * 80)

print(
    """
Pricing models depend on product type and customer behavior.

Common approaches:

Per-user pricing:
Useful when value scales with users.

Usage-based pricing:
Useful when infrastructure consumption scales with activity.

Flat-rate pricing:
Simple and predictable.

Tiered pricing:
Different feature sets or capacity levels.

Enterprise pricing:
Often negotiated based on organizational requirements.

Marketplace take rate:
A percentage of transactions.

Pricing involves trade-offs:
- Simplicity versus flexibility
- Predictability versus value alignment
- Revenue maximization versus adoption
"""
)


@dataclass
class PricingTier:
    name: str
    monthly_price: float
    included_units: int
    overage_price_per_unit: float

    def calculate_price(self, units_used: int) -> float:
        if units_used < 0:
            raise ValueError("Units used cannot be negative.")

        if units_used <= self.included_units:
            return self.monthly_price

        additional_units = units_used - self.included_units

        return (
            self.monthly_price
            + additional_units * self.overage_price_per_unit
        )


api_pricing_tier = PricingTier(
    name="Professional",
    monthly_price=100,
    included_units=10_000,
    overage_price_per_unit=0.01,
)

for usage in [5_000, 10_000, 15_000]:
    print(
        f"Usage: {usage:6} units | "
        f"Price: {api_pricing_tier.calculate_price(usage):.2f}"
    )


# ============================================================================
# 21. PRODUCT DISCOVERY DATABASES
# ============================================================================

print("\n" + "=" * 80)
print("21. PRODUCT DISCOVERY AND COMPANY DATABASES")
print("=" * 80)

print(
    """
Products and companies are often discovered through specialized information
ecosystems.

Two well-known examples are:

Product Hunt:
A product discovery ecosystem where people explore and discuss products,
particularly technology products and launches.

Crunchbase:
A business and company information ecosystem used to explore organizations,
funding activity, investors, industries, and related company information.

These services represent information products rather than being direct
substitutes for the product types described earlier.

Their value comes from structured information, discovery, search,
categorization, and ecosystem knowledge.
"""
)


@dataclass
class ProductListing:
    """
    Simplified representation of a product discovery record.

    This demonstrates how structured product information can support search
    and classification.
    """

    name: str
    category: str
    description: str
    launch_year: int
    tags: Set[str]


class ProductDiscoveryCatalog:
    """In-memory catalog supporting simple product discovery."""

    def __init__(self) -> None:
        self.listings: List[ProductListing] = []

    def add_listing(self, listing: ProductListing) -> None:
        self.listings.append(listing)

    def search_by_keyword(
        self,
        keyword: str,
    ) -> List[ProductListing]:
        normalized_keyword = keyword.lower()

        return [
            listing
            for listing in self.listings
            if (
                normalized_keyword in listing.name.lower()
                or normalized_keyword in listing.description.lower()
                or any(
                    normalized_keyword in tag.lower()
                    for tag in listing.tags
                )
            )
        ]

    def search_by_category(
        self,
        category: str,
    ) -> List[ProductListing]:
        return [
            listing
            for listing in self.listings
            if listing.category.lower() == category.lower()
        ]


catalog = ProductDiscoveryCatalog()

catalog.add_listing(
    ProductListing(
        name="TaskFlow",
        category="B2B SaaS",
        description="Project management software for distributed teams.",
        launch_year=2025,
        tags={"productivity", "project-management", "saas"},
    )
)

catalog.add_listing(
    ProductListing(
        name="MealConnect",
        category="Marketplace",
        description="Marketplace connecting local food providers with customers.",
        launch_year=2026,
        tags={"marketplace", "food", "consumer"},
    )
)

catalog.add_listing(
    ProductListing(
        name="DataBridge API",
        category="API",
        description="API for accessing structured business information.",
        launch_year=2024,
        tags={"api", "developer", "data"},
    )
)

print("\nSearch for 'API'")
for listing in catalog.search_by_keyword("API"):
    print(f"- {listing.name}: {listing.category}")

print("\nSearch for Marketplace")
for listing in catalog.search_by_category("Marketplace"):
    print(f"- {listing.name}: {listing.description}")


# ============================================================================
# 22. COMPANY AND PRODUCT DATA MODELING
# ============================================================================

print("\n" + "=" * 80)
print("22. COMPANY AND PRODUCT DATA MODELING")
print("=" * 80)

print(
    """
Product and company information systems frequently use structured records.

Typical company information may include:
- Company name
- Industry
- Founding year
- Products
- Funding information
- Investors
- Employees
- Headquarters

Data modeling requires clear distinctions between:
- A company
- A product
- A product category
- A customer
- A market
- A funding event

Poor data modeling creates ambiguity and makes analysis unreliable.
"""
)


@dataclass
class Company:
    name: str
    industry: str
    founded_year: int
    products: List[Product] = field(default_factory=list)

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def product_categories(self) -> Dict[str, List[str]]:
        classifier = ProductClassifier()

        return {
            product.name: sorted(classifier.classify(product))
            for product in self.products
        }


sample_company = Company(
    name="Example Technologies",
    industry="Software",
    founded_year=2020,
)

sample_company.add_product(analytics_saas)
sample_company.add_product(catalog_api)

print(
    json.dumps(
        sample_company.product_categories(),
        indent=2,
    )
)


# ============================================================================
# 23. PRODUCT DECISION MATRIX
# ============================================================================

print("\n" + "=" * 80)
print("23. PRODUCT DECISION MATRIX")
print("=" * 80)

print(
    """
Product decisions often require comparing alternatives using multiple criteria.

A weighted decision matrix can compare options according to criteria such as:
- Revenue potential
- Development complexity
- Customer demand
- Time to market
- Operational complexity

Important limitation:
A scoring model does not replace judgment.

Weights and scores can contain bias.
Quantitative frameworks are useful when assumptions are explicit.
"""
)


@dataclass
class ProductStrategyOption:
    name: str
    scores: Dict[str, float]

    def weighted_score(
        self,
        weights: Dict[str, float],
    ) -> float:
        if set(self.scores) != set(weights):
            raise ValueError(
                "Scores and weights must contain the same criteria."
            )

        return sum(
            self.scores[criterion] * weights[criterion]
            for criterion in weights
        )


weights = {
    "revenue_potential": 0.35,
    "customer_demand": 0.30,
    "time_to_market": 0.20,
    "operational_feasibility": 0.15,
}

strategy_options = [
    ProductStrategyOption(
        name="B2B SaaS",
        scores={
            "revenue_potential": 9,
            "customer_demand": 8,
            "time_to_market": 6,
            "operational_feasibility": 7,
        },
    ),
    ProductStrategyOption(
        name="Consumer App",
        scores={
            "revenue_potential": 7,
            "customer_demand": 9,
            "time_to_market": 8,
            "operational_feasibility": 6,
        },
    ),
    ProductStrategyOption(
        name="Marketplace",
        scores={
            "revenue_potential": 9,
            "customer_demand": 7,
            "time_to_market": 5,
            "operational_feasibility": 5,
        },
    ),
]

ranked_options = sorted(
    strategy_options,
    key=lambda option: option.weighted_score(weights),
    reverse=True,
)

for option in ranked_options:
    print(
        f"{option.name:15} "
        f"Score: {option.weighted_score(weights):.2f}"
    )


# ============================================================================
# 24. PRODUCT RISKS
# ============================================================================

print("\n" + "=" * 80)
print("24. PRODUCT RISKS AND TRADE-OFFS")
print("=" * 80)

product_risks = {
    "B2B": [
        "Long sales cycles",
        "Customer concentration",
        "Complex procurement",
        "Integration requirements",
    ],
    "B2C": [
        "High acquisition costs",
        "Low switching costs",
        "Large-scale support requirements",
        "Intense competition",
    ],
    "Marketplace": [
        "Chicken-and-egg problem",
        "Fraud",
        "Supply-demand imbalance",
        "Trust and safety requirements",
    ],
    "API": [
        "Breaking changes",
        "Abuse",
        "Security vulnerabilities",
        "Availability dependencies",
    ],
    "Enterprise": [
        "Complex implementation",
        "Security requirements",
        "Long procurement cycles",
        "Customization pressure",
    ],
}

for category, risks in product_risks.items():
    print(f"\n{category} Risks:")
    for risk in risks:
        print(" -", risk)


# ============================================================================
# 25. PRODUCT SECURITY CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("25. SECURITY CONSIDERATIONS")
print("=" * 80)

print(
    """
Security requirements differ by product type but commonly include:

Authentication:
Verify identity.

Authorization:
Determine what an authenticated entity may do.

Encryption:
Protect information during transmission and storage.

Input validation:
Reject malformed or dangerous input.

Rate limiting:
Reduce abuse and excessive consumption.

Audit logging:
Record important actions.

Tenant isolation:
Prevent customers from accessing each other's data.

A common mistake is treating security as a feature added after product design.
Security requirements should influence architecture and product decisions early.
"""
)


def validate_product_name(name: str) -> str:
    """
    Simple input validation example.

    Production validation would depend on specific business requirements.
    """
    if not isinstance(name, str):
        raise TypeError("Product name must be a string.")

    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Product name cannot be empty.")

    if len(cleaned_name) > 100:
        raise ValueError("Product name is too long.")

    return cleaned_name


test_names = [
    "Analytics Platform",
    "   ",
    "",
]

for name in test_names:
    try:
        print("Validated:", validate_product_name(name))
    except (TypeError, ValueError) as error:
        print(f"Validation failed for {name!r}: {error}")


# ============================================================================
# 26. PERFORMANCE CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("26. PERFORMANCE CONSIDERATIONS")
print("=" * 80)

print(
    """
Different product types create different performance requirements.

Consumer applications:
- Fast response times
- Large traffic spikes
- Mobile network variability

Enterprise products:
- Reliability
- Predictable performance
- Large datasets
- Integration performance

Marketplaces:
- Search and matching speed
- Real-time availability

APIs:
- Low latency
- Rate limits
- Efficient payloads
- Caching

Performance is often a product requirement because poor performance directly
reduces usability and customer trust.
"""
)


def linear_search(
    listings: List[ProductListing],
    keyword: str,
) -> List[ProductListing]:
    """
    O(n) search implementation.

    Each listing is examined.
    """
    keyword = keyword.lower()

    return [
        listing
        for listing in listings
        if keyword in listing.name.lower()
    ]


def build_name_index(
    listings: List[ProductListing],
) -> Dict[str, ProductListing]:
    """
    O(n) index construction followed by approximately O(1) lookup.

    This demonstrates a common trade-off:
    memory and preprocessing are exchanged for faster repeated lookups.
    """
    return {
        listing.name.lower(): listing
        for listing in listings
    }


product_index = build_name_index(catalog.listings)

print(
    "Linear Search Result:",
    [item.name for item in linear_search(catalog.listings, "Task")],
)

print(
    "Indexed Lookup Result:",
    product_index.get("taskflow"),
)


# ============================================================================
# 27. DEBUGGING AND VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("27. DEBUGGING AND VALIDATION")
print("=" * 80)

print(
    """
Product software requires systematic debugging.

Useful practices include:
- Input validation
- Structured error handling
- Logging
- Unit testing
- Monitoring
- Metrics
- Reproducible test cases

Assertions are useful for internal assumptions.

They should not be used as the only method of validating untrusted external input.
"""
)


def calculate_take_rate_revenue(
    gmv: float,
    take_rate: float,
) -> float:
    if gmv < 0:
        raise ValueError("GMV cannot be negative.")

    if not 0 <= take_rate <= 1:
        raise ValueError("Take rate must be between 0 and 1.")

    return gmv * take_rate


def run_basic_tests() -> None:
    assert calculate_take_rate_revenue(1000, 0.10) == 100
    assert calculate_take_rate_revenue(0, 0.10) == 0

    try:
        calculate_take_rate_revenue(-1, 0.10)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative GMV should raise ValueError.")

    try:
        calculate_take_rate_revenue(100, 1.5)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid take rate should raise ValueError.")


run_basic_tests()
print("Basic validation tests passed.")


# ============================================================================
# 28. PRODUCT TYPE RECOMMENDATION SIMULATION
# ============================================================================

print("\n" + "=" * 80)
print("28. PRODUCT TYPE RECOMMENDATION SIMULATION")
print("=" * 80)

print(
    """
The following rule-based function demonstrates how product characteristics
can suggest possible product models.

This is not a substitute for market research.
It demonstrates how requirements influence product classification.
"""
)


def suggest_product_models(
    target_businesses: bool,
    target_consumers: bool,
    connects_multiple_groups: bool,
    provides_developer_access: bool,
    recurring_software_value: bool,
) -> List[str]:
    suggestions: List[str] = []

    if target_businesses and not target_consumers:
        suggestions.append("B2B")

    if target_consumers and not target_businesses:
        suggestions.append("B2C / Consumer App")

    if target_businesses and target_consumers:
        suggestions.append("Multi-sided Product")

    if connects_multiple_groups:
        suggestions.append("Marketplace or Platform")

    if provides_developer_access:
        suggestions.append("API Product or Developer Platform")

    if recurring_software_value:
        suggestions.append("SaaS")

    if target_businesses and target_consumers and recurring_software_value:
        suggestions.append("Possible B2B2C SaaS")

    return suggestions


example_suggestions = suggest_product_models(
    target_businesses=True,
    target_consumers=True,
    connects_multiple_groups=True,
    provides_developer_access=True,
    recurring_software_value=True,
)

print("Suggested Models:")
for suggestion in example_suggestions:
    print(" -", suggestion)


# ============================================================================
# 29. ADVANCED PRODUCT ARCHITECTURE CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("29. ADVANCED PRODUCT ARCHITECTURE CONSIDERATIONS")
print("=" * 80)

print(
    """
Product type influences system architecture.

B2B SaaS may require:
- Organization accounts
- Role-based access
- Tenant isolation
- Integrations

Consumer applications may require:
- High scalability
- Personalization
- Notification systems

Marketplaces may require:
- Matching engines
- Payments
- Reputation systems
- Trust and safety systems

Platforms may require:
- Extensibility
- APIs
- Developer tooling
- Versioning

Enterprise products may require:
- Identity integration
- Audit logging
- Compliance controls
- Data governance

Architecture should follow product requirements rather than adopting
complex technology without a demonstrated need.
"""
)


@dataclass
class ArchitectureRequirement:
    product_category: str
    requirements: List[str]


architecture_requirements = [
    ArchitectureRequirement(
        "B2B SaaS",
        [
            "Multi-tenancy",
            "Role-based access",
            "Billing",
            "Integrations",
        ],
    ),
    ArchitectureRequirement(
        "Marketplace",
        [
            "Matching",
            "Payments",
            "Search",
            "Trust and safety",
        ],
    ),
    ArchitectureRequirement(
        "API Platform",
        [
            "Authentication",
            "Rate limiting",
            "Versioning",
            "Monitoring",
        ],
    ),
]

for architecture in architecture_requirements:
    print(f"\n{architecture.product_category}")
    for requirement in architecture.requirements:
        print(" -", requirement)


# ============================================================================
# 30. FINAL INTEGRATED PRODUCT EXAMPLE
# ============================================================================

print("\n" + "=" * 80)
print("30. INTEGRATED PRODUCT EXAMPLE")
print("=" * 80)

print(
    """
The final example demonstrates why modern products can belong to multiple
categories simultaneously.

Imagine a company operating a digital commerce ecosystem:

- Businesses use a SaaS dashboard.
- Consumers use a mobile application.
- Merchants and consumers transact through a marketplace.
- Developers integrate through APIs.
- Enterprise customers receive advanced controls.

This is not five unrelated products.
It can be one connected product ecosystem.
"""
)


@dataclass
class ProductEcosystem:
    name: str
    products: List[Product]

    def categories(self) -> Dict[str, List[str]]:
        classifier = ProductClassifier()

        return {
            product.name: sorted(classifier.classify(product))
            for product in self.products
        }

    def all_revenue_models(self) -> Set[str]:
        return {
            revenue_model.value
            for product in self.products
            for revenue_model in product.revenue_models
        }


merchant_dashboard = SaaSProduct(
    name="Merchant Dashboard",
    description="SaaS dashboard for businesses managing digital sales.",
    customer_types={CustomerType.BUSINESS},
    revenue_models={RevenueModel.SUBSCRIPTION},
    distribution_models={DistributionModel.SELF_SERVICE},
    target_users=["Merchants"],
    price_per_month=100,
    customer_count=1000,
)

consumer_shopping_app = ConsumerApp(
    name="Shopping Application",
    description="Consumer application for discovering products.",
    customer_types={CustomerType.CONSUMER},
    revenue_models={RevenueModel.ADVERTISING, RevenueModel.FREEMIUM},
    distribution_models={DistributionModel.APP_STORE},
    target_users=["Consumers"],
    monthly_active_users=500_000,
    daily_active_users=80_000,
)

commerce_marketplace = Marketplace(
    name="Commerce Marketplace",
    description="Marketplace connecting merchants and consumers.",
    customer_types={CustomerType.BUSINESS, CustomerType.CONSUMER},
    revenue_models={RevenueModel.COMMISSION},
    distribution_models={DistributionModel.MARKETPLACE},
    target_users=["Merchants", "Consumers"],
    buyers=500_000,
    sellers=20_000,
    average_transaction_value=50,
    commission_rate=0.08,
)

commerce_api = SimpleAPIProduct(
    name="Commerce API",
    description="API enabling external commerce integrations.",
    customer_types={CustomerType.BUSINESS, CustomerType.DEVELOPER},
    revenue_models={RevenueModel.USAGE_BASED},
    distribution_models={DistributionModel.API_DISTRIBUTION},
    target_users=["Developers", "Partners"],
    valid_api_keys={"partner-key"},
)

ecosystem = ProductEcosystem(
    name="Connected Commerce Ecosystem",
    products=[
        merchant_dashboard,
        consumer_shopping_app,
        commerce_marketplace,
        commerce_api,
    ],
)

print("\nEcosystem:", ecosystem.name)

print("\nProduct Classifications:")
for product_name, categories in ecosystem.categories().items():
    print(f"- {product_name}: {', '.join(categories)}")

print("\nRevenue Models:")
for revenue_model in sorted(ecosystem.all_revenue_models()):
    print("-", revenue_model)


# ============================================================================
# 31. COMMON PRODUCT CLASSIFICATION MISTAKES
# ============================================================================

print("\n" + "=" * 80)
print("31. COMMON MISTAKES")
print("=" * 80)

common_mistakes = [
    (
        "Mistake",
        "Assuming every product belongs to only one category.",
    ),
    (
        "Why it is incorrect",
        "Modern products frequently combine SaaS, API, platform, marketplace, "
        "and enterprise characteristics.",
    ),
    (
        "Mistake",
        "Confusing the buyer with the user.",
    ),
    (
        "Why it is incorrect",
        "B2B products frequently have economic buyers, administrators, and "
        "end users with different needs.",
    ),
    (
        "Mistake",
        "Assuming SaaS means B2B.",
    ),
    (
        "Why it is incorrect",
        "SaaS describes a software delivery and business model and can serve "
        "businesses or consumers.",
    ),
    (
        "Mistake",
        "Calling every multi-sided product a marketplace.",
    ),
    (
        "Why it is incorrect",
        "Platforms can enable ecosystem participation without directly "
        "facilitating transactions.",
    ),
    (
        "Mistake",
        "Treating APIs only as technical components.",
    ),
    (
        "Why it is incorrect",
        "Commercial APIs require product design, reliability, documentation, "
        "pricing, lifecycle management, and customer support.",
    ),
]

for label, explanation in common_mistakes:
    print(f"\n{label}: {explanation}")


# ============================================================================
# 32. PRACTICAL PRODUCT ANALYSIS WORKFLOW
# ============================================================================

print("\n" + "=" * 80)
print("32. PRACTICAL PRODUCT ANALYSIS WORKFLOW")
print("=" * 80)

workflow = [
    "1. Identify who receives value.",
    "2. Identify who pays.",
    "3. Identify whether buyers and users are the same.",
    "4. Identify how the product is distributed.",
    "5. Identify how revenue is generated.",
    "6. Identify whether multiple user groups interact.",
    "7. Identify whether external parties build on the product.",
    "8. Identify enterprise requirements.",
    "9. Identify API and integration requirements.",
    "10. Classify the product using multiple categories when appropriate.",
]

for step in workflow:
    print(step)


# ============================================================================
# 33. COMPLEXITY SIMULATION: MULTIPLE PRODUCT MODELS
# ============================================================================

print("\n" + "=" * 80)
print("33. MULTI-MODEL PRODUCT COMPLEXITY")
print("=" * 80)

print(
    """
Combining product models can increase opportunities and complexity.

For example:

B2B SaaS:
Requires organization management and recurring billing.

B2B SaaS + API:
Also requires developer experience and version management.

Marketplace + Payments:
Also requires transaction reliability and fraud management.

Enterprise Platform:
May require integrations, security, administration, APIs, compliance,
and ecosystem governance.

More product capabilities can increase value but also increase operational,
technical, and organizational complexity.
"""
)


def estimate_product_complexity(
    is_b2b: bool,
    is_b2c: bool,
    is_marketplace: bool,
    has_api: bool,
    is_enterprise: bool,
) -> int:
    """
    Educational complexity scoring model.

    The score is illustrative, not an industry standard.
    """
    score = 1

    if is_b2b:
        score += 2

    if is_b2c:
        score += 2

    if is_marketplace:
        score += 4

    if has_api:
        score += 3

    if is_enterprise:
        score += 4

    return score


complexity_score = estimate_product_complexity(
    is_b2b=True,
    is_b2c=True,
    is_marketplace=True,
    has_api=True,
    is_enterprise=True,
)

print("Illustrative Complexity Score:", complexity_score)


# ============================================================================
# 34. PRODUCT TYPE REFERENCE
# ============================================================================

print("\n" + "=" * 80)
print("34. PRODUCT TYPE REFERENCE")
print("=" * 80)

reference = {
    "B2B": "A product sold primarily to businesses.",
    "B2C": "A product sold primarily to individual consumers.",
    "B2B2C": (
        "A product that reaches consumers through a business intermediary."
    ),
    "SaaS": (
        "Software delivered as an ongoing service, commonly through recurring "
        "access and payment."
    ),
    "Marketplace": (
        "A product connecting multiple groups to facilitate transactions."
    ),
    "Platform": (
        "A foundation enabling participants to build, interact, distribute, "
        "or create value."
    ),
    "API Product": (
        "A programmable interface managed as a product for external users or "
        "developers."
    ),
    "Consumer App": (
        "An application primarily designed for individual users."
    ),
    "Enterprise Product": (
        "A product designed for the complex operational, security, and "
        "administrative requirements of organizations."
    ),
    "Product Discovery Ecosystem": (
        "An information product that helps users discover, classify, or "
        "analyze products."
    ),
    "Company Information Ecosystem": (
        "An information product that organizes and provides structured "
        "information about companies and business activity."
    ),
}

for term, definition in reference.items():
    print(f"\n{term}\n{definition}")


print("\n" + "=" * 80)
print("END OF PRODUCT TYPES STUDY SCRIPT")
print("=" * 80)
