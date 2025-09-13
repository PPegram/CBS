# 📡 Cultural Bias Shield - API Documentation

Complete API reference for integrating with Cultural Bias Shield.

## Base URL
- **Production:** `https://your-backend-url.a.run.app/api`
- **Local Development:** `http://localhost:8080/api`

## Authentication
No authentication required for public API endpoints. Rate limiting applies.

## Content-Type
All API requests must use `application/json` content type.

## Rate Limits
- **Analysis endpoint:** 60 requests per minute per IP
- **Data endpoints:** 300 requests per minute per IP

---

## 🎯 Core Endpoints

### Analyze Campaign
Perform cultural bias analysis on campaign content.

**Endpoint:** `POST /analyze`

**Request Body:**
```json
{
  "campaign_content": "string (required) - Campaign content to analyze",
  "target_countries": ["string"] - Array of ISO country codes (required)",
  "campaign_type": "string - Type of campaign (optional)",
  "industry": "string - Industry context (optional)"
}
```

**Campaign Types:**
- `social_media` (default)
- `display`
- `video`
- `email`
- `outdoor`
- `print`

**Industries:**
- `general` (default)
- `fashion`
- `tech`
- `finance`
- `food`
- `fitness`
- `healthcare`
- `automotive`
- `travel`
- `education`

**Example Request:**
```bash
curl -X POST https://your-backend-url.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_content": "Unlock your potential with our revolutionary fitness app! Join millions of successful individuals who have transformed their lives.",
    "target_countries": ["US", "UK", "JP", "CN"],
    "campaign_type": "social_media",
    "industry": "fitness"
  }'
```

**Response (200 OK):**
```json
{
  "analysis_id": "analysis_20250913_182045",
  "overall_score": 0.73,
  "country_scores": {
    "US": 0.82,
    "UK": 0.78,
    "JP": 0.61,
    "CN": 0.69
  },
  "bias_flags": [
    {
      "type": "cultural_assumption",
      "severity": 6,
      "description": "Western-centric assumptions detected",
      "matches": ["successful individuals", "revolutionary"],
      "cultural_context": "Individual success emphasis may not resonate in collectivist cultures"
    }
  ],
  "cultural_insights": {
    "US": {
      "cultural_fit": "Strong alignment with individualistic values",
      "potential_concerns": "None identified",
      "positive_elements": "Achievement-oriented language resonates well",
      "assumption_risk": 0.2
    },
    "JP": {
      "cultural_fit": "Moderate alignment, some concerns with individual focus", 
      "potential_concerns": "Emphasis on individual success over group harmony",
      "positive_elements": "Transformation and improvement themes",
      "assumption_risk": 0.7
    }
  },
  "recommendations": [
    {
      "country": "JP",
      "priority": "high", 
      "type": "cultural_adaptation",
      "message": "Consider emphasizing community benefits and group success",
      "specific_suggestions": [
        "Replace 'individual success' with 'community wellness'",
        "Add group-oriented benefits and social proof"
      ]
    }
  ],
  "risk_level": "medium",
  "confidence_intervals": {
    "US": {
      "lower_bound": 0.77,
      "upper_bound": 0.87,
      "confidence_level": 0.95,
      "margin_of_error": 0.05,
      "data_quality": 0.9
    }
  },
  "score_breakdown": {
    "US": {
      "cultural_fit": 0.82,
      "bias_penalty": 0.1,
      "confidence_bonus": 0.05,
      "data_quality": 0.9
    }
  },
  "processing_time": "2025-09-13T18:20:45.123Z"
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid input
{
  "error": "Invalid request",
  "message": "campaign_content is required",
  "code": "MISSING_CONTENT"
}

// 429 Too Many Requests
{
  "error": "Rate limit exceeded",
  "message": "Too many requests, please try again in 60 seconds",
  "retry_after": 60
}

// 500 Internal Server Error
{
  "error": "Analysis failed", 
  "message": "Gemini API temporarily unavailable",
  "code": "GEMINI_ERROR"
}
```

---

### Get Supported Countries
Retrieve list of countries with available cultural data.

**Endpoint:** `GET /countries`

