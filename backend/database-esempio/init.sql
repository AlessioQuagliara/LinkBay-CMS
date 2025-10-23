-- Tabella principale delle agenzie (tenant)
CREATE TABLE agency_tenant (
    agency_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    white_label_config JSONB,
    subscription_tier VARCHAR(50) DEFAULT 'pro',
    max_websites INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configurazione workspace per agenzia
CREATE TABLE workspace (
    workspace_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mappatura domini e sottodomini
CREATE TABLE domain_map (
    domain_map_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_name VARCHAR(255) UNIQUE NOT NULL,
    subdomain VARCHAR(100),
    domain_type VARCHAR(20) CHECK (domain_type IN ('custom', 'subdomain', 'alias')),
    status VARCHAR(20) CHECK (status IN ('active', 'pending', 'inactive')) DEFAULT 'pending',
    ssl_status VARCHAR(20) CHECK (ssl_status IN ('active', 'pending', 'error')) DEFAULT 'pending',
    ssl_certificate TEXT,
    ssl_private_key TEXT,
    agency_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    website_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configurazione generale dei website
CREATE TABLE website_config (
    website_config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_map_id UUID REFERENCES domain_map(domain_map_id),
    website_theme_id UUID,
    web_settings JSONB,
    status VARCHAR(20) CHECK (status IN ('suspended', 'active', 'maintenance')) DEFAULT 'active',
    theme_selected UUID,
    theme_market_id UUID,
    seo_settings JSONB,
    payment_gateways JSONB,
    shipping_config JSONB,
    tax_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Website effettivi
CREATE TABLE websites (
    website_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    workspace_id UUID NOT NULL REFERENCES workspace(workspace_id),
    website_config_id UUID NOT NULL REFERENCES website_config(website_config_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    currency VARCHAR(10) DEFAULT 'EUR',
    language VARCHAR(10) DEFAULT 'it',
    timezone VARCHAR(50) DEFAULT 'Europe/Rome',
    subscription_user_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Temi del marketplace
CREATE TABLE themes_market (
    market_theme_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    author VARCHAR(255),
    price DECIMAL(10,2) DEFAULT 0.00,
    category VARCHAR(100),
    preview_image_url TEXT,
    theme_files JSONB,
    style_config JSONB,
    supported_components JSONB,
    is_active BOOLEAN DEFAULT true,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relazione website-temi
CREATE TABLE website_themes (
    website_theme_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_config_id UUID NOT NULL REFERENCES website_config(website_config_id),
    theme_market_id UUID NOT NULL REFERENCES themes_market(market_theme_id),
    custom_css TEXT,
    custom_js TEXT,
    layout_overrides JSONB,
    is_active BOOLEAN DEFAULT true,
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configurazione tenant specifica
CREATE TABLE tenants_config (
    tenant_config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    name VARCHAR(255) NOT NULL,
    billing_info_id UUID,
    custom_domain_allowed BOOLEAN DEFAULT false,
    max_products INTEGER DEFAULT 1000,
    max_users INTEGER DEFAULT 10,
    features_allowed JSONB,
    api_rate_limit INTEGER DEFAULT 1000,
    storage_limit_mb INTEGER DEFAULT 1024,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Informazioni di billing
CREATE TABLE billing_info (
    billing_info_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    vat_number VARCHAR(50),
    fiscal_code VARCHAR(50),
    address_line_1 VARCHAR(255),
    address_line_2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Italy',
    province VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sottoscrizioni utente (per website specifici)
CREATE TABLE subscription_user (
    subscription_user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    subscription_id UUID NOT NULL,
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly', 'daily')) DEFAULT 'monthly',
    status VARCHAR(20) CHECK (status IN ('active', 'suspended', 'cancelled', 'trial')) DEFAULT 'active',
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'EUR',
    stripe_subscription_id VARCHAR(255),
    paypal_subscription_id VARCHAR(255),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    trial_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Piano sottoscrizioni disponibili
CREATE TABLE subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly', 'daily')) DEFAULT 'monthly',
    currency VARCHAR(10) DEFAULT 'EUR',
    features JSONB NOT NULL,
    max_websites INTEGER DEFAULT 1,
    max_products INTEGER DEFAULT 100,
    max_users INTEGER DEFAULT 3,
    support_level VARCHAR(50) DEFAULT 'basic',
    is_active BOOLEAN DEFAULT true,
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Utenti dei tenant (clienti finali delle agenzie)
CREATE TABLE users_tenant (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) CHECK (role IN ('owner', 'admin', 'editor', 'viewer', 'customer')) DEFAULT 'owner',
    permissions JSONB,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    timezone VARCHAR(50) DEFAULT 'Europe/Rome',
    language VARCHAR(10) DEFAULT 'it',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Manager delle agenzie (dipendenti/team)
CREATE TABLE user_manager (
    user_manager_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    user_id UUID NOT NULL REFERENCES users_tenant(user_id),
    role VARCHAR(50) CHECK (role IN ('super_admin', 'agency_admin', 'agency_editor', 'support_agent')) DEFAULT 'agency_editor',
    permissions JSONB,
    assigned_websites JSONB, -- Array di website_id gestiti
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configurazione SEO
CREATE TABLE seo (
    seo_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    page_slug VARCHAR(255),
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT,
    canonical_url VARCHAR(255),
    og_image VARCHAR(255),
    og_title VARCHAR(255),
    og_description TEXT,
    twitter_card VARCHAR(50),
    structured_data JSONB,
    robots_txt TEXT,
    sitemap_priority DECIMAL(3,2) DEFAULT 0.5,
    is_noindex BOOLEAN DEFAULT false,
    is_nofollow BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pagine dei website
CREATE TABLE pages (
    page_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    slug VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_html TEXT,
    content_css TEXT,
    content_js TEXT,
    page_type VARCHAR(50) CHECK (page_type IN ('home', 'product', 'category', 'custom', 'blog', 'contact', 'about')) DEFAULT 'custom',
    navigation_id UUID,
    footer_id UUID,
    language VARCHAR(10) DEFAULT 'it',
    is_published BOOLEAN DEFAULT false,
    published_at TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    parent_page_id UUID REFERENCES pages(page_id),
    template_used VARCHAR(100),
    seo_settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Informazioni agenzia
CREATE TABLE agency_info (
    agency_info_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_tenant_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    legal_name VARCHAR(255) NOT NULL,
    trading_name VARCHAR(255),
    description TEXT,
    website_url VARCHAR(255),
    logo_url VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    founded_year INTEGER,
    tax_id VARCHAR(100),
    agency_address_id UUID,
    agency_billing_id UUID,
    support_email VARCHAR(255),
    support_phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indirizzi agenzia
CREATE TABLE agency_address (
    agency_address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'Italy',
    address_type VARCHAR(50) CHECK (address_type IN ('legal', 'operational', 'billing')) DEFAULT 'legal',
    is_primary BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Billing agenzia
CREATE TABLE agency_billing (
    agency_billing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agency_tenant(agency_id),
    payment_method VARCHAR(50) CHECK (payment_method IN ('credit_card', 'bank_transfer', 'paypal', 'stripe')) DEFAULT 'credit_card',
    agency_subscription_id UUID NOT NULL,
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly', 'daily')) DEFAULT 'monthly',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    next_billing_date TIMESTAMP,
    stripe_customer_id VARCHAR(255),
    paypal_billing_agreement_id VARCHAR(255),
    invoice_prefix VARCHAR(50) DEFAULT 'AGENCY',
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sottoscrizioni agenzia
CREATE TABLE agency_subscription (
    agency_subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    billing_cycle VARCHAR(20) CHECK (billing_cycle IN ('monthly', 'yearly', 'daily')) DEFAULT 'monthly',
    status VARCHAR(20) CHECK (status IN ('active', 'suspended', 'cancelled')) DEFAULT 'active',
    features JSONB NOT NULL,
    max_websites INTEGER NOT NULL,
    max_storage_gb INTEGER DEFAULT 10,
    max_bandwidth_gb INTEGER DEFAULT 100,
    support_level VARCHAR(50) DEFAULT 'standard',
    white_label_allowed BOOLEAN DEFAULT false,
    custom_domain_allowed BOOLEAN DEFAULT false,
    api_access_allowed BOOLEAN DEFAULT false,
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Navigazione
CREATE TABLE navigation (
    navigation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('header', 'footer', 'sidebar', 'mobile')) DEFAULT 'header',
    menu_items JSONB NOT NULL,
    position VARCHAR(50) DEFAULT 'top',
    is_active BOOLEAN DEFAULT true,
    breakpoint VARCHAR(50) DEFAULT 'all',
    content_css TEXT,
    content_js TEXT,
    content_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Footer
CREATE TABLE footing (
    footing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('info', 'utility', 'contact', 'compliance', 'social')) DEFAULT 'info',
    content JSONB NOT NULL,
    position INTEGER DEFAULT 0,
    columns INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    content_css TEXT,
    content_js TEXT,
    content_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per le transazioni e commissioni (Stripe Connect)
CREATE TABLE marketplace_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    stripe_charge_id VARCHAR(255),
    stripe_transfer_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'EUR',
    application_fee_amount DECIMAL(10,2),
    agency_commission_rate DECIMAL(5,2) DEFAULT 0.20,
    platform_commission_rate DECIMAL(5,2) DEFAULT 0.05,
    status VARCHAR(50) CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    connected_account_id VARCHAR(255), -- Stripe Connect account ID
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plugin marketplace
CREATE TABLE plugins_market (
    plugin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    author VARCHAR(255),
    price DECIMAL(10,2) DEFAULT 0.00,
    category VARCHAR(100),
    plugin_type VARCHAR(50) CHECK (plugin_type IN ('payment', 'shipping', 'analytics', 'marketing', 'utility')),
    compatibility JSONB,
    download_url TEXT,
    is_active BOOLEAN DEFAULT true,
    download_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plugin installati
CREATE TABLE website_plugins (
    installation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID NOT NULL REFERENCES websites(website_id),
    plugin_id UUID NOT NULL REFERENCES plugins_market(plugin_id),
    version VARCHAR(20) NOT NULL,
    config JSONB,
    is_active BOOLEAN DEFAULT true,
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log per sicurezza
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID REFERENCES agency_tenant(agency_id),
    website_id UUID REFERENCES websites(website_id),
    user_id UUID REFERENCES users_tenant(user_id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indici per performance
CREATE INDEX idx_agency_tenant_workspace ON agency_tenant(workspace_id);
CREATE INDEX idx_websites_tenant ON websites(tenant_id);
CREATE INDEX idx_websites_workspace ON websites(workspace_id);
CREATE INDEX idx_domain_map_agency ON domain_map(agency_id);
CREATE INDEX idx_users_tenant_website ON users_tenant(website_id);
CREATE INDEX idx_pages_website ON pages(website_id);
CREATE INDEX idx_subscription_user_website ON subscription_user(website_id);
CREATE INDEX idx_audit_logs_agency ON audit_logs(agency_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_marketplace_transactions_website ON marketplace_transactions(website_id);