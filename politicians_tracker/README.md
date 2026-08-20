# Karnataka Politicians Tracker

An open-source public tracker for Karnataka politicians built with Django (DRF) and MySQL. This system provides comprehensive bilingual (English/Kannada) data with high-performance optimized queries for up to 1 million daily hits.

## Features

- 📊 **Comprehensive Data**: Politician profiles, financial declarations, legal records, and public records
- 🌐 **Bilingual Support**: Native English and Kannada content with optimized database queries
- ⚡ **High Performance**: MySQL-optimized with cursor-based pagination and proper indexing
- 🔒 **Read-Only Security**: Middleware-enforced read-only API
- 📱 **Mobile Friendly**: Responsive design and API structure
- 🔍 **Advanced Search**: Search across names, constituencies, and content
- 🏛️ **Complete Coverage**: Districts, constituencies, parties, and all politician types

## Technology Stack

- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: MySQL 8.0+ with UTF8MB4 for Kannada support
- **Caching**: Redis (optional but recommended for production)
- **Authentication**: None required (read-only public API)
- **Documentation**: Built-in API docs and Swagger integration

## Project Structure

```
politicians_tracker/
├── apps/
│   └── core/
│       ├── migrations/          # Database migrations
│       ├── tests/               # Test suite
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── exceptions.py
│       ├── middleware.py
│       ├── models.py
│       ├── pagination.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── templates/                   # HTML templates
├── requirements.txt
├── manage.py
├── settings.py
└── urls.py
```

## Installation

## Database backup included

This repository includes the full current database data in two formats:

- [data/db_dump.sql.xz](../data/db_dump.sql.xz) — complete SQL dump of the database
- [data/raw-db/](../data/raw-db/) — exact raw SQLite database split into parts

### Restore the exact raw SQLite database

```bash
cat data/raw-db/db.sqlite3.part-* > db.sqlite3
```

### Restore from the SQL dump

```bash
xzcat data/db_dump.sql.xz | sqlite3 db.sqlite3
```

The raw split parts preserve the full database contents exactly. The SQL dump is also complete and can be used to recreate the same data.

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Redis (recommended for production)
- Virtual environment

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/karnataka-politicians-tracker.git
   cd politicians_tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Admin panel: http://localhost:8000/admin/
   - API: http://localhost:8000/api/v1/
   - Documentation: http://localhost:8000/docs/

## API Usage

### Bilingual Support

All text fields support bilingual content. Use the `lang` parameter to switch between English and Kannada:

```
GET /api/v1/politicians/?lang=kn  # For Kannada content
GET /api/v1/politicians/?lang=en  # For English content (default)
```

### Pagination

All list endpoints use cursor-based pagination:

```
GET /api/v1/politicians/?page_size=20
GET /api/v1/politicians/?page_size=50&cursor=<cursor_value>
```

### Filtering

```bash
# Filter by district
GET /api/v1/politicians/?district=1

# Search by name
GET /api/v1/politicians/?search=john

# Filter by constituency type
GET /api/v1/constituencies/?constituency_type=general

# Filter by financial year
GET /api/v1/constituency-funds/?financial_year=2024-25
```

### Available Endpoints

- `GET /api/v1/districts/` - List all districts
- `GET /api/v1/constituencies/` - List all constituencies
- `GET /api/v1/politicians/` - List all politicians
- `GET /api/v1/politicians/{id}/` - Get politician details
- `GET /api/v1/financial-declarations/` - List financial declarations
- `GET /api/v1/legal-records/` - List legal records
- `GET /api/v1/public-records/` - List public records
- `GET /api/v1/constituency-funds/` - List constituency funds

## Performance Optimizations

### Database

- **Cursor-based pagination**: Avoids expensive OFFSET queries
- **Proper indexing**: Composite indexes on frequently filtered fields
- **Select-related/prefetch-related**: Prevents N+1 query problems
- **Denormalized counts**: Pre-computed term counts for politicians

### Caching

```python
# Example: Cache configuration in settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Read Replicas

For high-traffic scenarios (1M+ hits/day):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'politicians_tracker',
        'USER': 'Politicians_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',  # Primary
        'PORT': '3306',
    },
    'replica': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'politicians_tracker',
        'USER': 'Politicians_user',
        'PASSWORD': 'password',
        'HOST': 'replica-host',  # Read replica
        'PORT': '3306',
    }
}
```

## Deployment

### Production Server (Gunicorn + Uvicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn politicians_tracker.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --access-logfile - \
    --error-logfile -
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "politicians_tracker.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Testing

```bash
# Run all tests
python manage.py test politicians_tracker.apps.core

# Run specific test file
python manage.py test politicians_tracker.apps.core.tests.test_api_endpoints

# Run with coverage
coverage run manage.py test politicians_tracker.apps.core
coverage report
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for the public good to increase transparency in Karnataka politics
- Inspired by similar initiatives across India
- Open source community contributions welcome

## Contact

- GitHub: [https://github.com/yourusername/karnataka-politicians-tracker](https://github.com/yourusername/karnataka-politicians-tracker)
- Issues: [https://github.com/yourusername/karnataka-politicians-tracker/issues](https://github.com/yourusername/karnataka-politicians-tracker/issues)

---

Built with ❤️ for Karnataka