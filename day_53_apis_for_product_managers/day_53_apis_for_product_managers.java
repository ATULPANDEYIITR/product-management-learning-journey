import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Enterprise Product API Governance Model.
 *
 * The program represents API behavior as explicit domain objects and
 * services rather than as a web-framework tutorial.
 *
 * It models:
 * - REST resources
 * - HTTP operations
 * - authentication and authorization
 * - request validation
 * - reviewable API policy rules
 * - optimistic concurrency
 * - rate limits
 * - explicit state transitions
 * - API documentation metadata
 */
public class ProductApiGovernance {

    enum HttpMethod {
        GET, POST, PATCH, DELETE
    }

    enum Role {
        PRODUCT_MANAGER,
        ADMINISTRATOR,
        READ_ONLY
    }

    record Principal(String token, Role role) {}

    record APIRequest(
            HttpMethod method,
            String path,
            Map<String, String> headers,
            Map<String, String> query,
            Map<String, Object> body) {

        APIRequest {
            headers = Map.copyOf(headers);
            query = Map.copyOf(query);
            body = Map.copyOf(body);
        }
    }

    record APIResponse(
            int status,
            String message,
            Map<String, String> headers,
            Object body) {

        APIResponse {
            headers = Map.copyOf(headers);
        }

        static APIResponse of(
                int status,
                String message) {
            return new APIResponse(
                    status,
                    message,
                    Map.of(),
                    null
            );
        }
    }

    record Product(
            int id,
            String name,
            String category,
            double price,
            boolean active,
            int version,
            Instant updatedAt) {

        Product withChanges(Map<String, Object> changes) {
            return new Product(
                    id,
                    changes.containsKey("name")
                            ? (String) changes.get("name")
                            : name,
                    changes.containsKey("category")
                            ? (String) changes.get("category")
                            : category,
                    changes.containsKey("price")
                            ? ((Number) changes.get("price")).doubleValue()
                            : price,
                    changes.containsKey("active")
                            ? (Boolean) changes.get("active")
                            : active,
                    version + 1,
                    Instant.now()
            );
        }
    }

    record EndpointPolicy(
            HttpMethod method,
            String path,
            Set<Role> allowedRoles,
            String description) {}

    static class APIException extends RuntimeException {
        private final int status;

        APIException(int status, String message) {
            super(message);
            this.status = status;
        }

        int status() {
            return status;
        }
    }

    static final class AuthenticationService {

        private final Map<String, Role> credentials = Map.of(
                "pm-demo-key", Role.PRODUCT_MANAGER,
                "admin-demo-key", Role.ADMINISTRATOR,
                "read-demo-key", Role.READ_ONLY
        );

        Principal authenticate(APIRequest request) {
            String authorization = request.headers()
                    .getOrDefault("Authorization", "");

            if (!authorization.startsWith("Bearer ")) {
                throw new APIException(
                        401,
                        "Bearer authentication is required"
                );
            }

            String token = authorization.substring("Bearer ".length())
                    .trim();

            Role role = credentials.get(token);

            if (role == null) {
                throw new APIException(
                        401,
                        "Invalid API credentials"
                );
            }

            return new Principal(token, role);
        }
    }

    static final class ProductRepository {

        private final Map<Integer, Product> products =
                new ConcurrentHashMap<>();

        private final AtomicInteger sequence =
                new AtomicInteger(3);

        ProductRepository() {
            products.put(
                    1,
                    new Product(
                            1,
                            "Analytics Pro",
                            "analytics",
                            49.99,
                            true,
                            1,
                            Instant.now()
                    )
            );

            products.put(
                    2,
                    new Product(
                            2,
                            "Team Workspace",
                            "collaboration",
                            19.99,
                            true,
                            1,
                            Instant.now()
                    )
            );
        }

        Optional<Product> find(int id) {
            return Optional.ofNullable(products.get(id));
        }

        Product require(int id) {
            return find(id).orElseThrow(
                    () -> new APIException(
                            404,
                            "Product not found"
                    )
            );
        }

