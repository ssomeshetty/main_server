# Karnataka Politicians Tracker API Reference

## Quick Start

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
No authentication required for public data access.

### Response Format
All responses are in JSON format.

## Endpoints

### Districts

#### List Districts
```
GET /api/v1/districts/
```

**Query Parameters:**
- `region` - Filter by region (north, south, central, bangalore)
- `search` - Search by district name
- `page_size` - Number of results per page (default: 20, max: 100)
- `cursor` - Cursor for pagination
- `lang` - Language (en or kn)

**Example:**
```bash
curl "http://localhost:8000/api/v1/districts/?region=north&lang=kn"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/districts/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Bangalore Urban",
      "district_code": "BLR001",
      "region": "bangalore",
      "area_sq_km": 219.36,
      "population_2011": 9308131
    }
  ]
}
```

#### Get District Details
```
GET /api/v1/districts/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Bangalore Urban",
  "district_code": "BLR001",
  "region": "bangalore",
  "area_sq_km": 219.36,
  "population_2011": 9308131
}
```

### Constituencies

#### List Constituencies
```
GET /api/v1/constituencies/
```

**Query Parameters:**
- `district` - Filter by district ID
- `constituency_type` - Filter by type (general, sc, st)
- `search` - Search by constituency name
- `page_size` - Number of results per page
- `cursor` - Cursor for pagination
- `lang` - Language

**Example:**
```bash
curl "http://localhost:8000/api/v1/constituencies/?district=1&lang=kn"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/constituencies/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Bangalore Central",
      "constituency_number": 1,
      "district": 1,
      "district_name": "Bangalore Urban",
      "constituency_type": "general",
      "population_2011": 1000000,
      "male_population": 520000,
      "female_population": 480000,
      "sex_ratio": 923.08,
      "literacy_rate": 85.5
    }
  ]
}
```

#### Get Constituency Details
```
GET /api/v1/constituencies/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Bangalore Central",
  "constituency_number": 1,
  "district": 1,
  "district_name": "Bangalore Urban",
  "constituency_type": "general",
  "population_2011": 1000000,
  "male_population": 520000,
  "female_population": 480000,
  "sex_ratio": 923.08,
  "literacy_rate": 85.5,
  "politician_count": 1,
  "current_politician": {
    "id": 1,
    "name": "John Doe",
    "party": "Democratic Party"
  }
}
```

### Politicians

#### List Politicians
```
GET /api/v1/politicians/
```

**Query Parameters:**
- `district` - Filter by district ID (via constituency)
- `constituency` - Filter by constituency ID
- `party` - Filter by party ID
- `is_active` - Filter by active status
- `is_verified` - Filter by verified status
- `search` - Search by name
- `ordering` - Order results (name, -name, terms_won, -terms_won, etc.)
- `page_size` - Number of results per page
- `cursor` - Cursor for pagination
- `lang` - Language

**Example:**
```bash
curl "http://localhost:8000/api/v1/politicians/?party=1&is_active=true&lang=kn"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/politicians/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "slug": "john-doe",
      "photo_url": "https://example.com/photo.jpg",
      "party_name": "Democratic Party",
      "constituency_name": "Bangalore Central",
      "total_terms_contested": 3,
      "total_terms_won": 2,
      "is_active": true,
      "is_verified": true
    }
  ]
}
```

#### Get Politician Details
```
GET /api/v1/politicians/{id}/
```

