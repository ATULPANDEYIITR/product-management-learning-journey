import java.time.Instant;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/*
 * Enterprise repository-style technical architecture model.
 *
 * The application models a commerce platform where:
 * - CustomerService owns customer data.
 * - OrderService owns order data.
 * - CacheManager implements cache-aside access.
 * - EventQueue provides asynchronous processing.
 * - GovernancePolicy expresses service and scaling constraints.
 *
 * Java 17 records, enums, interfaces, immutable values, explicit state
 * transitions, and domain exceptions are used to keep architecture rules
 * visible in the model.
 */

public class TechnicalArchitectureDemo {

    enum CustomerTier {
        STANDARD,
        PREMIUM,
        ENTERPRISE
    }

    enum OrderStatus {
        CREATED,
        PROCESSING,
        COMPLETED,
        FAILED
    }

    record Customer(
        int id,
        String name,
        CustomerTier tier
    ) {
        Customer {
            if (id <= 0) {
                throw new ValidationException("Customer ID must be positive");
            }
            Objects.requireNonNull(name, "name");
            if (name.isBlank()) {
                throw new ValidationException("Customer name cannot be blank");
            }
            Objects.requireNonNull(tier, "tier");
        }
    }

    record Order(
        int id,
        int customerId,
        long amountPaise,
        OrderStatus status,
        Instant createdAt
    ) {
        Order {
            if (id <= 0 || customerId <= 0) {
                throw new ValidationException("IDs must be positive");
            }
            if (amountPaise <= 0) {
                throw new ValidationException(
                    "Order amount must be positive"
                );
            }
            Objects.requireNonNull(status, "status");
            Objects.requireNonNull(createdAt, "createdAt");
        }

        Order transitionTo(OrderStatus next) {
            boolean valid = switch (status) {
                case CREATED ->
                    next == OrderStatus.PROCESSING
                    || next == OrderStatus.FAILED;
                case PROCESSING ->
                    next == OrderStatus.COMPLETED
                    || next == OrderStatus.FAILED;
                case COMPLETED, FAILED -> false;
            };

            if (!valid) {
                throw new InvalidStateTransitionException(
                    "Cannot move order from "
                    + status
                    + " to "
                    + next
                );
            }

            return new Order(
                id,
                customerId,
                amountPaise,
                next,
                createdAt
            );
        }
    }

    record OrderCreatedEvent(
        int orderId,
        int customerId,
        long amountPaise
    ) {}

    static class ArchitectureException extends RuntimeException {
        ArchitectureException(String message) {
            super(message);
        }
    }

    static class ValidationException extends ArchitectureException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class ServiceUnavailableException
        extends ArchitectureException {

        ServiceUnavailableException(String message) {
            super(message);
        }
    }

    static class InvalidStateTransitionException
        extends ArchitectureException {

        InvalidStateTransitionException(String message) {
            super(message);
        }
    }

    interface Repository<T> {
        Optional<T> findById(int id);

        void save(T value);

        List<T> findAll();
    }

    static final class CustomerRepository
        implements Repository<Customer> {

        private final Map<Integer, Customer> records =
            new HashMap<>();

        private boolean available = true;
        private long reads;
        private long writes;

        void setAvailable(boolean available) {
            this.available = available;
        }

        private void ensureAvailable() {
            if (!available) {
                throw new ServiceUnavailableException(
                    "Customer database unavailable"
                );
            }
        }

        @Override
        public Optional<Customer> findById(int id) {
            ensureAvailable();
            reads++;
            return Optional.ofNullable(records.get(id));
        }

        @Override
        public void save(Customer value) {
            ensureAvailable();

            if (records.containsKey(value.id())) {
                throw new ValidationException(
                    "Customer already exists"
                );
            }

            records.put(value.id(), value);
            writes++;
        }

        @Override
        public List<Customer> findAll() {
            ensureAvailable();
            reads += records.size();
            return List.copyOf(records.values());
        }

        long reads() {
            return reads;
        }

        long writes() {
            return writes;
        }
    }