        Product save(Product product) {
            products.put(product.id(), product);
            return product;
        }

        Product create(
                String name,
                String category,
                double price,
                boolean active) {

            int id = sequence.getAndIncrement();

            Product product = new Product(
                    id,
                    name,
                    category,
                    price,
                    active,
                    1,
                    Instant.now()
            );

            products.put(id, product);
            return product;
        }

        void delete(int id) {
            if (products.remove(id) == null) {
                throw new APIException(
                        404,
                        "Product not found"
                );
            }
        }

        List<Product> findAll() {
            return products.values()
                    .stream()
                    .sorted(Comparator.comparing(Product::id))
                    .toList();
        }
    }

    static final class RateLimitService {

        private final Map<String, List<Long>> requests =
                new ConcurrentHashMap<>();

        private static final int MAX_REQUESTS = 20;
        private static final long WINDOW_MS = 60_000L;

        void check(String token) {
            long now = System.currentTimeMillis();

            List<Long> timestamps = requests.computeIfAbsent(
                    token,
                    ignored -> new ArrayList<>()
            );

            synchronized (timestamps) {
                timestamps.removeIf(
                        timestamp -> now - timestamp >= WINDOW_MS
                );

                if (timestamps.size() >= MAX_REQUESTS) {
                    throw new APIException(
                            429,
                            "Rate limit exceeded"
                    );
                }

                timestamps.add(now);
            }
        }
    }

    static final class ValidationService {

        private static final Set<String> ALLOWED_FIELDS =
                Set.of("name", "category", "price", "active");

        void validate(
                Map<String, Object> body,
                boolean partial) {

            if (!partial) {
                for (String required :
                        List.of("name", "category", "price")) {

                    if (!body.containsKey(required)) {
                        throw new APIException(
                                400,
                                "Missing required field: " + required
                        );
                    }
                }
            }

            for (String field : body.keySet()) {
                if (!ALLOWED_FIELDS.contains(field)) {
                    throw new APIException(
                            400,
                            "Unknown field: " + field
                    );
                }
            }

            if (body.containsKey("name")) {
                requireText(body.get("name"), "name");
            }

            if (body.containsKey("category")) {
                requireText(body.get("category"), "category");
            }

            if (body.containsKey("price")) {
                Object value = body.get("price");

                if (!(value instanceof Number number) ||
                        !Double.isFinite(number.doubleValue()) ||
                        number.doubleValue() < 0) {
                    throw new APIException(
                            400,
                            "price must be a non-negative number"
                    );
                }
            }

            if (body.containsKey("active") &&
                    !(body.get("active") instanceof Boolean)) {

                throw new APIException(
                        400,
                        "active must be boolean"
                );
            }
        }

        private void requireText(
                Object value,
                String field) {

            if (!(value instanceof String text) ||
                    text.trim().isEmpty()) {

                throw new APIException(
                        400,
                        field + " must be non-empty"
                );
            }
        }
    }

    static final class ProductApiService {

        private final AuthenticationService authentication;
        private final ProductRepository repository;
        private final ValidationService validation;
        private final RateLimitService rateLimit;

        ProductApiService() {
            authentication = new AuthenticationService();
            repository = new ProductRepository();
            validation = new ValidationService();
            rateLimit = new RateLimitService();
        }

        APIResponse handle(APIRequest request) {
            try {
                Principal principal =
                        authentication.authenticate(request);

                rateLimit.check(principal.token());

                if (request.path().equals("/api/v1/products")) {
                    return collectionOperation(
                            request,
                            principal.role()
                    );
                }

                int id = parseId(request.path());

                return resourceOperation(
                        request,
                        principal.role(),
                        id
                );

            } catch (APIException error) {
                return APIResponse.of(
                        error.status(),
                        error.getMessage()
                );
            }
        }

