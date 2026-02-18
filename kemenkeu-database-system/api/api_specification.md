# KEMENKEU Regulation Database API Specification
## RESTful and GraphQL API for Ministry of Finance Regulations

### Version: 2.0
### Base URL: `https://api.kemenkeu.go.id/regulations/v2`

## Overview

The KEMENKEU Regulation Database API provides comprehensive access to Indonesian Ministry of Finance regulations, metadata, and analytics. Designed for government systems integration, public transparency, and developer ecosystem support.

### Key Features
- **Multi-format Access**: RESTful JSON, GraphQL, and XML endpoints
- **Advanced Search**: Semantic search with AI-powered relevance
- **Real-time Updates**: WebSocket subscriptions for live updates
- **Public Transparency**: Open access to public regulations
- **Rate Limiting**: Tiered access based on user type and API key
- **Multi-language**: Indonesian and English content support

## Authentication

### API Key Types
- **Public Access**: No authentication required for public regulations
- **Government**: Enhanced access with department-level authentication
- **Developer**: Registered developer access with usage analytics
- **Internal**: Full system access for ministry applications

```http
Authorization: Bearer <api_key>
X-API-Client: <client_identifier>
```

## Core Endpoints

### 1. Regulations

#### GET /regulations
List and search regulations with advanced filtering

```http
GET /regulations?page=1&limit=20&status=active&policy_area=TAX&theme=TRANSPARENCY
```

**Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (max: 100, default: 20)
- `status` (string): active, superseded, revoked, draft
- `regulation_type` (string): PMK, SE, PER, KMK, etc.
- `policy_area` (string): Policy area code
- `theme` (string): Theme code
- `directorate` (string): Issuing directorate
- `date_from` (date): Issue date range start
- `date_to` (date): Issue date range end
- `language` (string): id, en, both
- `search` (string): Full-text search query
- `sort` (string): issue_date, title, popularity, relevance

**Response:**
```json
{
  "data": [
    {
      "id": 12345,
      "regulation_number": "PMK-123/PMK.03/2024",
      "title": "Peraturan Menteri Keuangan tentang Pajak Penghasilan",
      "title_en": "Minister of Finance Regulation on Income Tax",
      "regulation_type": "PMK",
      "issuing_directorate": "Direktorat Jenderal Pajak",
      "issue_date": "2024-01-15",
      "effective_date": "2024-02-01",
      "status": "active",
      "language": "id",
      "complexity_score": 7.5,
      "conversion_quality_score": 9.2,
      "url": "/regulations/12345",
      "pdf_url": "https://files.kemenkeu.go.id/regulations/PMK-123-PMK.03-2024.pdf",
      "policy_areas": [
        {
          "code": "TAX_INCOME",
          "name": "Pajak Penghasilan",
          "name_en": "Income Tax",
          "is_primary": true
        }
      ],
      "themes": [
        {
          "code": "TRANSPARENCY",
          "name": "Transparansi",
          "relevance_score": 0.85
        }
      ],
      "tags": [
        "corporate_tax",
        "individual_tax",
        "withholding_tax"
      ]
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_pages": 232,
    "total_items": 4631,
    "has_next": true,
    "has_previous": false
  },
  "filters_applied": {
    "status": "active",
    "policy_area": "TAX"
  },
  "search_metadata": {
    "query_time_ms": 45,
    "total_found": 1247,
    "semantic_search_used": true
  }
}
```

#### GET /regulations/{id}
Get detailed regulation information

```http
GET /regulations/12345?include=content,relationships,analytics
```

**Parameters:**
- `include` (string): content, relationships, analytics, versions
- `language` (string): Preferred language for content

**Response:**
```json
{
  "data": {
    "id": 12345,
    "regulation_number": "PMK-123/PMK.03/2024",
    "title": "Peraturan Menteri Keuangan tentang Pajak Penghasilan",
    "regulation_type": "PMK",
    "issuing_directorate": "Direktorat Jenderal Pajak",
    "issue_date": "2024-01-15",
    "effective_date": "2024-02-01",
    "status": "active",
    "page_count": 45,
    "article_count": 28,
    "complexity_score": 7.5,
    "readability_score": 6.8,
    "international_alignment": {
      "oecd_compliant": true,
      "standards": ["BEPS", "AEOI"]
    },
    "content": [
      {
        "id": 1001,
        "content_type": "chapter",
        "sequence_number": 1,
        "title": "KETENTUAN UMUM",
        "title_en": "GENERAL PROVISIONS",
        "content": "Dalam Peraturan Menteri ini yang dimaksud dengan...",
        "content_en": "In this Ministerial Regulation, what is meant by...",
        "word_count": 245,
        "has_tables": false,
        "has_formulas": true
      }
    ],
    "relationships": [
      {
        "type": "amends",
        "target_regulation": {
          "id": 11234,
          "regulation_number": "PMK-098/PMK.03/2023",
          "title": "Peraturan sebelumnya tentang Pajak Penghasilan"
        },
        "description": "Mengubah ketentuan tarif pajak penghasilan"
      }
    ],
    "analytics": {
      "total_views": 15420,
      "views_last_30_days": 1247,
      "popularity_rank": 15,
      "avg_time_spent": "00:08:32",
      "download_count": 3421
    },
    "metadata": {
      "created_at": "2024-01-20T10:30:00Z",
      "updated_at": "2024-01-25T14:15:00Z",
      "last_reviewed": "2024-01-25T14:15:00Z",
      "version": 2
    }
  }
}
```

### 2. Search

#### POST /search
Advanced semantic search with AI-powered relevance

