# Litestar Template 🚀

<div align="center">

![Litestar](https://raw.githubusercontent.com/litestar-org/litestar/main/docs/images/litestar-logo.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)

A reusable base template for building fast and reliable APIs using Litestar.

[Features](#features) • [Getting Started](#getting-started) • [Project Structure](#project-structure) • [Development](#development)

</div>

## 🌟 Features

- ⚡ **High Performance**: Built on top of Litestar, one of the fastest Python web frameworks
- 🔒 **Security First**: Built-in security features with JWT authentication and Argon2 password hashing
- 🗄️ **Database Integration**: SQLAlchemy with async PostgreSQL support
- 🔄 **Message Queue**: NATS integration for reliable message queuing
- 🚀 **Modern Stack**: 
  - Python 3.12
  - Litestar 2.x
  - Msgspec for data validation and serialization
  - SQLAlchemy 2.0
  - Granian ASGI server
  - Redis for caching
  - Dishka for dependency injection
  - uv for fast and reliable package management

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- NATS
- uv package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ocbunknown/litestar-template.git
cd litestar-template
```

2. Install dependencies:
```bash
uv sync --all-groups
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
python -m src
```

## 📁 Project Structure

```
litestar-template/
├── src/
│   ├── api/                # API routes and controllers
│   ├── core/              # Core application logic
│   ├── database/          # Database models and migrations
│   ├── services/          # Business logic services
│   ├── common/            # Shared utilities and helpers
│   ├── __init__.py       # Package initialization
│   └── __main__.py       # Application entry point
├── tests/                 # Test suite
├── migrations/            # Alembic migrations
├── nats/                 # NATS configuration and handlers
├── jetstream/            # JetStream configuration
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── alembic.ini          # Alembic configuration
├── docker-compose.dev.yml # Development Docker Compose
├── Dockerfile           # Docker configuration
├── makefile            # Make commands
└── pyproject.toml      # Project dependencies and configuration
```

## 🛠️ Development

### Code Quality

This project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter
- **MyPy**: Static type checking
- **Pre-commit**: Git hooks for code quality
- **Pytest**: Testing framework

### Running Tests

```bash
pytest
```

### Code Style

The project follows strict code style guidelines enforced by Ruff and MyPy. Run the following commands to check your code:

```bash
ruff check .
mypy .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [Litestar](https://github.com/litestar-org/litestar) - The amazing web framework this template is built on
- [Msgspec](https://github.com/jcrist/msgspec) - Fast and friendly JSON serialization
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- All the open-source libraries that make this template possible 