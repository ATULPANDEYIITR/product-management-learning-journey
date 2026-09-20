<!-- File: README.md -->
# Customer Journey Mapping Lab

## Topic

Customer journey mapping is a structured method for describing a customer's experience across a sequence of stages. This project models seven common stages:

- Awareness
- Consideration
- Purchase
- Onboarding
- Usage
- Retention
- Advocacy

The repository demonstrates how a journey map can be represented as structured data, analyzed programmatically, exposed through an API, displayed in a browser, and processed through a native C++ implementation.

## Project purpose

A journey map is more than a timeline of customer actions. A useful map connects several dimensions:

- The customer persona
- The scenario being studied
- The customer's goal
- Customer actions
- Customer thoughts
- Customer emotions
- Business touchpoints
- Customer pain points
- Improvement opportunities
- Customer effort
- Customer sentiment

The project turns those concepts into executable software.

## Repository structure

The repository contains:

- `backend/app/main.py` - FastAPI application and journey analysis logic
- `backend/tests/test_main.py` - API and validation tests
- `frontend/index.html` - browser interface
- `frontend/app.js` - browser state management and API communication
- `frontend/style.css` - responsive interface styling
- `cpp/src/journey_analyzer.cpp` - C++ journey analysis implementation
- `cpp/CMakeLists.txt` - C++ build configuration
- `openapi.yaml` - API contract
- `Dockerfile` - production-oriented application container
- `compose.yaml` - local container orchestration
- `.github/workflows/ci.yml` - automated validation
- `pyproject.toml` - Python dependencies and tooling configuration

## Fundamental concepts

### Persona

A persona represents the customer type whose experience is being mapped.

A persona should be specific enough to distinguish one customer group from another. It can contain demographic, behavioral, professional, or contextual characteristics when those characteristics are relevant to the journey.

A journey should not assume that every customer has the same experience.

### Scenario

The scenario defines the situation being investigated.

Examples include:

- A new customer evaluating a SaaS product
- An existing customer renewing a subscription
- A customer contacting support after a failed transaction
- A customer adopting a newly purchased device

The same persona can have different journeys for different scenarios.

### Journey stage

A stage groups related customer activity.

This project uses a seven-stage model:

1. Awareness
2. Consideration
3. Purchase
4. Onboarding
5. Usage
6. Retention
7. Advocacy

These stages are a practical model rather than a universal rule. Some organizations use different names, combine stages, split stages into smaller units, or model non-linear journeys.

### Awareness

The customer becomes aware of a problem, need, product, company, or possible solution.

Typical activities include:

- Search
- Social discovery
- Advertising exposure
- Word-of-mouth discovery
- Content consumption

Useful questions include:

- What triggered awareness?
- What information is available?
- What does the customer already know?
- Which channels create the first interaction?

### Consideration

The customer evaluates possible solutions.

Typical activities include:

- Comparing alternatives
- Reading reviews
- Watching demonstrations
- Checking documentation
- Comparing features
- Asking colleagues or friends

The key concern is usually whether the proposed solution is appropriate for the customer's problem.

### Purchase

The customer commits to a transaction.

The journey may include:

- Pricing
- Plan selection
- Checkout
- Payment
- Contract acceptance
- Confirmation

Purchase friction can result from unclear pricing, unexpected requirements, poor error handling, or lack of trust.

### Onboarding

The customer attempts to become capable of using the product.

Examples include:

- Account creation
- Initial configuration
- Importing data
- Tutorials
- Setup checklists
- First successful task

A purchase does not automatically mean that the customer has received value.

### Usage

The customer incorporates the product or service into real activity.

The map should identify:

- Core tasks
- Frequency of use
- Important features
- Friction
- Support interactions
- Moments where value is experienced

### Retention

The customer decides whether continued use is worthwhile.

Retention can involve:

- Renewal
- Repeated purchases
- Subscription continuation
- Account expansion
- Reduced usage
- Cancellation consideration

Retention is affected by perceived value, effort, reliability, switching costs, and unresolved problems.

### Advocacy

The customer voluntarily recommends or promotes the product.

Examples include:

- Referrals
- Reviews
- Testimonials
- Community participation
- Case studies
- Recommendations to colleagues

Advocacy should be treated as an observed customer behavior rather than an assumption.

## Touchpoints

A touchpoint is an interaction between the customer and an organization, product, service, or communication channel.

Examples:

- Search engine
- Website
- Mobile application
- Sales call
- Email
- Store
- Customer support
- Payment system
- Product documentation
- Social media
- Referral

One stage can contain multiple touchpoints.

## Sentiment

The project represents touchpoint sentiment using a scale from `-5` to `5`.

- `-5` represents strongly negative sentiment
- `0` represents neutral sentiment
- `5` represents strongly positive sentiment

This numerical value is a modeling device. It does not claim that human emotion can be measured with scientific precision using a single number.