```http
POST /search
Content-Type: application/json

{
  "query": "pajak penghasilan perusahaan multinasional",
  "search_type": "semantic",
  "filters": {
    "policy_areas": ["TAX_INCOME"],
    "themes": ["INTERNATIONAL"],
    "date_range": {
      "from": "2020-01-01",
      "to": "2024-12-31"
    },
    "complexity_range": {
      "min": 5.0,
      "max": 10.0
    }
  },
  "language": "id",
  "include_suggestions": true,
  "max_results": 50
}
```

**Response:**
```json
{
  "data": {
    "results": [
      {
        "regulation": {
          "id": 12345,
          "regulation_number": "PMK-123/PMK.03/2024",
          "title": "Peraturan tentang Pajak Penghasilan Perusahaan Multinasional",
          "relevance_score": 0.95,
          "matched_terms": ["pajak penghasilan", "perusahaan multinasional"],
          "highlight": "...mengenai <mark>pajak penghasilan</mark> bagi <mark>perusahaan multinasional</mark>..."
        }
      }
    ],
    "total_results": 127,
    "search_time_ms": 85,
    "suggestions": [
      "transfer pricing",
      "base erosion and profit shifting",
      "thin capitalization"
    ],
    "related_searches": [
      "pajak penghasilan badan",
      "perusahaan asing di indonesia",
      "perjanjian penghindaran pajak berganda"
    ]
  },
  "metadata": {
    "query_processed": "pajak penghasilan perusahaan multinasional",
    "search_type": "semantic",
    "ai_enhancement_used": true,
    "filters_applied": 3
  }
}
```

### 3. Metadata and Classifications

#### GET /policy-areas
Get policy area taxonomy

```http
GET /policy-areas?include_hierarchy=true&language=both
```

#### GET /themes
Get thematic classifications

#### GET /tags
Get available tags with usage statistics

### 4. Analytics

#### GET /analytics/popular
Get trending and popular regulations

```http
GET /analytics/popular?period=last_30_days&category=all&limit=10
```

#### GET /analytics/usage/{regulation_id}
Get usage statistics for specific regulation

### 5. Export and Bulk Access

#### GET /export
Export regulations in various formats

```http
GET /export?format=json&filter=policy_area:TAX&include=metadata,content
```

**Supported Formats:**
- JSON
- XML
- CSV (metadata only)
- Excel (metadata only)
- ZIP (bulk download)

## GraphQL Endpoint

### URL: `/graphql`

**Example Query:**
```graphql
query GetRegulation($id: ID!, $includeContent: Boolean = false) {
  regulation(id: $id) {
    id
    regulationNumber
    title
    titleEn
    regulationType
    issuingDirectorate
    issueDate
    effectiveDate
    status
    complexityScore
    policyAreas {
      code
      name
      nameEn
      isPrimary
    }
    themes {
      code
      name
      relevanceScore
    }
    content @include(if: $includeContent) {
      id
      contentType
      title
      content
      wordCount
    }
    relationships {
      type
      targetRegulation {
        id
        regulationNumber
        title
      }
    }
    analytics {
      totalViews
      viewsLast30Days
      popularityRank
    }
  }
}
```

## WebSocket Subscriptions

### URL: `wss://api.kemenkeu.go.id/regulations/ws`

**Subscribe to regulation updates:**
```javascript
{
  "action": "subscribe",
  "channel": "regulation_updates",
  "filters": {
    "policy_areas": ["TAX"],
    "status": ["active"]
  }
}
```

## Rate Limiting

### Limits by User Type
- **Public**: 1000 requests/hour
- **Developer**: 10,000 requests/hour  
- **Government**: 50,000 requests/hour
- **Internal**: Unlimited

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "REGULATION_NOT_FOUND",
    "message": "Regulation with ID 99999 was not found",
    "details": {
      "searched_id": 99999,
      "suggestions": [12345, 12346]
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-20T10:30:00Z"
  }
}
```

### Error Codes
- `REGULATION_NOT_FOUND`: Regulation doesn't exist
- `INVALID_PARAMETERS`: Request parameters are invalid
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `UNAUTHORIZED`: Invalid or missing API key
- `INTERNAL_ERROR`: Server error
- `MAINTENANCE_MODE`: System under maintenance

## Data Quality and Versioning

### Content Quality Indicators
```json
{
  "quality_indicators": {
    "conversion_quality_score": 9.2,
    "metadata_completeness": 0.95,
    "last_quality_check": "2024-01-25T14:15:00Z",
    "known_issues": []
  }
}
```

### API Versioning
- Current Version: v2
- Supported Versions: v1, v2
- Deprecation Policy: 12 months notice
- Version Header: `Accept: application/vnd.kemenkeu.v2+json`

## SDK and Integration

### Available SDKs
- **JavaScript/Node.js**: `npm install kemenkeu-regulations-api`
- **Python**: `pip install kemenkeu-regulations`
- **Java**: Maven/Gradle dependency
- **PHP**: Composer package
- **Go**: Go module

### Integration Examples
```javascript
// Node.js
const KemenkeuAPI = require('kemenkeu-regulations-api');
const client = new KemenkeuAPI({ apiKey: 'your-api-key' });

const regulations = await client.regulations.search({
  query: 'pajak penghasilan',
  policyArea: 'TAX',
  limit: 10
});
```

## Monitoring and Support

### API Health Check
- **Endpoint**: `/health`
- **Response**: System status and performance metrics

### Documentation and Support
- **Interactive Docs**: `/docs` (Swagger UI)
- **Developer Portal**: `https://developer.kemenkeu.go.id`
- **Support Email**: `api-support@kemenkeu.go.id`
- **Status Page**: `https://status.api.kemenkeu.go.id`