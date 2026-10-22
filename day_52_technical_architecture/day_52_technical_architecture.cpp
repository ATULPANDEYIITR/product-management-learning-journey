#include <algorithm>
#include <chrono>
#include <cmath>
#include <deque>
#include <exception>
#include <iomanip>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Repository-scale technical architecture case study.
 *
 * Scenario:
 * An order platform has independent Customer and Order domains.
 *
 * The engine demonstrates:
 * - service ownership
 * - database ownership
 * - cache-aside reads
 * - synchronous service dependencies
 * - asynchronous queue processing
 * - retry and dead-letter behavior
 * - horizontal scaling calculations
 * - failure isolation
 *
 * C++17 is used for explicit domain objects, value semantics, and deterministic
 * in-process simulation.
 */

struct Customer {
    int id;
    std::string name;
    std::string tier;
};

struct Order {
    int id;
    int customerId;
    double amount;
    std::string status;
};

struct Event {
    std::string type;
    int orderId;
    int customerId;
    double amount;
    int attempts = 0;
};

class Database {
private:
    std::string name_;
    std::unordered_map<int, Customer> customers_;
    std::unordered_map<int, Order> orders_;
    bool available_ = true;
    std::size_t reads_ = 0;
    std::size_t writes_ = 0;

public:
    explicit Database(std::string name) : name_(std::move(name)) {}

    const std::string& name() const {
        return name_;
    }

    void setAvailable(bool available) {
        available_ = available;
    }

    void ensureAvailable() const {
        if (!available_) {
            throw std::runtime_error("Database unavailable: " + name_);
        }
    }

    void insertCustomer(const Customer& customer) {
        ensureAvailable();

        if (customers_.contains(customer.id)) {
            throw std::invalid_argument("Duplicate customer ID");
        }

        customers_.emplace(customer.id, customer);
        ++writes_;
    }

    std::optional<Customer> findCustomer(int id) {
        ensureAvailable();
        ++reads_;

        auto it = customers_.find(id);
        if (it == customers_.end()) {
            return std::nullopt;
        }

        return it->second;
    }

    int nextOrderId() {
        ensureAvailable();

        int highest = 0;
        for (const auto& [id, order] : orders_) {
            highest = std::max(highest, id);
        }

        return highest + 1;
    }

    void insertOrder(const Order& order) {
        ensureAvailable();

        if (orders_.contains(order.id)) {
            throw std::invalid_argument("Duplicate order ID");
        }

        orders_.emplace(order.id, order);
        ++writes_;
    }

    std::size_t reads() const {
        return reads_;
    }

    std::size_t writes() const {
        return writes_;
    }
};

class Cache {
private:
    struct Entry {
        Customer customer;
        std::chrono::steady_clock::time_point expiresAt;
    };

    std::size_t capacity_;
    std::chrono::seconds ttl_;
    std::unordered_map<int, Entry> entries_;
    std::size_t hits_ = 0;
    std::size_t misses_ = 0;

public:
    Cache(std::size_t capacity, std::chrono::seconds ttl)
        : capacity_(capacity), ttl_(ttl) {
        if (capacity_ == 0 || ttl_.count() <= 0) {
            throw std::invalid_argument("Invalid cache configuration");
        }
    }

    std::optional<Customer> get(int customerId) {
        auto it = entries_.find(customerId);

        if (it == entries_.end()) {
            ++misses_;
            return std::nullopt;
        }

        if (std::chrono::steady_clock::now() >= it->second.expiresAt) {
            entries_.erase(it);
            ++misses_;
            return std::nullopt;
        }

        ++hits_;
        return it->second.customer;
    }

    void put(const Customer& customer) {
        if (!entries_.contains(customer.id) &&
            entries_.size() >= capacity_) {
            entries_.erase(entries_.begin());
        }

        entries_[customer.id] = Entry{
            customer,
            std::chrono::steady_clock::now() + ttl_
        };
    }

    void invalidate(int customerId) {
        entries_.erase(customerId);
    }

    double hitRatio() const {
        const auto total = hits_ + misses_;
        return total == 0
            ? 0.0
            : static_cast<double>(hits_) / static_cast<double>(total);
    }
};

class MessageQueue {
private:
    std::deque<Event> messages_;
    std::vector<Event> deadLetters_;
    int maxRetries_;

public:
    explicit MessageQueue(int maxRetries = 3)
        : maxRetries_(maxRetries) {
        if (maxRetries_ < 1) {
            throw std::invalid_argument("maxRetries must be positive");
        }
    }

    void publish(Event event) {
        messages_.push_back(std::move(event));
    }

    template <typename Handler>
    void drain(Handler handler) {
        while (!messages_.empty()) {
            Event event = messages_.front();
            messages_.pop_front();

            ++event.attempts;

            try {
                handler(event);
            } catch (const std::exception&) {
                if (event.attempts >= maxRetries_) {
                    deadLetters_.push_back(event);
                } else {
                    messages_.push_back(event);
                }
            }
        }
    }

    std::size_t pending() const {
        return messages_.size();
    }

    std::size_t deadLetters() const {
        return deadLetters_.size();
    }
};

class CustomerService {
private:
    Database& database_;
    Cache& cache_;
    bool healthy_ = true;

public:
    CustomerService(Database& database, Cache& cache)
        : database_(database), cache_(cache) {}

    void setHealthy(bool healthy) {
        healthy_ = healthy;
    }

