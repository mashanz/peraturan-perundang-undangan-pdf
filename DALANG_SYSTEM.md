# DALANG.IO SYSTEM CONFIGURATION

## Environments

**Staging:** `/home/dalang/staging/`
- `dalang-cli/` - CLI tool (Go)
- `test-api.dalang.io/` - Test API
- `test.dalang.io/` - Test frontend

**Production:** `/home/dalang/dev/`
- `api.dalang.io/` - Main API (Go)
- `dalang.io/` - Main frontend (SvelteKit + Bun)
- `bot.dalang.io/` - Telegram bot (Go)

## Services (SystemD)

**API Backend:** `dalang-api@8801-8808.service` (8 instances, ports 8801-8808)
- Binary: `/home/dalang/dev/api.dalang.io/dalang-api`
- Working Dir: `/home/dalang/dev/api.dalang.io`
- User: dalang

**Frontend:** `dalang-frontend@3001-3008.service` (8 instances, ports 3001-3008)
- Runtime: `/home/dalang/.bun/bin/bun ./build/index.js`
- Working Dir: `/home/dalang/dev/dalang.io`
- User: dalang

**Bot:** `dalang-bot.service`
- Binary: `/home/dalang/dev/bot.dalang.io/dalang-bot`
- User: dalang

**Test Services:**
- `dalang-test-api.service` - Test API
- `dalang-test-frontend.service` - Test frontend

## Infrastructure

**Incus Cluster:** `x99:` 
- Remote cluster for VPS containers
- API manages VPS via Incus API

**Database:** `/home/dalang/dev/api.dalang.io/data/dalang.db` (SQLite)
- Live files: `dalang.db`, `dalang.db-shm`, `dalang.db-wal`

**CLI Configuration:**
- API URL: `http://localhost:8801` (DALANG_API_URL)
- Auth: OAuth via https://dalang.io/auth/cli

## Business Model

- VPS hosting with custom configurations
- Container deployments (GitHub integration)
- Credit-based billing system (IDR)
- Affiliate/referral program
- Custom domains addon
- Monthly subscriptions