    static final class OrderRepository
        implements Repository<Order> {

        private final Map<Integer, Order> records =
            new HashMap<>();

        private boolean available = true;
        private long reads;
        private long writes;

        void setAvailable(boolean available) {
            this.available = available;
        }

        private void ensureAvailable() {
            if (!available) {
                throw new ServiceUnavailableException(
                    "Order database unavailable"
                );
            }
        }

        @Override
        public Optional<Order> findById(int id) {
            ensureAvailable();
            reads++;
            return Optional.ofNullable(records.get(id));
        }

        @Override
        public void save(Order order) {
            ensureAvailable();

            if (records.containsKey(order.id())) {
                throw new ValidationException(
                    "Order already exists"
                );
            }

            records.put(order.id(), order);
            writes++;
        }

        @Override
        public List<Order> findAll() {
            ensureAvailable();
            reads += records.size();
            return List.copyOf(records.values());
        }

        int nextId() {
            return records.keySet()
                .stream()
                .mapToInt(Integer::intValue)
                .max()
                .orElse(0) + 1;
        }

        long reads() {
            return reads;
        }

        long writes() {
            return writes;
        }
    }

    static final class CacheManager {
        private record Entry(
            Customer value,
            long expiresAt
        ) {}

        private final int capacity;
        private final long ttlMillis;
        private final Map<Integer, Entry> entries =
            new HashMap<>();

        private long hits;
        private long misses;

        CacheManager(int capacity, long ttlMillis) {
            if (capacity <= 0 || ttlMillis <= 0) {
                throw new ValidationException(
                    "Invalid cache configuration"
                );
            }

            this.capacity = capacity;
            this.ttlMillis = ttlMillis;
        }

        Optional<Customer> get(int customerId) {
            Entry entry = entries.get(customerId);

            if (entry == null) {
                misses++;
                return Optional.empty();
            }

            if (entry.expiresAt() <= System.currentTimeMillis()) {
                entries.remove(customerId);
                misses++;
                return Optional.empty();
            }

            hits++;
            return Optional.of(entry.value());
        }

        void put(Customer customer) {
            if (!entries.containsKey(customer.id())
                && entries.size() >= capacity) {

                Integer oldestKey =
                    entries.keySet().iterator().next();

                entries.remove(oldestKey);
            }

            entries.put(
                customer.id(),
                new Entry(
                    customer,
                    System.currentTimeMillis() + ttlMillis
                )
            );
        }

        void invalidate(int customerId) {
            entries.remove(customerId);
        }

        double hitRatio() {
            long total = hits + misses;
            return total == 0
                ? 0.0
                : (double) hits / total;
        }
    }

    static final class EventQueue {
        private record Message(
            OrderCreatedEvent event,
            int attempts
        ) {}

        private final Deque<Message> messages =
            new ArrayDeque<>();

        private final List<OrderCreatedEvent> deadLetters =
            new ArrayList<>();

        private final int maxRetries;

        EventQueue(int maxRetries) {
            if (maxRetries < 1) {
                throw new ValidationException(
                    "maxRetries must be positive"
                );
            }

            this.maxRetries = maxRetries;
        }

        void publish(OrderCreatedEvent event) {
            messages.addLast(new Message(event, 0));
        }

        void drain(EventHandler handler) {
            while (!messages.isEmpty()) {
                Message message = messages.removeFirst();
                int attempts = message.attempts() + 1;

                try {
                    handler.handle(message.event());
                } catch (RuntimeException error) {
                    if (attempts >= maxRetries) {
                        deadLetters.add(message.event());
                    } else {
                        messages.addLast(
                            new Message(
                                message.event(),
                                attempts
                            )
                        );
                    }
                }
            }
        }

        int deadLetterCount() {
            return deadLetters.size();
        }
    }

    @FunctionalInterface
    interface EventHandler {
        void handle(OrderCreatedEvent event);
    }

    static final class CustomerService {
        private final CustomerRepository repository;
        private final CacheManager cache;
        private boolean available = true;

        CustomerService(
            CustomerRepository repository,
            CacheManager cache
        ) {
            this.repository = repository;
            this.cache = cache;
        }

        void setAvailable(boolean available) {
            this.available = available;
        }

        Customer getCustomer(int id) {
            if (!available) {
                throw new ServiceUnavailableException(
                    "Customer service unavailable"
                );
            }

            return cache.get(id)
                .orElseGet(() -> repository.findById(id)
                    .map(customer -> {
                        cache.put(customer);
                        return customer;
                    })
                    .orElseThrow(() ->
                        new ValidationException(
                            "Customer " + id + " not found"
                        )
                    ));
        }
    }

