#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

/*
 * Repository-independent API governance case study:
 * a product manager evaluates whether an API request should be accepted.
 *
 * The program models:
 * - REST resources and HTTP methods
 * - authentication
 * - request validation
 * - response status codes
 * - required headers
 * - endpoint permissions
 * - rate limits
 * - optimistic concurrency
 *
 * The implementation uses value-oriented C++ structures and explicit
 * policy evaluation rather than relying on a web framework.
 */

enum class HttpMethod {
    GET,
    POST,
    PATCH,
    DELETE_
};

enum class Role {
    ProductManager,
    Administrator,
    ReadOnly
};

enum class Status {
    OK = 200,
    Created = 201,
    NoContent = 204,
    BadRequest = 400,
    Unauthorized = 401,
    Forbidden = 403,
    NotFound = 404,
    MethodNotAllowed = 405,
    PreconditionFailed = 412,
    Conflict = 409,
    TooManyRequests = 429
};

struct Request {
    HttpMethod method;
    std::string path;
    std::map<std::string, std::string> headers;
    std::map<std::string, std::string> query;
    std::map<std::string, std::string> body;
};

struct Response {
    Status status;
    std::string message;
    std::map<std::string, std::string> headers;
};

struct Product {
    int id;
    std::string name;
    std::string category;
    double price;
    bool active;
    int version;
};

class APIException : public std::runtime_error {
public:
    APIException(Status status, const std::string& message)
        : std::runtime_error(message), status_(status) {}

    Status status() const {
        return status_;
    }

private:
    Status status_;
};

class ProductRepository {
public:
    ProductRepository() {
        products_.emplace(
            1,
            Product{1, "Analytics Pro", "analytics", 49.99, true, 1}
        );
        products_.emplace(
            2,
            Product{2, "Team Workspace", "collaboration", 19.99, true, 1}
        );
    }

    const Product& find(int id) const {
        auto it = products_.find(id);

        if (it == products_.end()) {
            throw APIException(Status::NotFound, "Product not found");
        }

        return it->second;
    }

    Product& findMutable(int id) {
        auto it = products_.find(id);

        if (it == products_.end()) {
            throw APIException(Status::NotFound, "Product not found");
        }

        return it->second;
    }

    int create(
        const std::string& name,
        const std::string& category,
        double price,
        bool active
    ) {
        const int id = next_id_++;
        products_.emplace(
            id,
            Product{id, name, category, price, active, 1}
        );
        return id;
    }

    void erase(int id) {
        if (products_.erase(id) == 0) {
            throw APIException(Status::NotFound, "Product not found");
        }
    }

private:
    std::map<int, Product> products_;
    int next_id_ = 3;
};

class Authenticator {
public:
    Authenticator() {
        credentials_["pm-demo-key"] = Role::ProductManager;
        credentials_["admin-demo-key"] = Role::Administrator;
        credentials_["read-demo-key"] = Role::ReadOnly;
    }

    Role authenticate(const Request& request) const {
        auto header = request.headers.find("Authorization");

        if (header == request.headers.end()) {
            throw APIException(
                Status::Unauthorized,
                "Authorization header is required"
            );
        }

        const std::string prefix = "Bearer ";

        if (header->second.rfind(prefix, 0) != 0) {
            throw APIException(
                Status::Unauthorized,
                "Bearer authentication is required"
            );
        }

        const std::string token = header->second.substr(prefix.size());
        auto credential = credentials_.find(token);

        if (credential == credentials_.end()) {
            throw APIException(
                Status::Unauthorized,
                "Invalid credentials"
            );
        }

        return credential->second;
    }

private:
    std::unordered_map<std::string, Role> credentials_;
};

class RateLimiter {
public:
    bool allow(const std::string& token) {
        const auto now = std::chrono::steady_clock::now();

        auto& timestamps = requests_[token];

        timestamps.erase(
            std::remove_if(
                timestamps.begin(),
                timestamps.end(),
                [now](const auto& timestamp) {
                    return now - timestamp > std::chrono::seconds(60);
                }
            ),
            timestamps.end()
        );

        if (timestamps.size() >= 10) {
            return false;
        }

        timestamps.push_back(now);
        return true;
    }

private:
    using Clock = std::chrono::steady_clock;
    std::unordered_map<std::string, std::vector<Clock::time_point>> requests_;
};

