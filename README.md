# Extraction Library

A Python library for web scraping and data extraction with support for multiple scrapers.

## Features

- **Multiple Scrapers**: Built-in support for Firecrawl, GG.deals, and SoloTodo
- **Database Integration**: SQLAlchemy-based data persistence
- **Airflow Integration**: Tasks for orchestrating scraping workflows
- **Type Safety**: Full type annotations
- **Flexible Configuration**: Environment-based configuration

## Architecture

This project follows Domain-Driven Design (DDD) principles with a clean architecture:

```
src/scraping_utils/
├── core/                   # Core configuration and settings
├── domain/                 # Domain entities and repository interfaces
│   ├── entities/          # Business entities (WebsiteEntity)
│   └── repositories/      # Repository abstractions
├── infrastructure/        # Infrastructure implementations
│   ├── db/               # Database models and services
│   ├── orchestration/    # Airflow tasks and workflows
│   └── scraper/          # Scraper implementations
```

## Installation

### Requirements

- Python 3.12+

### Install Dependencies

```bash
uv sync
```

### Development Dependencies

```bash
uv sync --group dev
```

## Configuration

Create a `.env` file in the project root with your database and Firecrawl settings.

### Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DB__URL` | `sqlite:///./scraped_data.db` | Database connection URL |
| `FIRECRAWL__BASE_URL` | `http://localhost:3002/` | Firecrawl service URL |
| `FIRECRAWL__API_KEY` | `None` | Firecrawl API key |

## Usage

The library provides functionality for:

### Basic Scraping
Scrape websites and save results to JSON files.

### Using Specific Scrapers
Use dedicated scrapers for different websites (Firecrawl, GG.deals, SoloTodo).

### Database Integration
Save and retrieve scraped data using the built-in database service.

## Supported Scrapers

- **Firecrawl**: General-purpose web scraping using Firecrawl service
- **GG.deals**: Gaming deals and product information from `gg.deals`
- **SoloTodo**: Chilean e-commerce price comparison from `solotodo.com`

## Airflow Integration

The library includes pre-built Airflow tasks for orchestrating scraping workflows.

## Data Models

### WebsiteEntity

The core domain entity representing scraped website data with fields for content, metadata, links, images, and tracking information.

## Development

### Adding New Scrapers

Create new scrapers by inheriting from `BaseScraper` and implementing the required methods.

### Code Quality

Run code quality checks using the dev dependencies:

```bash
# Install dev dependencies
uv sync --group dev

# Run linting
uv run ruff check
uv run ruff format
```

## Dependencies

- **Apache Airflow**: Workflow orchestration
- **Pydantic**: Data validation and settings
- **SQLAlchemy**: Database ORM
- **httpx**: HTTP client
- **BeautifulSoup4**: HTML parsing
- **firecrawl-py**: Firecrawl service integration

## License

This project is developed by FarDust (gabriel.faundez@gmail.com).
