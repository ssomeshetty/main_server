# Tests for Karnataka Politicians Tracker

This directory contains all tests for the Core app.

## Running Tests

```bash
# Run all tests
python manage.py test politicians_tracker.apps.core

# Run specific test file
python manage.py test politicians_tracker.apps.core.tests.test_api_endpoints

# Run specific test class
python manage.py test politicians_tracker.apps.core.tests.test_api_endpoints.APIReadonlyTests

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage
coverage run manage.py test politicians_tracker.apps.core
coverage report
```

## Test Structure

- `test_api_endpoints.py`: API endpoint tests for all resources
- `test_serializers.py`: Serializer validation and transformation tests
- `test_models.py`: Model field and method tests
- `factories.py`: Factory Boy factories for test data generation

## Key Test Coverage

### API Endpoints
- ✅ Read-only enforcement (405 for POST/PUT/PATCH/DELETE)
- ✅ Bilingual support (lang=en/kn parameter)
- ✅ Cursor pagination
- ✅ Query optimization (no N+1 queries)
- ✅ Filtering and search
- ✅ Ordering

### Serializers
- ✅ Field serialization
- ✅ Bilingual field handling
- ✅ Computed fields
- ✅ Language parameter

### Models
- ✅ Field defaults and constraints
- ✅ Model methods
- ✅ Relationships
- ✅ Query optimization