    static final class OrderService {
        private final OrderRepository repository;
        private final CustomerService customerService;
        private final EventQueue queue;

        private boolean available = true;

        OrderService(
            OrderRepository repository,
            CustomerService customerService,
            EventQueue queue
        ) {
            this.repository = repository;
            this.customerService = customerService;
            this.queue = queue;
        }

        void setAvailable(boolean available) {
            this.available = available;
        }

        Order createOrder(
            int customerId,
            long amountPaise
        ) {
            if (!available) {
                throw new ServiceUnavailableException(
                    "Order service unavailable"
                );
            }

            customerService.getCustomer(customerId);

            Order order = new Order(
                repository.nextId(),
                customerId,
                amountPaise,
                OrderStatus.CREATED,
                Instant.now()
            );

            repository.save(order);

            queue.publish(
                new OrderCreatedEvent(
                    order.id(),
                    order.customerId(),
                    order.amountPaise()
                )
            );

            return order;
        }
    }

    record ScalingPlan(
        int instances,
        int capacity
    ) {}

    static ScalingPlan planScaling(
        int requestedRps,
        int instanceCapacity
    ) {
        if (requestedRps < 0 || instanceCapacity <= 0) {
            throw new ValidationException(
                "Invalid scaling parameters"
            );
        }

        int instances = Math.max(
            1,
            (requestedRps + instanceCapacity - 1)
                / instanceCapacity
        );

        return new ScalingPlan(
            instances,
            instances * instanceCapacity
        );
    }

    public static void main(String[] args) {
        CustomerRepository customerRepository =
            new CustomerRepository();

        OrderRepository orderRepository =
            new OrderRepository();

        CacheManager cache =
            new CacheManager(100, 60_000);

        EventQueue queue =
            new EventQueue(3);

        CustomerService customerService =
            new CustomerService(
                customerRepository,
                cache
            );

        OrderService orderService =
            new OrderService(
                orderRepository,
                customerService,
                queue
            );

        customerRepository.save(
            new Customer(
                1,
                "Asha",
                CustomerTier.PREMIUM
            )
        );

        customerRepository.save(
            new Customer(
                2,
                "Ravi",
                CustomerTier.STANDARD
            )
        );

        Order order =
            orderService.createOrder(
                1,
                249950
            );

        System.out.println(
            "Created order: " + order
        );

        Customer first =
            customerService.getCustomer(1);

        Customer cached =
            customerService.getCustomer(1);

        System.out.println(
            "Customer: " + first.name()
        );

        System.out.println(
            "Cached customer: " + cached.name()
        );

        System.out.printf(
            "Cache hit ratio: %.2f%n",
            cache.hitRatio()
        );

        System.out.println(
            "Processing asynchronous event:"
        );

        queue.drain(event -> System.out.println(
            "Consumed order.created for order "
            + event.orderId()
        ));

        System.out.println(
            "Dead letters: "
            + queue.deadLetterCount()
        );

        System.out.println(
            "Scaling plans:"
        );

        for (int rps : List.of(
            50,
            100,
            101,
            250,
            1000
        )) {
            System.out.println(
                rps
                + " RPS -> "
                + planScaling(rps, 100)
            );
        }

        System.out.println(
            "Failure isolation:"
        );

        customerService.setAvailable(false);

        try {
            orderService.createOrder(1, 75000);
        } catch (ArchitectureException error) {
            System.out.println(
                "Order rejected: "
                + error.getMessage()
            );
        }

        System.out.println(
            "Customer DB writes="
            + customerRepository.writes()
            + ", reads="
            + customerRepository.reads()
        );

        System.out.println(
            "Order DB writes="
            + orderRepository.writes()
            + ", reads="
            + orderRepository.reads()
        );

        /*
         * Security and production design:
         * - Service APIs should authenticate callers and authorize operations.
         * - Databases should use least-privilege service accounts.
         * - Cache keys must not expose secrets or cross tenant boundaries.
         * - Queue consumers need idempotency because delivery can be repeated.
         * - Distributed transactions should not be assumed from separate
         *   database and queue operations.
         */
    }
}