## Effort

Touchpoint effort uses a scale from `1` to `5`.

A low value represents relatively low customer effort. A high value represents relatively high effort.

Effort can represent cognitive, physical, procedural, or time-related friction depending on the research method.

## Frequency

Frequency uses a scale from `1` to `5` to represent how often a touchpoint occurs within the mapped scenario.

Frequency should be defined consistently within a particular study.

## Pain points

Pain points identify observed or reported sources of customer difficulty.

Examples:

- Confusing pricing
- Repeated data entry
- Long waiting times
- Missing information
- Difficult navigation
- Failed payments
- Poor error messages

A pain point should be connected to evidence whenever the journey map is used for real product decisions.

## Opportunities

An opportunity describes a possible area for improvement.

Examples:

- Simplify checkout
- Improve onboarding instructions
- Provide clearer pricing explanations
- Reduce repeated data entry
- Improve support discoverability

An opportunity is not automatically a validated solution. It identifies an area that may deserve investigation.

## Journey-map data model

The main object is `JourneyMap`.

It contains:

- `persona`
- `scenario`
- `stages`

Each `JourneyStage` contains customer-centered information and a collection of `Touchpoint` objects.

A `Touchpoint` contains:

- `channel`
- `description`
- `sentiment`
- `effort`
- `frequency`

This structure allows a visual map to be converted into machine-readable information.

## Architecture

The repository uses three implementation layers.

### Browser

The browser application collects journey information and displays the seven journey stages.

`frontend/app.js` maintains the browser state and sends the complete journey to the backend.

### Python API

FastAPI validates the submitted journey and calculates descriptive metrics.

The API performs:

- Schema validation
- Touchpoint aggregation
- Sentiment calculation
- Effort calculation
- Pain-point counting
- Opportunity counting
- Channel-frequency counting
- Stage-level sentiment comparison

### C++ analysis program

The C++ program demonstrates that the core analytical concepts can also be implemented using a compiled language.

It uses standard library containers and algorithms instead of third-party libraries.

## Python implementation

The Python implementation uses Pydantic models to define the data contract.

For example, `Touchpoint` restricts sentiment to `-5` through `5`, effort to `1` through `5`, and frequency to `1` through `5`.

FastAPI automatically converts those model definitions into request validation behavior and API documentation.

The analysis function flattens all touchpoints from all stages before calculating global metrics.

This is a useful example of separating:

1. Input representation
2. Validation
3. Transformation
4. Aggregation
5. Output representation

## JavaScript implementation

The browser application uses standard JavaScript modules and DOM APIs.

The application keeps a state object containing all seven stages.

When the user changes an input, the corresponding state value is updated.

The `analyzeJourney` function uses `fetch()` to send JSON to:

`POST /api/journeys/analyze`

The server response is then rendered as analysis metrics.

The browser intentionally does not contain the authoritative analysis algorithm. This keeps the API responsible for validating and processing submitted data.

## C++ implementation

The C++ implementation represents touchpoints and stages with `struct` types and uses a `JourneyAnalyzer` class for analysis.

The implementation demonstrates:

- `std::vector`
- `std::map`
- `std::accumulate`
- Range-based loops
- Structured bindings
- Exception handling
- Input validation
- Resource-safe standard containers

The application calculates average sentiment, average effort, total touchpoints, and channel frequency.

The analysis has linear time complexity relative to the number of touchpoints for the main aggregation operations.

## API

The service exposes two endpoints.

### Health endpoint

`GET /health`

Response:

`{"status":"ok"}`

### Journey analysis endpoint

`POST /api/journeys/analyze`

The request body contains:

- Persona
- Scenario
- Stages
- Touchpoints

The response contains:

- Average sentiment
- Average effort
- Total touchpoints
- Pain-point count
- Opportunity count
- Strongest stage by average sentiment
- Weakest stage by average sentiment
- Channel frequency

The OpenAPI contract is stored in `openapi.yaml`.

FastAPI also exposes its interactive documentation when the service is running at `http://localhost:8000/docs`.

## Validation

Validation prevents invalid analytical data from entering the application.

Examples include:

- Empty persona values are rejected.
- Empty scenarios are rejected.
- Unknown stage names are rejected.
- Sentiment outside `-5` to `5` is rejected.
- Effort outside `1` to `5` is rejected.
- Frequency outside `1` to `5` is rejected.
- A journey must contain at least one stage.

Validation is important because analytical output is only useful when the input data follows a known structure.

## Error handling

FastAPI returns validation errors when request data violates the defined schema.

The frontend checks HTTP status codes and displays a readable error message.

The C++ application catches validation exceptions and returns a non-zero process status when invalid data is encountered.

## Testing

Install development dependencies with:

`pip install -e ".[dev]"`

Run the Python test suite with:

`pytest`

The tests cover:

- Health behavior
- Successful journey analysis
- Invalid sentiment
- Missing required fields