**Example Request:**
```bash
curl https://your-backend-url.a.run.app/api/countries
```

**Response (200 OK):**
```json
{
  "countries": [
    {
      "code": "US",
      "name": "United States"
    },
    {
      "code": "UK", 
      "name": "United Kingdom"
    },
    {
      "code": "JP",
      "name": "Japan"
    }
  ],
  "total_count": 107
}
```

---

### Get Cultural Dimensions
Get Hofstede cultural dimensions for specific country.

**Endpoint:** `GET /cultural-dimensions/{country_code}`

**Parameters:**
- `country_code` (required) - ISO country code (e.g., "US", "JP")

**Example Request:**
```bash
curl https://your-backend-url.a.run.app/api/cultural-dimensions/JP
```

**Response (200 OK):**
```json
{
  "country": "JP",
  "dimensions": {
    "power_distance": 54,
    "individualism": 46,
    "masculinity": 95,
    "uncertainty_avoidance": 92,
    "long_term_orientation": 88,
    "indulgence": 42
  },
  "interpretation": {
    "power_distance": "Medium hierarchy acceptance",
    "individualism": "Collectivistic",
    "masculinity": "Achievement-oriented", 
    "uncertainty_avoidance": "High uncertainty avoidance",
    "long_term_orientation": "Long-term oriented",
    "indulgence": "Restrained"
  }
}
```

**Error Response (404):**
```json
{
  "error": "Country not found",
  "message": "No cultural data available for country code: XX"
}
```

---

### Health Check
Check API health and service status.

**Endpoint:** `GET /health`

**Example Request:**
```bash
curl https://your-backend-url.a.run.app/api/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-13T18:20:45.123Z",
  "services": {
    "gemini_api": true,
    "cultural_data": true,
    "bias_detector": true
  },
  "version": "1.0.0",
  "uptime": "2h 15m 30s"
}
```

---

## 🔄 Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## 📊 Data Models

### Bias Flag Object
```json
{
  "type": "string - Type of bias detected",
  "severity": "number - Severity score 1-10",
  "description": "string - Human-readable description",
  "matches": ["string"] - Text patterns that triggered detection",
  "cultural_context": "string - Cultural context explanation"
}
```

**Bias Types:**
- `cultural_assumption` - Assumptions about cultural norms
- `stereotype` - Cultural stereotypes or generalizations  
- `linguistic` - Language that may not translate culturally
- `representation` - Representation bias in examples/imagery

### Cultural Insight Object
```json
{
  "cultural_fit": "string - Assessment of cultural alignment",
  "potential_concerns": "string - Areas of concern",
  "positive_elements": "string - Elements that align well",
  "assumption_risk": "number - Risk score 0.0-1.0"
}
```

### Recommendation Object
```json
{
  "country": "string - Target country code",
  "priority": "string - Priority level (high|medium|low)",
  "type": "string - Type of recommendation",
  "message": "string - Main recommendation message", 
  "specific_suggestions": ["string"] - Actionable suggestions
}
```

---

## 🔌 SDKs & Integration Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

