# AgriBridge Database Schema

The AgriBridge platform utilizes a MySQL database with a multi-tenant design, where each tenant's data is logically separated using a `tenant_id` column in relevant tables.

## Schema Diagram

```mermaid
erDiagram
    TENANTS ||--o{ FARMERS : 擁有
    TENANTS ||--o{ PRODUCTS : 擁有
    TENANTS ||--o{ ORDERS : 擁有
    FARMERS ||--o{ PRODUCTS : 提供

    TENANTS {
        int id PK
        string name UK
    }

    FARMERS {
        int id PK
        int tenant_id FK
        string name INDEX
        string location
        float esg_score
        float total_sales
    }

    PRODUCTS {
        int id PK
        int tenant_id FK
        string name
        float price
        int farmer_id FK
    }

    ORDERS {
        int id PK
        int tenant_id FK
        int product_id FK
        int quantity
        float total_price
        int buyer_id
        string status
    }
```

## Table Descriptions

-   **`tenants`**: Stores information about each tenant (e.g., organization, farm conglomerate).
    -   `id`: Unique identifier for the tenant.
    -   `name`: Name of the tenant (must be unique).
-   **`farmers`**: Stores farmer profiles. Each farmer belongs to a specific tenant.
    -   `id`: Unique identifier for the farmer.
    -   `tenant_id`: Foreign key referencing the `tenants` table, enforcing multi-tenancy.
    -   `name`: Name of the farmer.
    -   `location`: Geographical location of the farmer.
    -   `esg_score`: Environmental, Social, and Governance score.
    -   `total_sales`: Total sales volume for the farmer.
-   **`products`**: Stores details about agricultural products. Each product belongs to a specific tenant and is associated with a farmer.
    -   `id`: Unique identifier for the product.
    -   `tenant_id`: Foreign key referencing the `tenants` table.
    -   `name`: Name of the product.
    -   `price`: Price of the product.
    -   `farmer_id`: Foreign key referencing the `farmers` table.
-   **`orders`**: Records customer orders for products. Each order belongs to a specific tenant and references a product.
    -   `id`: Unique identifier for the order.
    -   `tenant_id`: Foreign key referencing the `tenants` table.
    -   `product_id`: Foreign key referencing the `products` table.
    -   `quantity`: Quantity of the product ordered.
    -   `total_price`: Total price of the order.
    -   `buyer_id`: Identifier for the buyer (mocked in this version).
    -   `status`: Current status of the order (e.g., 'pending', 'completed', 'shipped').

### Multi-Tenancy Implementation
The `tenant_id` column in `farmers`, `products`, and `orders` tables ensures that data is logically partitioned and accessible only by the respective tenant, providing data isolation crucial for a SaaS platform.
