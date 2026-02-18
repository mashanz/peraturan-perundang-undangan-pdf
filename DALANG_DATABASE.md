# DALANG.IO DATABASE SCHEMA

**Location:** `/home/dalang/dev/api.dalang.io/data/dalang.db` (SQLite)

## Core Tables

### users
User accounts and authentication
```sql
id TEXT PRIMARY KEY,              -- UUID from Google or generated  
email TEXT UNIQUE NOT NULL,
email_verified INTEGER DEFAULT 0, -- 0=false, 1=true
google_id TEXT UNIQUE,            -- Google OAuth sub claim
display_name TEXT,
avatar_url TEXT,
role TEXT DEFAULT 'user',         -- 'user', 'admin', 'support'
is_active INTEGER DEFAULT 1,      -- 0=false, 1=true
last_sign_in_at TEXT,            -- ISO 8601 timestamp
created_at TEXT,
updated_at TEXT,
last_login_ip TEXT,
last_login_location TEXT,
login_count INTEGER DEFAULT 0,
github_id TEXT
```

### service_vps
VPS service instances
```sql
id TEXT PRIMARY KEY,              -- UUID
user_id TEXT NOT NULL,
name TEXT,
vcpu INTEGER CHECK(vcpu > 0),
ram INTEGER CHECK(ram > 0),       -- In MB
storage INTEGER CHECK(storage > 0), -- In GB
storage_type TEXT,                -- 'HDD', 'SSD', 'NVME'
status TEXT DEFAULT 'UNAVAILABLE', -- 'RUNNING', 'STOPPED', 'CREATING', 'UNAVAILABLE'
created_at TEXT,
updated_at TEXT,
expired_at TEXT,                  -- ISO 8601 timestamp
price REAL CHECK(price >= 0),     -- Monthly subscription price
bandwidth INTEGER DEFAULT 20,
custom_domain_enabled INTEGER DEFAULT 0,
custom_domain_price REAL DEFAULT 10000,
display_name TEXT,
node TEXT,
shell INTEGER DEFAULT 0,
ping INTEGER DEFAULT 0,
curl INTEGER DEFAULT 0
```

### credit_transactions
Credit/billing transactions (FIFO system)
```sql
id INTEGER PRIMARY KEY,
user_id TEXT NOT NULL,
type TEXT NOT NULL,               -- 'topup', 'spend', 'commission', 'refund', 'expired'
amount INTEGER NOT NULL,          -- positive for credit, negative for debit
remaining_amount INTEGER DEFAULT 0, -- for topup: tracks unspent portion for FIFO
balance_after INTEGER NOT NULL,
description TEXT,
reference_id TEXT,                -- external_id for topup, bill external_id for spend
reference_type TEXT,              -- 'xendit_invoice', 'bill', 'commission', etc.
expires_at DATETIME,              -- 12 months after topup for topup type
created_at DATETIME
```

### bill_records
Invoice/billing records
```sql
id INTEGER PRIMARY KEY,
user_id TEXT NOT NULL,
external_id TEXT,                 -- Xendit external ID
description TEXT,
invoice_xendit_id TEXT,
url_invoice TEXT,
price INTEGER NOT NULL,           -- In smallest currency unit (rupiah)
status TEXT DEFAULT 'pending',    -- 'pending', 'paid', 'failed', 'expired', 'cancelled'
paid_at TEXT,
created_at TEXT,
updated_at TEXT,
expired_url_at TEXT,
metadata TEXT,
vps_id TEXT,
container_id TEXT,
deployment_id TEXT,
payment_method TEXT DEFAULT 'xendit',
dedicated_id TEXT,
receipt_token TEXT
```

### products
Service product catalog
```sql
id TEXT PRIMARY KEY,
name TEXT NOT NULL,
category TEXT NOT NULL,
price INTEGER NOT NULL,
vcpu INTEGER,
ram INTEGER,
storage INTEGER,
storage_type TEXT,
description TEXT,
created_at TEXT,
updated_at TEXT
```

### github_deployments
GitHub integration for container deployments
```sql
id TEXT PRIMARY KEY,
user_id TEXT NOT NULL,
container_id TEXT,
repo_owner TEXT NOT NULL,
repo_name TEXT NOT NULL,
repo_full_name TEXT NOT NULL,     -- owner/repo
branch TEXT DEFAULT 'main',
dockerfile_path TEXT DEFAULT 'Dockerfile',
port INTEGER NOT NULL,            -- exposed port for the app
subdomain TEXT,                   -- e.g., myapp-abc123.svc.dalang.io
webhook_secret TEXT,              -- for verifying GitHub webhooks
webhook_id INTEGER,               -- GitHub webhook ID for cleanup
auto_deploy INTEGER DEFAULT 1,    -- auto rebuild on push
status TEXT DEFAULT 'pending',    -- 'pending', 'building', 'running', 'failed', 'stopped'
last_build_at TEXT,
last_commit_sha TEXT,
created_at TEXT,
updated_at TEXT,
cpu_limit TEXT DEFAULT '1',
memory_limit TEXT DEFAULT '128MiB',
storage_limit TEXT DEFAULT '2GiB',
env_vars TEXT DEFAULT '{}',
container_ip TEXT,
display_name TEXT,
expired_at TEXT,
price REAL DEFAULT 25000,
custom_domain_enabled INTEGER DEFAULT 0
```

## Support Tables

- `service_container` - Container service instances
- `service_vps_domains` - Custom domain mappings
- `service_vps_snapshots` - VPS backup snapshots  
- `vps_usage` - Resource usage tracking
- `cluster_cache` - Cached cluster resource data
- `cli_auth_codes` - CLI authentication codes
- `oauth_states` - OAuth state tracking
- `tickets` - Customer support tickets
- `referrals` / `referral_codes` - Referral program
- `affiliate_commissions` - Affiliate earnings
- `personal_info` - Additional user data
- `user_wallet` - User credit balances
- `vps_cpu_tracking` - CPU usage monitoring

## All Tables List

```
affiliate_commissions, bill_records, cli_auth_codes, cluster_cache, 
credit_transactions, customer_service, deployment_domains, github_deployments,
github_tokens, oauth_states, personal_info, products, products_baremetal_service,
products_custom_server_distributor, referral_codes, referrals, revenue_stats,
schema_migrations, service_container, service_container_detail, service_dedicated,
service_vps, service_vps_detail, service_vps_domains, service_vps_snapshots,
services_records, tickets, user_active_services, user_logins, user_wallet,
users, vps_cpu_tracking, vps_usage, vps_with_users, wa_to_discord
```