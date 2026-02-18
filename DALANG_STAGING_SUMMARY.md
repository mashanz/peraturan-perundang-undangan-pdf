# DALANG.IO STAGING ENVIRONMENT SUMMARY

## Overview
Staging environment at `/home/dalang/staging/` contains development versions of the Dalang.io PaaS platform, featuring a comprehensive CLI tool and test environments for both API and frontend.

## Key Projects

### 1. Dalang CLI (`dalang-cli/`)
**Language:** Go  
**Purpose:** Command-line interface for managing Dalang.io cloud services

**Core Features:**
- **Authentication:** OAuth login via device code flow
- **Service Management:** List, create, info for VPS/containers/apps
- **VM Operations:** Shell access, exec commands, console, start/stop/delete
- **Credit Management:** Balance check, transaction history, top-up
- **Domain Management:** Custom domain addon, DNS verification
- **Pricing:** VPS pricing calculator
- **Terminal Integration:** WebSocket-based shell/console with persistent sessions

**Architecture:**
- API client with Cloudflare DNS resolver (1.1.1.1)
- JWT token authentication via file-based credentials
- Config system supporting environment variables and config files
- Rich CLI with colored output, progress bars, JSON mode
- Cross-platform build targets (Linux, macOS, Windows, Android)

### 2. Test API (`test-api.dalang.io/`)
**Language:** Go 1.24  
**Purpose:** Backend REST API for staging/testing

**Key Features:**
- SQLite database with WAL mode and custom migrations
- Incus container management via Unix socket
- Google/GitHub OAuth2 + JWT authentication
- Xendit payment integration with webhooks
- Cloudflare SaaS SSL integration
- Pingora proxy route management
- Swagger API documentation
- Admin panel capabilities

**Architecture:**
- Main entry point with comprehensive route definitions
- Modular handlers (~45 files): admin, VPS, billing, webhooks, users
- Middleware for CORS and JWT authentication
- Database migration system with up/down scripts
- Container operations through Incus client

### 3. Test Frontend (`test.dalang.io/`)
**Language:** SvelteKit 2.10 + Svelte 5, Bun runtime  
**Purpose:** Web interface for staging/testing

**Key Features:**
- File-based routing with i18n support (en, zh, id)
- OAuth login flows (Google/GitHub)
- Protected dashboard for service management
- Xendit checkout integration
- Admin panel (`/su/` routes)
- Terminal interface with xterm.js
- TailwindCSS + DaisyUI styling

**Architecture:**
- Server-side auth middleware with JWT validation
- Centralized API client for backend communication
- Component-based architecture with reusable Svelte components
- Internationalization system with translation files
- Production deployment via git tags + cron

## Security Issues Status

### ✅ **Fixed (1/5):**
- **Frontend Secret Exposure:** VITE_XENDIT_SECRET_KEY → XENDIT_SECRET_KEY (no longer bundled in client-side JS)

### ⚠️ **Partially Fixed (1/5):**  
- **Secret Management:** `.env` properly gitignored, but APP_API_KEY still placeholder value `SUPER_SECRET_API_KEY_123`

### ❌ **Not Fixed (3/5):**
1. **Data Encryption:** VPS passwords/SSH keys still plaintext (TODO comments in models/models.go)
2. **Webhook Security:** Timestamp validation logs warning but doesn't reject stale requests
3. **XSS Prevention:** Admin email preview still uses `{@html body}` without DOMPurify sanitization

### Security Score: **2/5 fixes implemented**

## Technology Stack

**Backend:**
- Database: SQLite with WAL mode
- Container Platform: Incus (Unix socket communication)
- Payment Gateway: Xendit with webhook integration
- Proxy: Pingora load balancer
- Auth: Google/GitHub OAuth2 + JWT

**Frontend:**
- Runtime: Bun with SvelteAdapter
- Styling: TailwindCSS + DaisyUI (brand: #facc15)
- Terminal: xterm.js for browser-based VPS access
- Docs: mdsvex for markdown pages

**CLI:**
- Language: Go with Cobra-like command structure
- API Communication: HTTP client with custom DNS resolver
- Terminal: WebSocket-based persistent sessions
- Auth: Device code OAuth flow

## Development Workflow

**Build Commands:**
- CLI: `go build -o dalang` in `dalang-cli/`
- API: `go run main.go` (dev) or `go build -o dalang-api`
- Frontend: `bun run dev` (development) or `bun run build` (production)

**Deployment:**
- Staging services run via systemd
- Production uses git tag-based auto-deployment
- 8 replicas each for API (ports 8801-8808) and frontend (ports 3001-3008)

## Current Status
- Test environments functional with systemd services
- CLI tool feature-complete and production-ready
- Critical security vulnerabilities documented and planned for fixing
- Architecture supports scale-out deployment model
- Full OAuth integration and payment processing pipeline

## Next Steps
- Address 4 critical security vulnerabilities
- Complete migration of staging features to production
- Implement additional CLI features for container management
- Scale testing of load-balanced deployment architecture