    Customer getCustomer(int customerId) {
        if (customerId <= 0) {
            throw std::invalid_argument("Customer ID must be positive");
        }

        if (!healthy_) {
            throw std::runtime_error("Customer service unavailable");
        }

        if (auto cached = cache_.get(customerId)) {
            return *cached;
        }

        auto customer = database_.findCustomer(customerId);

        if (!customer) {
            throw std::out_of_range("Customer does not exist");
        }

        cache_.put(*customer);
        return *customer;
    }
};

class OrderService {
private:
    Database& database_;
    MessageQueue& queue_;
    CustomerService& customerService_;
    bool healthy_ = true;

public:
    OrderService(
        Database& database,
        MessageQueue& queue,
        CustomerService& customerService
    )
        : database_(database),
          queue_(queue),
          customerService_(customerService) {}

    void setHealthy(bool healthy) {
        healthy_ = healthy;
    }

    Order createOrder(int customerId, double amount) {
        if (!healthy_) {
            throw std::runtime_error("Order service unavailable");
        }

        if (!std::isfinite(amount) || amount <= 0.0) {
            throw std::invalid_argument("Order amount must be positive");
        }

        // Cross-service validation is synchronous because an order cannot
        // safely reference an unknown customer.
        customerService_.getCustomer(customerId);

        Order order{
            database_.nextOrderId(),
            customerId,
            amount,
            "CREATED"
        };

        database_.insertOrder(order);

        // Persistence and publication are separate operations. Production
        // systems often use an outbox pattern to avoid a database/message
        // broker dual-write consistency problem.
        queue_.publish(Event{
            "order.created",
            order.id,
            order.customerId,
            order.amount
        });

        return order;
    }
};

struct ScalingPlan {
    int instances;
    int nominalCapacity;
};

ScalingPlan calculateScaling(int requestsPerSecond, int capacityPerInstance) {
    if (requestsPerSecond < 0 || capacityPerInstance <= 0) {
        throw std::invalid_argument("Invalid scaling inputs");
    }

    const int instances = std::max(
        1,
        static_cast<int>(
            std::ceil(
                static_cast<double>(requestsPerSecond)
                / capacityPerInstance
            )
        )
    );

    return {instances, instances * capacityPerInstance};
}

void printOrder(const Order& order) {
    std::cout
        << "Order{id=" << order.id
        << ", customerId=" << order.customerId
        << ", amount=" << std::fixed << std::setprecision(2)
        << order.amount
        << ", status=" << order.status
        << "}\n";
}

int main() {
    try {
        Database customerDatabase("customer-db");
        Database orderDatabase("order-db");

        Cache customerCache(100, std::chrono::seconds(60));
        MessageQueue orderEvents(3);

        CustomerService customerService(
            customerDatabase,
            customerCache
        );

        OrderService orderService(
            orderDatabase,
            orderEvents,
            customerService
        );

        customerDatabase.insertCustomer(
            {1, "Asha", "PREMIUM"}
        );

        customerDatabase.insertCustomer(
            {2, "Ravi", "STANDARD"}
        );

        std::cout << "Synchronous service workflow:\n";

        Order firstOrder = orderService.createOrder(1, 2499.50);
        printOrder(firstOrder);

        // The second lookup exercises the cache rather than the database.
        Customer firstCustomer = customerService.getCustomer(1);
        Customer cachedCustomer = customerService.getCustomer(1);

        std::cout
            << "Customer: "
            << firstCustomer.name
            << "\nCached customer: "
            << cachedCustomer.name
            << "\nCache hit ratio: "
            << std::fixed
            << std::setprecision(2)
            << customerCache.hitRatio()
            << "\n";

        std::cout << "\nAsynchronous event processing:\n";

        orderEvents.drain([](const Event& event) {
            if (event.type != "order.created") {
                throw std::runtime_error("Unsupported event");
            }

            std::cout
                << "Processed event "
                << event.type
                << " for order "
                << event.orderId
                << "\n";
        });

        std::cout << "\nRetry and dead-letter behavior:\n";

        MessageQueue failingQueue(3);
        failingQueue.publish({
            "payment.capture",
            9001,
            1,
            500.00
        });

        failingQueue.drain([](const Event&) {
            throw std::runtime_error(
                "Payment provider timeout"
            );
        });

        std::cout
            << "Dead letters: "
            << failingQueue.deadLetters()
            << "\n";

        std::cout << "\nFailure isolation:\n";

        customerService.setHealthy(false);

        try {
            orderService.createOrder(1, 750.00);
        } catch (const std::exception& error) {
            std::cout
                << "Order rejected: "
                << error.what()
                << "\n";
        }

        std::cout << "\nScaling plan:\n";

        for (int rps : {50, 100, 101, 250, 1000}) {
            ScalingPlan plan = calculateScaling(rps, 100);

            std::cout
                << rps
                << " RPS -> "
                << plan.instances
                << " instances, nominal capacity "
                << plan.nominalCapacity
                << " RPS\n";
        }

        std::cout << "\nDatabase ownership:\n";
        std::cout
            << customerDatabase.name()
            << " writes="
            << customerDatabase.writes()
            << ", reads="
            << customerDatabase.reads()
            << "\n";

        std::cout
            << orderDatabase.name()
            << " writes="
            << orderDatabase.writes()
            << ", reads="
            << orderDatabase.reads()
            << "\n";

    } catch (const std::exception& error) {
        std::cerr
            << "Architecture simulation failed: "
            << error.what()
            << "\n";
        return 1;
    }

    return 0;
}
