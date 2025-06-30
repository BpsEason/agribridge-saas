# AgriBridge System Architecture

The AgriBridge platform is designed with a modular, microservices-based architecture to ensure scalability and extensibility. Below is a high-level overview of the system components.

## Architecture Diagram

```mermaid
graph TD
    A[Client Browser] -->|HTTPS| B[Frontend: Vue 3 + TailwindCSS]
    B -->|API Calls (JWT)| C[API Gateway: FastAPI]
    C --> D(Auth Module)
    C --> E(Product & Order Module)
    C --> F(Financial Ledger Module)
    C --> G(Crawler & Intelligence Module)
    C --> H(Dashboard & ESG Report Module)
    C --> P(IoT Module)
    C --> Q(Blockchain Integration Mock)
    C --> I(Notification Module)
    D --> J(MySQL Database: Multi-Tenant)
    E --> J
    F --> J
    G --> J
    H --> J
    P --> J
    Q --> J
    C --> K(Redis: Caching)
    I --> L(External Services: SMTP/LINE API)
```

## Component Descriptions
- **Frontend**: Built with Vue 3 and TailwindCSS, providing a responsive SPA with ESG and IoT visualizations using Chart.js. Includes full login integration and enhanced data display for all modules.
- **API Gateway**: FastAPI handles all RESTful API requests, with CORS support and robust JWT validation for secure multi-tenant access.
- **Auth Module**: Implements JWT-based authentication with mock RBAC and multi-tenancy support, now explicitly including tenant_id in JWT.
- **Product & Order Module**: Manages product listings and order processing with CRUD endpoints, fully integrated with multi-tenancy.
- **Financial Ledger Module**: Integrates mock payment gateways (Stripe, NewebPay) and tracks financial transactions.
- **Crawler & Intelligence Module**: Scrapes market data and generates dynamic pricing using Pandas and BeautifulSoup.
- **Dashboard & ESG Report Module**: Visualizes ESG metrics for farmers and buyers.
- **IoT Module**: Provides mock endpoints for receiving and retrieving IoT sensor data, now supporting historical data for charting.
- **Notification Module**: Sends notifications via Email (SMTP) and LINE Messaging API, with webhook validation and improved environment variable checks.
- **Blockchain Integration Mock**: A service to mock blockchain transaction recording, with clearer schema for frontend display.
- **Database**: MySQL with multi-tenant schema design (`tenant_id` column) for data isolation. Includes initial data for tenants, farmers, products, and orders.
- **Cache**: Redis for caching ESG reports and other high-frequency data.

## Deployment
- **Docker**: Containerized services for consistent development and production environments, now using multi-stage builds for optimized image sizes.
- **CI/CD**: GitHub Actions for automated testing, linting (with ESLint for frontend), and deployment to VPS or cloud providers, including optional Vercel deployment for the frontend.