**Query Parameters:**
- `lang` - Language

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "full_name_en": "John Doe",
  "full_name_kn": "ಜಾನ್ ಡೊ",
  "photo_url": "https://example.com/photo.jpg",
  "date_of_birth": "1970-01-01",
  "age": 53,
  "gender": "male",
  "email": "john@example.com",
  "phone": "+91 9876543210",
  "residence_address": "123, Main Street, Bangalore",
  "party": {
    "id": 1,
    "name": "Democratic Party",
    "short_name": "DP",
    "party_symbol": "Hand",
    "party_type": "state",
    "is_active": true
  },
  "party_name": "Democratic Party",
  "constituency": {
    "id": 1,
    "name": "Bangalore Central",
    "constituency_number": 1,
    "district": 1,
    "district_name": "Bangalore Urban",
    "constituency_type": "general",
    "population_2011": 1000000
  },
  "district_name": "Bangalore Urban",
  "total_terms_contested": 3,
  "total_terms_won": 2,
  "terms_as_mla": 2,
  "terms_as_mlna": 1,
  "terms_as_mp": 0,
  "terms_as_minister": 1,
  "biography_en": "Full biography in English...",
  "biography_kn": " Kannada ಪೂರ್ಣ ಜೀವನಚರಿತ್ರೆ...",
  "social_media": {
    "facebook": "https://facebook.com/johndoe",
    "twitter": "https://twitter.com/johndoe",
    "instagram": "https://instagram.com/johndoe",
    "youtube": "https://youtube.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe",
    "website": "https://johndoe.example.com"
  },
  "ec_candidate_id": "ECI12345678",
  "is_active": true,
  "is_verified": true,
  "latest_financial_year": 2024,
  "net_worth": 8000000.0
}
```

#### Get Politician Overview
```
GET /api/v1/politicians/{id}/overview/
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "slug": "john-doe",
  "photo_url": "https://example.com/photo.jpg",
  "date_of_birth": "1970-01-01",
  "age": 53,
  "gender": "male",
  "party": {...},
  "constituency": {...},
  "total_terms_contested": 3,
  "total_terms_won": 2,
  "latest_declaration": {...},
  "legal_record_count": 1,
  "public_record_count": 5,
  "social_media": {...},
  "is_active": true,
  "is_verified": true
}
```

### Financial Declarations

#### List Financial Declarations
```
GET /api/v1/financial-declarations/
```

**Query Parameters:**
- `politician` - Filter by politician ID
- `year` - Filter by year
- `year_gte` - Filter by year >= value
- `year_lte` - Filter by year <= value
- `declaration_type` - Filter by type (election, annual, appointment, other)
- `ordering` - Order results (declaration_year, -declaration_year, net_worth, -net_worth)
- `page_size` - Number of results per page
- `cursor` - Cursor for pagination
- `lang` - Language

**Example:**
```bash
curl "http://localhost:8000/api/v1/financial-declarations/?politician=1&year=2024"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/financial-declarations/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "politician": 1,
      "politician_name": "John Doe",
      "politician_slug": "john-doe",
      "party_name": "Democratic Party",
      "declaration_year": 2024,
      "declaration_type": "election",
      "declaration_date": "2024-03-15",
      "declaration_url": "https://example.com/declaration.pdf",
      "total_assets": 10000000.00,
      "total_liabilities": 2000000.00,
      "net_worth": 8000000.00,
      "residential_property_value": 5000000.00,
      "commercial_property_value": 3000000.00,
      "agricultural_land_value": 1000000.00,
      "bank_deposits": 2000000.00,
      "shares_and_securities": 1000000.00,
      "vehicles_value": 500000.00,
      "jewelry_value": 200000.00,
      "is_verified": true
    }
  ]
}
```

#### Get Financial Declaration Details
```
GET /api/v1/financial-declarations/{id}/
```

**Response:**
```json
{
  "id": 1,
  "politician": 1,
  "politician_name": "John Doe",
  "politician_slug": "john-doe",
  "party_name": "Democratic Party",
  "declaration_year": 2024,
  "declaration_type": "election",
  "declaration_date": "2024-03-15",
  "declaration_url": "https://example.com/declaration.pdf",
  "total_assets": 10000000.00,
  "total_liabilities": 2000000.00,
  "net_worth": 8000000.00,
  "residential_property_count": 2,
  "residential_property_value": 5000000.00,
  "commercial_property_count": 1,
  "commercial_property_value": 3000000.00,
  "agricultural_land_acres": 5.5,
  "agricultural_land_value": 1000000.00,
  "bank_deposits": 2000000.00,
  "shares_and_securities": 1000000.00,
  "insurance_policies": 500000.00,
  "loans_received": 0.00,
  "vehicles_count": 2,
  "vehicles_value": 500000.00,
  "jewelry_value": 200000.00,
  "other_assets": 500000.00,
  "personal_loans": 1000000.00,
  "business_loans": 500000.00,
  "mortgage": 500000.00,
  "other_liabilities": 0.00,
  "notes": "Additional notes here",
  "is_verified": true
}
```

### Legal Records

#### List Legal Records
```
GET /api/v1/legal-records/
```

**Query Parameters:**
- `politician` - Filter by politician ID
- `case_status` - Filter by status
- `district` - Filter by district
- `is_verified` - Filter by verified status
- `search` - Search by case number or description
- `ordering` - Order results (fir_date, -fir_date, registration_date, -registration_date)
- `page_size` - Number of results per page
- `cursor` - Cursor for pagination
- `lang` - Language

**Example:**
```bash
curl "http://localhost:8000/api/v1/legal-records/?case_status=trial_in_progress&lang=kn"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/legal-records/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "politician": 1,
      "politician_name": "John Doe",
      "politician_slug": "john-doe",
      "case_number": "FIR/2024/001",
      "police_station": "Test Police Station",
      "district": "Test District",
      "fir_date": "2024-01-15",
      "registration_date": "2024-01-15",
      "case_status": "trial_in_progress",
      "ipc_sections_list": [100, 302],
      "other_sections": [34, 120B],
      "description_en": "Description in English...",
      "description_kn": "Kannada ವಿವರಣೆ...",
      "court_name": "Sessions Court",
      "case_type": "Criminal Case 100",
      "case_url": "https://example.com/case",
      "next_hearing_date": "2024-06-15",
      "is_verified": true
    }
  ]
}
```

#### Get Legal Record Details
```
GET /api/v1/legal-records/{id}/
```

**Response:**
```json
{
  "id": 1,
  "politician": 1,
  "politician_name": "John Doe",
  "politician_slug": "john-doe",
  "case_number": "FIR/2024/001",
  "police_station": "Test Police Station",
  "district": "Test District",
  "fir_date": "2024-01-15",
  "registration_date": "2024-01-15",
  "case_status": "trial_in_progress",
  "ipc_sections_list": [100, 302],
  "other_sections": [34, 120B],
  "description_en": "Description in English...",
  "description_kn": "Kannada ವಿವರಣೆ...",
  "court_name": "Sessions Court",
  "case_type": "Criminal Case 100",
  "case_url": "https://example.com/case",
  "next_hearing_date": "2024-06-15",
  "conviction_date": null,
  "sentence_details": "",
  "fine_amount": null,
  "imprisonment_years": 0,
  "imprisonment_months": 0,
  "source_url": "https://example.com/source",
  "source_organization": "Karnataka Police",
  "verification_date": null,
  "is_verified": true
}
```

### Public Records

#### List Public Records
```
GET /api/v1/public-records/
```

**Query Parameters:**
- `politician` - Filter by politician ID
- `record_type` - Filter by type (speech, statement, controversy, allegation, promise, bill_proposed, initiative)
- `verification_status` - Filter by verification status
- `is_verified` - Filter by verified status
- `event_date_gte` - Filter by event date >= value
- `event_date_lte` - Filter by event date <= value
- `search` - Search by title or content
- `ordering` - Order results (event_date, -event_date, created_at, -created_at)
- `page_size` - Number of results per page
- `cursor` - Cursor for pagination
- `lang` - Language

**Example:**
```bash
curl "http://localhost:8000/api/v1/public-records/?record_type=speech&is_verified=true&lang=kn"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/public-records/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "politician": 1,
      "politician_name": "John Doe",
      "politician_slug": "john-doe",
      "record_type": "speech",
      "title_en": "Test Speech",
      "title_kn": "ಟೆಸ್ಟ್ ಭಾಷಣ",
      "content_en": "This is test content...",
      "content_kn": "ಇದು ಪಠ್ಯದ ಪಠ್ಯವಾಗಿದೆ...",
      "summary_en": "Test summary",
      "summary_kn": "ಟೆಸ್ಟ್ ಸಾರಾಂಶ",
      "categories": ["education", "healthcare"],
      "tags": ["speech", "public"],
      "event_name": "Event Name",
      "event_date": "2024-03-15",
      "location": "Bangalore",
      "verification_status": "verified",
      "is_verified": true,
      "verified_by": "FactChecker Org",
      "verification_date": "2024-03-16",
      "sentiment_score": 0.5,
      "word_count": 500,
      "language": "en",
      "source_url": "https://example.com/speech",
      "source_organization": "News Organization"
    }
  ]
}
```

#### Get Public Record Details
```
GET /api/v1/public-records/{id}/
```

**Response:**
```json
{
  "id": 1,
  "politician": 1,
  "politician_name": "John Doe",
  "politician_slug": "john-doe",
  "record_type": "speech",
  "title_en": "Test Speech",
  "title_kn": "ಟೆಸ್ಟ್ ಭಾಷಣ",
  "content_en": "This is test content...",
  "content_kn": "ಇದು ಪಠ್ಯದ ಪಠ್ಯವಾಗಿದೆ...",
  "summary_en": "Test summary",
  "summary_kn": "ಟೆಸ್ಟ್ ಸಾರಾಂಶ",
  "categories": ["education", "healthcare"],
  "tags": ["speech", "public"],
  "event_name": "Event Name",
  "event_date": "2024-03-15",
  "location": "Bangalore",
  "verification_status": "verified",
  "verification_details": "Verification details here",
  "is_verified": true,
  "verified_by": "FactChecker Org",
  "verification_date": "2024-03-16",
  "sentiment_score": 0.5,
  "word_count": 500,
  "language": "en",
  "source_url": "https://example.com/speech",
  "source_organization": "News Organization"
}
```

### Constituency Funds

#### List Constituency Funds
```
GET /api/v1/constituency-funds/
```

**Query Parameters:**
- `constituency` - Filter by constituency ID
- `fund_type` - Filter by type (mla, mllp, central, other)
- `financial_year` - Filter by financial year
- `project_status` - Filter by project status
- `search` - Search by project name
- `ordering` - Order results (financial_year, -financial_year, allocated_amount, -allocated_amount)
- `page_size` - Number of results per page
- `cursor` - Cursor for pagination
- `lang` - Language

**Example:**
```bash
curl "http://localhost:8000/api/v1/constituency-funds/?financial_year=2024-25&fund_type=mla"
```

**Response:**
```json
{
  "next": "http://localhost:8000/api/v1/constituency-funds/?cursor=cursor_value",
  "previous": null,
  "results": [
    {
      "id": 1,
      "constituency": 1,
      "constituency_name": "Bangalore Central",
      "district_name": "Bangalore Urban",
      "fund_type": "mla",
      "financial_year": "2024-25",
      "allocated_amount": 10000000.00,
      "allocated_date": "2024-04-01",
      "utilized_amount": 5000000.00,
      "utilization_date": "2024-06-15",
      "utilization_percentage": 50.00,
      "remaining_amount": 5000000.00,
      "project_name_en": "Test Project",
      "project_name_kn": "ಟೆಸ್ಟ್ ಪ್ರಾಜೆಕ್ಟ್",
      "project_status": "in_progress",
      "completion_percentage": 50.00,
      "implementing_agency": "Test Agency",
      "contractor_name": "Test Contractor",
      "utilization_url": "https://example.com/fund",
      "notes": "Project notes here"
    }
  ]
}
```

#### Get Constituency Fund Details
```
GET /api/v1/constituency-funds/{id}/
```

**Response:**
```json
{
  "id": 1,
  "constituency": 1,
  "constituency_name": "Bangalore Central",
  "district_name": "Bangalore Urban",
  "fund_type": "mla",
  "financial_year": "2024-25",
  "allocated_amount": 10000000.00,
  "allocated_date": "2024-04-01",
  "utilized_amount": 5000000.00,
  "utilization_date": "2024-06-15",
  "utilization_percentage": 50.00,
  "remaining_amount": 5000000.00,
  "project_name_en": "Test Project",
  "project_name_kn": "ಟೆಸ್ಟ್ ಪ್ರಾಜೆಕ್ಟ್",
  "project_description_en": "Project description...",
  "project_description_kn": "ಪ್ರಾಜೆಕ್ಟ್ ವಿವರಣೆ...",
  "project_status": "in_progress",
  "completion_percentage": 50.00,
  "implementing_agency": "Test Agency",
  "contractor_name": "Test Contractor",
  "fund_source_url": "https://example.com/source",
  "utilization_url": "https://example.com/fund",
  "notes": "Project notes here"
}
```

## Search Examples

### Search Politicians by Name
```bash
curl "http://localhost:8000/api/v1/politicians/?search=rahul"
```

### Search Content by Query
```bash
curl "http://localhost:8000/api/v1/public-records/?search=education"
```

## Error Responses

### 405 Method Not Allowed
```json
{
  "error": {
    "code": "method_not_allowed",
    "message": "Create operations are not allowed. This API is read-only."
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found"
  }
}
```

### 500 Server Error
```json
{
  "error": {
    "code": "server_error",
    "message": "Internal server error"
  }
}
```

## Performance Tips

1. **Use Cursor Pagination**: Avoid page-number pagination for large datasets
2. **Filter Early**: Apply filters before pagination
3. **Use Lang Parameter**: Get only required language content
4. **Request Specific Fields**: Use query parameters to limit fields
5. **Cache Responses**: Implement client-side caching for repeated requests
6. **Use Read Replicas**: For high-traffic applications

## Rate Limiting

Currently, no rate limiting is enforced. For production deployment, consider adding rate limiting:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/minute',
    }
}
```

## Support

For issues and feature requests, please visit our GitHub repository.