class GovernanceEngine {
public:
    GovernanceEngine()
        : repository_(), authenticator_(), limiter_() {}

    Response evaluate(const Request& request) {
        try {
            const std::string token = bearerToken(request);
            const Role role = authenticator_.authenticate(request);

            if (!limiter_.allow(token)) {
                throw APIException(
                    Status::TooManyRequests,
                    "Rate limit exceeded"
                );
            }

            validateVersionedPath(request.path);

            if (request.path == "/api/v1/products") {
                return evaluateCollection(request, role);
            }

            const int productId = extractId(request.path);

            return evaluateResource(request, role, productId);
        }
        catch (const APIException& error) {
            return Response{
                error.status(),
                error.what(),
                {}
            };
        }
    }

private:
    static std::string bearerToken(const Request& request) {
        auto it = request.headers.find("Authorization");

        if (it == request.headers.end()) {
            throw APIException(
                Status::Unauthorized,
                "Authorization header is required"
            );
        }

        const std::string prefix = "Bearer ";

        if (it->second.rfind(prefix, 0) != 0) {
            throw APIException(
                Status::Unauthorized,
                "Invalid Authorization format"
            );
        }

        return it->second.substr(prefix.size());
    }

    static void validateVersionedPath(const std::string& path) {
        if (path.rfind("/api/v1/products", 0) != 0) {
            throw APIException(
                Status::NotFound,
                "Unknown API resource"
            );
        }
    }

    static int extractId(const std::string& path) {
        const std::string prefix = "/api/v1/products/";

        if (path.rfind(prefix, 0) != 0) {
            throw APIException(
                Status::NotFound,
                "Invalid product resource"
            );
        }

        const std::string idText = path.substr(prefix.size());

        if (idText.empty() ||
            !std::all_of(
                idText.begin(),
                idText.end(),
                [](unsigned char character) {
                    return std::isdigit(character);
                }
            )) {
            throw APIException(
                Status::BadRequest,
                "Product ID must be numeric"
            );
        }

        return std::stoi(idText);
    }

    static bool canWrite(Role role) {
        return role == Role::ProductManager ||
               role == Role::Administrator;
    }

    Response evaluateCollection(
        const Request& request,
        Role role
    ) {
        if (request.method == HttpMethod::GET) {
            return Response{
                Status::OK,
                "Product collection can be returned",
                {
                    {"Content-Type", "application/json"}
                }
            };
        }

        if (request.method == HttpMethod::POST) {
            if (!canWrite(role)) {
                throw APIException(
                    Status::Forbidden,
                    "Write permission required"
                );
            }

            validateCreatePayload(request.body);

            const int id = repository_.create(
                request.body.at("name"),
                request.body.at("category"),
                std::stod(request.body.at("price")),
                request.body.count("active")
                    ? request.body.at("active") == "true"
                    : true
            );

            return Response{
                Status::Created,
                "Product created",
                {
                    {"Location", "/api/v1/products/" + std::to_string(id)}
                }
            };
        }

        throw APIException(
            Status::MethodNotAllowed,
            "Method is not supported on product collection"
        );
    }

    Response evaluateResource(
        const Request& request,
        Role role,
        int productId
    ) {
        const Product& product = repository_.find(productId);

        if (request.method == HttpMethod::GET) {
            return Response{
                Status::OK,
                "Product retrieved",
                {
                    {"ETag", makeETag(product)}
                }
            };
        }

        if (request.method == HttpMethod::PATCH) {
            if (!canWrite(role)) {
                throw APIException(
                    Status::Forbidden,
                    "Write permission required"
                );
            }

            validatePatchPayload(request.body);

            const auto header = request.headers.find("If-Match");

            if (header == request.headers.end()) {
                throw APIException(
                    Status::PreconditionFailed,
                    "If-Match is required for updates"
                );
            }

            if (header->second != makeETag(product)) {
                throw APIException(
                    Status::Conflict,
                    "Stale resource version"
                );
            }

            Product& mutableProduct = repository_.findMutable(productId);

            if (request.body.count("name")) {
                mutableProduct.name = request.body.at("name");
            }

            if (request.body.count("price")) {
                mutableProduct.price =
                    std::stod(request.body.at("price"));
            }

            if (request.body.count("active")) {
                mutableProduct.active =
                    request.body.at("active") == "true";
            }

            ++mutableProduct.version;

            return Response{
                Status::OK,
                "Product updated",
                {
                    {"ETag", makeETag(mutableProduct)}
                }
            };
        }

        if (request.method == HttpMethod::DELETE_) {
            if (role != Role::Administrator) {
                throw APIException(
                    Status::Forbidden,
                    "Administrator permission required"
                );
            }

            repository_.erase(productId);

            return Response{
                Status::NoContent,
                "Product deleted",
                {}
            };
        }

        throw APIException(
            Status::MethodNotAllowed,
            "Method is not supported on product resource"
        );
    }