        private APIResponse collectionOperation(
                APIRequest request,
                Role role) {

            if (request.method() == HttpMethod.GET) {
                List<Product> result = repository.findAll();

                String category =
                        request.query().get("category");

                if (category != null) {
                    result = result.stream()
                            .filter(product ->
                                    product.category()
                                            .equalsIgnoreCase(category))
                            .toList();
                }

                return new APIResponse(
                        200,
                        "Products retrieved",
                        Map.of("Content-Type", "application/json"),
                        result
                );
            }

            if (request.method() == HttpMethod.POST) {
                requireWriteRole(role);
                validation.validate(request.body(), false);

                String name =
                        ((String) request.body().get("name")).trim();

                String category =
                        ((String) request.body().get("category"))
                                .trim()
                                .toLowerCase(Locale.ROOT);

                double price =
                        ((Number) request.body().get("price"))
                                .doubleValue();

                boolean active =
                        request.body().containsKey("active")
                                ? (Boolean) request.body().get("active")
                                : true;

                Product product = repository.create(
                        name,
                        category,
                        price,
                        active
                );

                return new APIResponse(
                        201,
                        "Product created",
                        Map.of(
                                "Location",
                                "/api/v1/products/" + product.id(),
                                "ETag",
                                etag(product)
                        ),
                        product
                );
            }

            throw new APIException(
                    405,
                    "Method is not supported"
            );
        }

        private APIResponse resourceOperation(
                APIRequest request,
                Role role,
                int id) {

            Product product = repository.require(id);

            return switch (request.method()) {
                case GET -> new APIResponse(
                        200,
                        "Product retrieved",
                        Map.of(
                                "Content-Type",
                                "application/json",
                                "ETag",
                                etag(product)
                        ),
                        product
                );

                case PATCH -> update(request, role, product);

                case DELETE -> delete(role, product);

                case POST -> throw new APIException(
                        405,
                        "POST is not supported for an individual product"
                );
            };
        }

        private APIResponse update(
                APIRequest request,
                Role role,
                Product current) {

            requireWriteRole(role);

            validation.validate(request.body(), true);

            String expectedETag =
                    request.headers().get("If-Match");

            if (expectedETag == null) {
                throw new APIException(
                        412,
                        "If-Match header is required"
                );
            }

            if (!expectedETag.equals(etag(current))) {
                throw new APIException(
                        412,
                        "Resource version is stale"
                );
            }

            Map<String, Object> normalized =
                    new HashMap<>(request.body());

            if (normalized.containsKey("name")) {
                normalized.put(
                        "name",
                        ((String) normalized.get("name")).trim()
                );
            }

            if (normalized.containsKey("category")) {
                normalized.put(
                        "category",
                        ((String) normalized.get("category"))
                                .trim()
                                .toLowerCase(Locale.ROOT)
                );
            }

            Product updated = current.withChanges(normalized);
            repository.save(updated);

            return new APIResponse(
                    200,
                    "Product updated",
                    Map.of(
                            "Content-Type",
                            "application/json",
                            "ETag",
                            etag(updated)
                    ),
                    updated
            );
        }

        private APIResponse delete(
                Role role,
                Product product) {

            if (role != Role.ADMINISTRATOR) {
                throw new APIException(
                        403,
                        "Administrator role required"
                );
            }

            repository.delete(product.id());

            return APIResponse.of(
                    204,
                    "Product deleted"
            );
        }

        private static void requireWriteRole(Role role) {
            if (role != Role.PRODUCT_MANAGER &&
                    role != Role.ADMINISTRATOR) {

                throw new APIException(
                        403,
                        "Write permission required"
                );
            }
        }

        private static int parseId(String path) {
            String prefix = "/api/v1/products/";

            if (!path.startsWith(prefix)) {
                throw new APIException(
                        404,
                        "Endpoint not found"
                );
            }

            try {
                int id = Integer.parseInt(
                        path.substring(prefix.length())
                );

                if (id <= 0) {
                    throw new NumberFormatException();
                }

                return id;

            } catch (NumberFormatException error) {
                throw new APIException(
                        400,
                        "Product ID must be positive integer"
                );
            }
        }

