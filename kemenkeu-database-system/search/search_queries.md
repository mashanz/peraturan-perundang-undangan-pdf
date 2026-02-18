# KEMENKEU Regulation Search Queries
## Advanced Search Patterns and Semantic Search Implementation

### Overview
Comprehensive search query patterns for the KEMENKEU regulation database using Elasticsearch with AI-powered semantic search capabilities. Supports multi-language queries, complex filtering, and relevance optimization.

## Basic Search Patterns

### 1. Simple Text Search
```json
{
  "query": {
    "multi_match": {
      "query": "pajak penghasilan",
      "fields": [
        "title^3",
        "title_en^2.5",
        "content.title^2",
        "content.content^1",
        "content.content_en^1"
      ],
      "type": "best_fields",
      "fuzziness": "AUTO",
      "operator": "or",
      "minimum_should_match": "75%"
    }
  },
  "highlight": {
    "fields": {
      "title": {},
      "title_en": {},
      "content.content": {
        "fragment_size": 150,
        "number_of_fragments": 3
      }
    },
    "pre_tags": ["<mark>"],
    "post_tags": ["</mark>"]
  }
}
```

### 2. Regulation Number Search
```json
{
  "query": {
    "bool": {
      "should": [
        {
          "term": {
            "regulation_number.raw": {
              "value": "PMK-123/PMK.03/2024",
              "boost": 10.0
            }
          }
        },
        {
          "wildcard": {
            "regulation_number.raw": {
              "value": "*PMK-123*",
              "boost": 5.0
            }
          }
        },
        {
          "match": {
            "regulation_number": {
              "query": "PMK 123 2024",
              "boost": 3.0
            }
          }
        }
      ]
    }
  }
}
```

## Advanced Filter Queries

### 3. Multi-Criteria Filtering
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "transfer pricing",
            "fields": ["title^3", "content.content^1"]
          }
        }
      ],
      "filter": [
        {
          "term": {
            "status": "active"
          }
        },
        {
          "terms": {
            "regulation_type": ["PMK", "SE"]
          }
        },
        {
          "range": {
            "issue_date": {
              "gte": "2020-01-01",
              "lte": "2024-12-31"
            }
          }
        },
        {
          "nested": {
            "path": "policy_areas",
            "query": {
              "bool": {
                "must": [
                  {
                    "term": {
                      "policy_areas.code": "TAX_INCOME"
                    }
                  },
                  {
                    "term": {
                      "policy_areas.is_primary": true
                    }
                  }
                ]
              }
            }
          }
        },
        {
          "range": {
            "complexity_score": {
              "gte": 5.0,
              "lte": 8.0
            }
          }
        }
      ]
    }
  },
  "sort": [
    {
      "_score": {
        "order": "desc"
      }
    },
    {
      "issue_date": {
        "order": "desc"
      }
    }
  ]
}
```

### 4. Theme-Based Search
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "digitalisasi"
          }
        }
      ],
      "should": [
        {
          "nested": {
            "path": "themes",
            "query": {
              "bool": {
                "must": [
                  {
                    "term": {
                      "themes.code": "DIGITALIZATION"
                    }
                  }
                ]
              }
            },
            "score_mode": "max",
            "boost": 2.0
          }
        }
      ]
    }
  }
}
```

## Semantic Search Queries

### 5. Vector Similarity Search
```json
{
  "query": {
    "script_score": {
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "status": "active"
              }
            },
            {
              "exists": {
                "field": "embedding_vector"
              }
            }
          ]
        }
      },
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
        "params": {
          "query_vector": [0.123, 0.456, 0.789]
        }
      },
      "min_score": 1.2
    }
  },
  "size": 20
}
```

### 6. Hybrid Search (Text + Vector)
```json
{
  "query": {
    "bool": {
      "should": [
        {
          "multi_match": {
            "query": "pajak digital ekonomi",
            "fields": ["title^3", "content.content^1"],
            "boost": 1.0
          }
        },
        {
          "script_score": {
            "query": {
              "exists": {
                "field": "embedding_vector"
              }
            },
            "script": {
              "source": "(cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0) * 0.5",
              "params": {
                "query_vector": [0.123, 0.456, 0.789]
              }
            }
          }
        }
      ],
      "filter": [
        {
          "term": {
            "status": "active"
          }
        }
      ]
    }
  }
}
```

## Aggregation Queries

### 7. Faceted Search with Aggregations
```json
{
  "query": {
    "match": {
      "title": "pajak"
    }
  },
  "aggs": {
    "regulation_types": {
      "terms": {
        "field": "regulation_type",
        "size": 10,
        "order": {
          "_count": "desc"
        }
      }
    },
    "policy_areas": {
      "nested": {
        "path": "policy_areas"
      },
      "aggs": {
        "policy_area_codes": {
          "terms": {
            "field": "policy_areas.code",
            "size": 20
          },
          "aggs": {
            "policy_area_names": {
              "terms": {
                "field": "policy_areas.name.raw"
              }
            }
          }
        }
      }
    },
    "themes": {
      "nested": {
        "path": "themes"
      },
      "aggs": {
        "theme_codes": {
          "terms": {
            "field": "themes.code",
            "size": 15
          }
        }
      }
    },
    "issue_date_range": {
      "date_histogram": {
        "field": "issue_date",
        "calendar_interval": "year",
        "format": "yyyy",
        "min_doc_count": 1
      }
    },
    "complexity_distribution": {
      "histogram": {
        "field": "complexity_score",
        "interval": 1,
        "min_doc_count": 1
      }
    },
    "issuing_directorates": {
      "terms": {
        "field": "issuing_directorate.raw",
        "size": 10,
        "order": {
          "_count": "desc"
        }
      }
    }
  },
  "size": 0
}
```

