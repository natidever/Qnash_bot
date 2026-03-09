CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    image_url TEXT,
    group_size_required INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS group_deals (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'open' CHECK (status IN ('open','fulfilled','cancelled')),
    current_participants INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    fulfilled_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    discount_value NUMERIC(10,2) NOT NULL,
    discount_type TEXT CHECK (discount_type IN ('percent','fixed')),
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE NOT NULL,
    max_uses INTEGER DEFAULT 9999,
    used_count INTEGER DEFAULT 0,
    product_id INTEGER REFERENCES products(id),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT REFERENCES users(telegram_id),
    group_deal_id INTEGER REFERENCES group_deals(id),
    coupon_id INTEGER REFERENCES coupons(id),
    phone TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending','confirmed','cancelled','refunded')),
    total_amount NUMERIC(10,2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS coupon_usage_log (
    id SERIAL PRIMARY KEY,
    coupon_id INTEGER REFERENCES coupons(id),
    telegram_id BIGINT,
    used_at TIMESTAMP DEFAULT NOW()
);
