# Contributing to OrionAI

Thank you for considering contributing to OrionAI. This document outlines the process and guidelines for contributing.

## Development Setup

### Prerequisites

- Python 3.8+
- Docker 20.10+
- kubectl (for Kubernetes development)
- Helm 3.x (for chart development)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/DrashtiPrajapati/OrionAI.git
cd OrionAI
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Copy environment template:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run tests:
```bash
pytest tests/ -v
```

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following our coding standards

3. Write tests for new functionality

4. Run the test suite:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

5. Run linting:
```bash
flake8 .
black --check .
isort --check-only .
```

6. Commit your changes:
```bash
git commit -m "feat: add new feature"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

7. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use Black for formatting
- Use isort for import sorting

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features
- Add inline comments for complex logic

### Testing

- Write unit tests for all new functions
- Write integration tests for API endpoints
- Maintain minimum 80% code coverage
- Use pytest fixtures for test setup
- Mock external dependencies

### Async Code

- Use async/await consistently
- Properly handle async context managers
- Close all async resources
- Test concurrent behavior

## Pull Request Process

1. Update documentation for any changed functionality
2. Add tests covering your changes
3. Ensure all tests pass
4. Update CHANGELOG.md with your changes
5. Request review from maintainers
6. Address review feedback
7. Squash commits before merge (if requested)

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

## Reporting Issues

### Bug Reports

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Potential impact on existing functionality

## Code Review Guidelines

### For Authors

- Keep PRs focused and reasonably sized
- Respond to feedback promptly
- Be open to suggestions
- Test thoroughly before requesting review

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates
- Test locally when possible

## Performance Considerations

- Profile code for performance bottlenecks
- Use async operations for I/O-bound tasks
- Implement caching where appropriate
- Monitor memory usage
- Document performance characteristics

## Security

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP guidelines
- Report security issues privately

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Contact maintainers at support@orionai.dev

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Release notes

Thank you for contributing to OrionAI!