    static void validateCreatePayload(
        const std::map<std::string, std::string>& body
    ) {
        if (!body.count("name") ||
            !body.count("category") ||
            !body.count("price")) {
            throw APIException(
                Status::BadRequest,
                "name, category and price are required"
            );
        }

        validateCommonFields(body);
    }

    static void validatePatchPayload(
        const std::map<std::string, std::string>& body
    ) {
        if (body.empty()) {
            throw APIException(
                Status::BadRequest,
                "PATCH must contain at least one field"
            );
        }

        validateCommonFields(body);
    }

    static void validateCommonFields(
        const std::map<std::string, std::string>& body
    ) {
        static const std::vector<std::string> allowed{
            "name",
            "category",
            "price",
            "active"
        };

        for (const auto& [key, value] : body) {
            if (std::find(
                    allowed.begin(),
                    allowed.end(),
                    key
                ) == allowed.end()) {
                throw APIException(
                    Status::BadRequest,
                    "Unknown field: " + key
                );
            }

            if ((key == "name" || key == "category") &&
                value.empty()) {
                throw APIException(
                    Status::BadRequest,
                    key + " cannot be empty"
                );
            }

            if (key == "price") {
                try {
                    if (std::stod(value) < 0) {
                        throw APIException(
                            Status::BadRequest,
                            "price cannot be negative"
                        );
                    }
                }
                catch (const std::invalid_argument&) {
                    throw APIException(
                        Status::BadRequest,
                        "price must be numeric"
                    );
                }
            }

            if (key == "active" &&
                value != "true" &&
                value != "false") {
                throw APIException(
                    Status::BadRequest,
                    "active must be true or false"
                );
            }
        }
    }

    static std::string makeETag(const Product& product) {
        std::ostringstream stream;
        stream << '"' << product.id
               << '-' << product.version << '"';
        return stream.str();
    }

    ProductRepository repository_;
    Authenticator authenticator_;
    RateLimiter limiter_;
};

static std::string statusText(Status status) {
    return std::to_string(static_cast<int>(status));
}

static void printResponse(const Response& response) {
    std::cout << "HTTP " << statusText(response.status)
              << " | " << response.message << '\n';

    for (const auto& [key, value] : response.headers) {
        std::cout << key << ": " << value << '\n';
    }

    std::cout << '\n';
}

int main() {
    GovernanceEngine engine;

    Request listRequest{
        HttpMethod::GET,
        "/api/v1/products",
        {{"Authorization", "Bearer pm-demo-key"}},
        {},
        {}
    };

    Request createRequest{
        HttpMethod::POST,
        "/api/v1/products",
        {{"Authorization", "Bearer pm-demo-key"}},
        {},
        {
            {"name", "Customer Insights"},
            {"category", "analytics"},
            {"price", "79.00"},
            {"active", "true"}
        }
    };

    Request unauthorizedDelete{
        HttpMethod::DELETE_,
        "/api/v1/products/1",
        {{"Authorization", "Bearer pm-demo-key"}},
        {},
        {}
    };

    Request readRequest{
        HttpMethod::GET,
        "/api/v1/products/1",
        {{"Authorization", "Bearer read-demo-key"}},
        {},
        {}
    };

    printResponse(engine.evaluate(listRequest));
    printResponse(engine.evaluate(createRequest));
    printResponse(engine.evaluate(unauthorizedDelete));
    printResponse(engine.evaluate(readRequest));

    // This request intentionally demonstrates stale-version rejection.
    Request staleUpdate{
        HttpMethod::PATCH,
        "/api/v1/products/1",
        {
            {"Authorization", "Bearer pm-demo-key"},
            {"If-Match", "\"1-0\""}
        },
        {},
        {
            {"price", "99.00"}
        }
    };

    printResponse(engine.evaluate(staleUpdate));

    return 0;
}