The test suite uses FastAPI's test client and does not require a running server.

## Running locally

Create a virtual environment:

`python -m venv .venv`

Activate it on Windows PowerShell:

`.venv\Scripts\Activate.ps1`

Activate it on Linux or macOS:

`source .venv/bin/activate`

Install the project:

`pip install -e ".[dev]"`

Start the API:

`uvicorn app.main:app --app-dir backend --reload`

The API is available at `http://localhost:8000`.

The browser interface can be opened directly from `frontend/index.html` for basic static inspection, but the Analyze Journey button expects the API to be available at the same origin.

For an integrated local experience, serve the frontend through a web server that proxies `/api` to the FastAPI service.

## Docker

Build the image:

`docker build -t customer-journey-mapping .`

Run the container:

`docker run --rm -p 8000:8000 customer-journey-mapping`

The health endpoint is then available at `http://localhost:8000/health`.

Compose can also be used:

`docker compose up --build`

The container runs the API using a non-root user.

## C++ build

Configure the project:

`cmake -S cpp -B cpp/build`

Build it:

`cmake --build cpp/build --config Release`

On Linux, the resulting executable is normally:

`cpp/build/customer_journey_analyzer`

Run it:

`./cpp/build/customer_journey_analyzer`

On Windows with a multi-configuration generator, the executable can be located under the corresponding configuration directory.

## CI/CD

The GitHub Actions workflow performs three independent checks.

The Python job:

- Installs Python 3.11
- Installs project dependencies
- Runs Ruff
- Runs pytest

The C++ job:

- Configures CMake
- Builds the C++ application

The frontend job:

- Installs Node.js
- Runs Node's JavaScript syntax checker

No credentials are required by the workflow.

## Production considerations

A production journey-mapping system would normally require stronger controls around identity, authorization, data retention, audit logging, privacy, and research evidence.

Journey maps can contain sensitive customer research. Real deployments should classify the information being collected and apply appropriate access controls.

The demonstration API currently allows unrestricted cross-origin requests and does not implement authentication. Those settings simplify local education and should not automatically be copied into a public production deployment.

## Security considerations

The project avoids hard-coded credentials.

Input validation is performed at the API boundary.

The Docker container runs as a non-root user.

The application does not log submitted journey contents.

A production system should also consider:

- Authentication
- Authorization
- Rate limiting
- HTTPS
- CSRF protections where applicable
- Security headers
- Audit logging
- Data encryption
- Secure secret storage
- Dependency scanning
- Controlled CORS configuration
- Privacy requirements for customer research

## Performance considerations

The core aggregation operations are linear with respect to the number of touchpoints.

If there are `n` touchpoints, calculating the global averages requires approximately `O(n)` processing time.

Channel counting also requires `O(n)` expected map operations.

Memory usage is proportional to the number of touchpoints retained in the request.

For very large research datasets, a production system could use persistent storage, database indexes, pagination, batch processing, and precomputed analytical aggregates.

## Data quality considerations

A journey map is only as reliable as the research behind it.

Potential evidence sources include:

- Interviews
- Usability studies
- Support records
- Product analytics
- Surveys
- Transaction data
- Customer feedback
- Session observations

A map based entirely on internal assumptions should be distinguished from one supported by direct customer evidence.

## Common mistakes

### Treating the journey as strictly linear

Customers can move backward, skip stages, repeat stages, or interact with multiple channels simultaneously.

### Mapping the organization instead of the customer

A map should describe what the customer experiences rather than merely listing internal departments.

### Confusing touchpoints with stages

A stage is a broader part of the journey. A touchpoint is an interaction occurring within that stage.

### Recording solutions instead of problems

An opportunity should remain connected to an observed problem or unmet need.

### Using unsupported emotional assumptions

Customer emotions should ideally come from research rather than internal guesses.

### Ignoring post-purchase behavior

The experience continues after the transaction. Onboarding, usage, retention, and advocacy can expose problems that are invisible during acquisition.

## Limitations

This implementation is an educational reference rather than a complete commercial journey-mapping platform.

It does not provide:

- Multi-user collaboration
- Persistent database storage
- Authentication
- Role-based access
- Real-time collaborative editing
- Drag-and-drop visual canvas editing
- Research evidence management
- Version history
- Advanced analytics
- Production-grade observability

The numerical sentiment and effort scales are simplified representations designed for structured analysis.

## Trade-offs

A structured JSON model makes journey information easy to validate and analyze, but it does not capture every nuance of a visual collaborative board.

A browser application provides accessibility and simplicity, while a dedicated canvas system can represent complex relationships more visually.

The Python API favors rapid development and strong validation. The C++ implementation demonstrates lower-level implementation techniques and explicit control over data structures and execution.

The repository deliberately keeps persistent storage out of the core demonstration so that the customer journey model can be understood before database concerns are introduced.