        private static String etag(Product product) {
            return "\"" + product.id() +
                    "-" + product.version() + "\"";
        }
    }

    static final List<EndpointPolicy> DOCUMENTATION =
            List.of(
                    new EndpointPolicy(
                            HttpMethod.GET,
                            "/api/v1/products",
                            Set.of(
                                    Role.PRODUCT_MANAGER,
                                    Role.ADMINISTRATOR,
                                    Role.READ_ONLY
                            ),
                            "List products"
                    ),
                    new EndpointPolicy(
                            HttpMethod.POST,
                            "/api/v1/products",
                            Set.of(
                                    Role.PRODUCT_MANAGER,
                                    Role.ADMINISTRATOR
                            ),
                            "Create a product"
                    ),
                    new EndpointPolicy(
                            HttpMethod.GET,
                            "/api/v1/products/{id}",
                            Set.of(
                                    Role.PRODUCT_MANAGER,
                                    Role.ADMINISTRATOR,
                                    Role.READ_ONLY
                            ),
                            "Retrieve one product"
                    ),
                    new EndpointPolicy(
                            HttpMethod.PATCH,
                            "/api/v1/products/{id}",
                            Set.of(
                                    Role.PRODUCT_MANAGER,
                                    Role.ADMINISTRATOR
                            ),
                            "Update a product with optimistic concurrency"
                    ),
                    new EndpointPolicy(
                            HttpMethod.DELETE,
                            "/api/v1/products/{id}",
                            Set.of(Role.ADMINISTRATOR),
                            "Delete a product"
                    )
            );

    private static APIRequest request(
            HttpMethod method,
            String path,
            String token,
            Map<String, Object> body) {

        return new APIRequest(
                method,
                path,
                Map.of("Authorization", "Bearer " + token),
                Map.of(),
                body
        );
    }

    public static void main(String[] args) {
        ProductApiService service =
                new ProductApiService();

        APIResponse list = service.handle(
                request(
                        HttpMethod.GET,
                        "/api/v1/products",
                        "read-demo-key",
                        Map.of()
                )
        );

        print(list);

        APIResponse created = service.handle(
                request(
                        HttpMethod.POST,
                        "/api/v1/products",
                        "pm-demo-key",
                        Map.of(
                                "name", "Customer Insights",
                                "category", "analytics",
                                "price", 79.0
                        )
                )
        );

        print(created);

        APIResponse firstRead = service.handle(
                request(
                        HttpMethod.GET,
                        "/api/v1/products/1",
                        "pm-demo-key",
                        Map.of()
                )
        );

        print(firstRead);

        String currentETag =
                firstRead.headers().get("ETag");

        APIRequest update = new APIRequest(
                HttpMethod.PATCH,
                "/api/v1/products/1",
                Map.of(
                        "Authorization",
                        "Bearer pm-demo-key",
                        "If-Match",
                        currentETag
                ),
                Map.of(),
                Map.of("price", 59.99)
        );

        print(service.handle(update));

        APIRequest unauthorizedDelete = request(
                HttpMethod.DELETE,
                "/api/v1/products/1",
                "pm-demo-key",
                Map.of()
        );

        print(service.handle(unauthorizedDelete));

        System.out.println("\nDocumented endpoint policies:");

        DOCUMENTATION.forEach(policy ->
                System.out.println(
                        policy.method() +
                        " " +
                        policy.path() +
                        " -> " +
                        policy.description() +
                        " | roles=" +
                        policy.allowedRoles()
                )
        );
    }

    private static void print(APIResponse response) {
        System.out.println(
                "HTTP " +
                response.status() +
                " | " +
                response.message()
        );

        response.headers().forEach(
                (key, value) ->
                        System.out.println(key + ": " + value)
        );

        if (response.body() != null) {
            System.out.println(response.body());
        }

        System.out.println();
    }
}