### 8. Analytics Aggregations
```json
{
  "query": {
    "match_all": {}
  },
  "aggs": {
    "popular_regulations": {
      "terms": {
        "field": "id",
        "size": 10,
        "order": {
          "avg_views": "desc"
        }
      },
      "aggs": {
        "avg_views": {
          "avg": {
            "field": "analytics.views_last_30_days"
          }
        },
        "regulation_info": {
          "top_hits": {
            "_source": ["title", "regulation_number", "analytics"],
            "size": 1
          }
        }
      }
    },
    "trending_themes": {
      "nested": {
        "path": "themes"
      },
      "aggs": {
        "theme_popularity": {
          "terms": {
            "field": "themes.code",
            "size": 10
          },
          "aggs": {
            "reverse_nested_to_regulation": {
              "reverse_nested": {},
              "aggs": {
                "avg_popularity": {
                  "avg": {
                    "field": "analytics.trending_score"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## Suggestion and Autocomplete

### 9. Auto-completion Query
```json
{
  "suggest": {
    "regulation_suggest": {
      "prefix": "pajak peng",
      "completion": {
        "field": "suggest",
        "size": 10,
        "contexts": {
          "regulation_type": ["PMK", "SE"],
          "policy_area": ["TAX"]
        }
      }
    }
  },
  "_source": false
}
```

### 10. Smart Suggestions with Context
```json
{
  "suggest": {
    "title_suggestions": {
      "text": "pajak penghasilan",
      "term": {
        "field": "title",
        "size": 5,
        "sort": "frequency",
        "suggest_mode": "popular"
      }
    },
    "phrase_suggestions": {
      "text": "pajak penghasilan perusahaan",
      "phrase": {
        "field": "title",
        "size": 3,
        "gram_size": 3,
        "direct_generator": [
          {
            "field": "title",
            "suggest_mode": "always",
            "min_word_length": 3
          }
        ],
        "highlight": {
          "pre_tag": "<em>",
          "post_tag": "</em>"
        }
      }
    }
  }
}
```

## Complex Relationship Queries

### 11. Find Related Regulations
```json
{
  "query": {
    "bool": {
      "should": [
        {
          "nested": {
            "path": "relationships",
            "query": {
              "bool": {
                "must": [
                  {
                    "term": {
                      "relationships.target_regulation_id": 12345
                    }
                  },
                  {
                    "terms": {
                      "relationships.type": ["amends", "supersedes", "relates_to"]
                    }
                  }
                ]
              }
            },
            "score_mode": "max"
          }
        },
        {
          "more_like_this": {
            "fields": ["title", "content.content"],
            "like": [
              {
                "_index": "kemenkeu_regulations",
                "_id": "12345"
              }
            ],
            "min_term_freq": 2,
            "max_query_terms": 25,
            "min_doc_freq": 5,
            "minimum_should_match": "30%"
          }
        }
      ]
    }
  },
  "size": 10
}
```

## Performance Optimization Queries

### 12. Cached Query with Filters
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "pajak penghasilan",
            "fields": ["title^3", "content.content"]
          }
        }
      ],
      "filter": [
        {
          "bool": {
            "_cache": true,
            "must": [
              {
                "term": {
                  "status": "active"
                }
              },
              {
                "range": {
                  "issue_date": {
                    "gte": "2020-01-01"
                  }
                }
              }
            ]
          }
        }
      ]
    }
  },
  "post_filter": {
    "nested": {
      "path": "policy_areas",
      "query": {
        "term": {
          "policy_areas.code": "TAX"
        }
      }
    }
  }
}
```

## Search Templates

### 13. Parameterized Search Template
```json
{
  "script": {
    "lang": "mustache",
    "source": {
      "query": {
        "bool": {
          "must": [
            {
              "multi_match": {
                "query": "{{query_string}}",
                "fields": [
                  "title^{{title_boost}}",
                  "content.content^{{content_boost}}"
                ]
              }
            }
          ],
          "filter": [
            {
              "term": {
                "status": "{{status}}"
              }
            },
            {{#regulation_types}}
            {
              "terms": {
                "regulation_type": {{regulation_types}}
              }
            },
            {{/regulation_types}}
            {{#date_range}}
            {
              "range": {
                "issue_date": {
                  "gte": "{{date_range.from}}",
                  "lte": "{{date_range.to}}"
                }
              }
            }
            {{/date_range}}
          ]
        }
      },
      "size": "{{size}}",
      "from": "{{from}}"
    }
  },
  "params": {
    "query_string": "pajak penghasilan",
    "title_boost": 3,
    "content_boost": 1,
    "status": "active",
    "regulation_types": ["PMK", "SE"],
    "date_range": {
      "from": "2020-01-01",
      "to": "2024-12-31"
    },
    "size": 20,
    "from": 0
  }
}
```

## Query Performance Guidelines

### Best Practices
1. **Use Filters**: Always use `filter` context for exact matches to leverage caching
2. **Limit Fields**: Use `_source` filtering to return only necessary fields
3. **Pagination**: Use `search_after` for deep pagination instead of `from/size`
4. **Aggregations**: Use `size: 0` when only aggregations are needed
5. **Caching**: Enable query caching for frequently used filter combinations

### Performance Monitoring
```json
{
  "profile": true,
  "query": {
    "match": {
      "title": "pajak"
    }
  }
}
```

This returns detailed timing information for query optimization.