class CulturalBiasShieldAPI {
  constructor(baseURL) {
    this.client = axios.create({
      baseURL: baseURL + '/api',
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  async analyzeCampaign(campaignData) {
    try {
      const response = await this.client.post('/analyze', campaignData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Analysis failed');
    }
  }

  async getCountries() {
    const response = await this.client.get('/countries');
    return response.data.countries;
  }
}

// Usage
const api = new CulturalBiasShieldAPI('https://your-backend-url.a.run.app');

const result = await api.analyzeCampaign({
  campaign_content: "Your campaign text here",
  target_countries: ["US", "UK", "JP"],
  campaign_type: "social_media",
  industry: "tech"
});

console.log('Overall Score:', result.overall_score);
```

### Python
```python
import requests
import json

class CulturalBiasShieldAPI:
    def __init__(self, base_url):
        self.base_url = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def analyze_campaign(self, campaign_data):
        """Analyze campaign for cultural bias"""
        response = self.session.post(f"{self.base_url}/analyze", json=campaign_data)
        response.raise_for_status()
        return response.json()

    def get_countries(self):
        """Get supported countries"""
        response = self.session.get(f"{self.base_url}/countries")
        response.raise_for_status()
        return response.json()['countries']

# Usage
api = CulturalBiasShieldAPI('https://your-backend-url.a.run.app')

result = api.analyze_campaign({
    'campaign_content': 'Your campaign text here',
    'target_countries': ['US', 'UK', 'JP'],
    'campaign_type': 'social_media',
    'industry': 'tech'
})

print(f"Overall Score: {result['overall_score']}")
```

### cURL Examples
```bash
# Analyze campaign
curl -X POST https://your-backend-url.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d @campaign.json

# Get countries
curl https://your-backend-url.a.run.app/api/countries | jq '.countries[]'

# Get cultural dimensions  
curl https://your-backend-url.a.run.app/api/cultural-dimensions/US | jq '.dimensions'

# Health check
curl https://your-backend-url.a.run.app/api/health | jq '.status'
```

---

## ⚡ Performance & Optimization

### Response Times
- **Typical analysis:** 15-30 seconds
- **Countries endpoint:** <500ms  
- **Cultural dimensions:** <200ms
- **Health check:** <100ms

### Caching
- Country data: Cached for 24 hours
- Cultural dimensions: Cached for 7 days
- Health status: No caching

### Optimization Tips
1. **Batch requests** - Analyze multiple countries in single request
2. **Cache responses** - Cache analysis results for identical content
3. **Compress requests** - Use gzip compression for large campaign content
4. **Async processing** - Don't block UI during analysis

---

## 🔐 Security & Privacy

### Data Handling
- Campaign content is **not stored** permanently
- Analysis results are **not logged** with content
- All requests use **HTTPS encryption**
- API keys are **not exposed** in responses

### Privacy Compliance
- **GDPR compliant** - No personal data collection
- **CCPA compliant** - No data selling or tracking
- **SOC 2** - Secure infrastructure on Google Cloud

### Rate Limiting
- **Per-IP limits** to prevent abuse
- **Graceful degradation** during high traffic
- **Retry headers** provided for rate-limited requests

---

## 🐛 Error Handling

### Best Practices
```javascript
async function analyzeCampaignSafely(campaignData) {
  try {
    const result = await api.analyzeCampaign(campaignData);
    return result;
  } catch (error) {
    if (error.response?.status === 429) {
      // Rate limited - wait and retry
      await new Promise(resolve => setTimeout(resolve, 60000));
      return analyzeCampaignSafely(campaignData);
    } else if (error.response?.status >= 500) {
      // Server error - try again later
      console.error('Server error, please try again later');
      return null;
    } else {
      // Client error - fix request
      console.error('Request error:', error.response?.data?.message);
      throw error;
    }
  }
}
```

### Retry Logic
```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1
)

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
```

---

## 📈 Analytics & Monitoring

Track API usage and performance:

### Request Metrics
- Total requests per endpoint
- Response time percentiles
- Error rates by status code
- Geographic distribution of requests

### Business Metrics
- Most analyzed countries
- Common bias patterns detected
- Industry breakdown of requests
- Campaign type popularity

### Alerts
Set up monitoring for:
- High error rates (>5%)
- Slow response times (>45s)
- API quota exhaustion
- Service downtime

---

## 🆕 Changelog

### v1.0.0 (Current)
- ✅ Core analysis endpoint
- ✅ Cultural dimensions API
- ✅ Country listing
- ✅ Health check endpoint
- ✅ Confidence intervals
- ✅ Bias pattern detection

### Planned Features
- 🔄 Batch analysis endpoint
- 🔄 Historical analysis tracking
- 🔄 Custom industry patterns
- 🔄 Webhook notifications
- 🔄 Advanced filtering options

---

## 💬 Support

**API Issues:**
- Check health endpoint first
- Verify request format matches examples
- Ensure valid country codes
- Review rate limit headers

**Documentation:**
- [Main Documentation](../README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [GitHub Issues](https://github.com/yourorg/cultural-bias-shield/issues)

**Contact:**
- Email: api-support@cultural-bias-shield.com
- Discord: [Join our community](https://discord.gg/cultural-ai)