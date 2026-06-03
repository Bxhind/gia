CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'manager',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS partner_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS partners (
    id SERIAL PRIMARY KEY,
    partner_type_id INTEGER NOT NULL REFERENCES partner_types(id),
    name VARCHAR(255) NOT NULL,
    legal_address TEXT NOT NULL,
    inn VARCHAR(20) NOT NULL,
    director_full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 0),
    logo_path TEXT
);

CREATE TABLE IF NOT EXISTS product_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    coefficient NUMERIC(10, 4) NOT NULL CHECK (coefficient > 0)
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    article VARCHAR(100) UNIQUE,
    product_type_id INTEGER NOT NULL REFERENCES product_types(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    min_partner_price NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS sales_history (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER NOT NULL REFERENCES partners(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    sale_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS material_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    defect_percent NUMERIC(5, 2) NOT NULL CHECK (defect_percent >= 0)
);

CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    material_type_id INTEGER NOT NULL REFERENCES material_types(id),
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    quantity_in_stock NUMERIC(12, 3) NOT NULL DEFAULT 0,
    min_quantity NUMERIC(12, 3) NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_partners_name ON partners(name);
CREATE INDEX IF NOT EXISTS ix_partners_partner_type_id ON partners(partner_type_id);
CREATE INDEX IF NOT EXISTS ix_partners_rating ON partners(rating);
CREATE INDEX IF NOT EXISTS ix_sales_history_partner_id ON sales_history(partner_id);
CREATE INDEX IF NOT EXISTS ix_sales_history_product_id ON sales_history(product_id);
CREATE INDEX IF NOT EXISTS ix_sales_history_sale_date ON sales_history(sale_date);
