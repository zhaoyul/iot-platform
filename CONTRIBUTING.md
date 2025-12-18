# Contributing to IoT Platform

Thank you for your interest in contributing to IoT Platform! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/zhaoyul/iot-platform/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, versions, etc.)

### Suggesting Features

1. Check [Issues](https://github.com/zhaoyul/iot-platform/issues) for existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/iot-platform.git
cd iot-platform

# Start development environment
docker-compose up -d

# Run tests
./scripts/run-tests.sh
```

### Coding Standards

#### Go

- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Run `golint` before committing

#### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use `black` for formatting
- Use `pylint` for linting

#### TypeScript/JavaScript

- Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Use `prettier` for formatting
- Use `eslint` for linting

### Commit Messages

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test updates
- `chore`: Build/tooling changes

Example:
```
feat(plc): add support for function block diagrams

Implements FBD parsing and visualization using React Flow.
Supports basic FBD elements and connections.

Closes #123
```

### Testing

- Write unit tests for new features
- Ensure existing tests pass
- Add integration tests where appropriate

### Documentation

- Update README.md if needed
- Add/update API documentation
- Include code comments for complex logic
- Update ARCHITECTURE.md for architectural changes

## Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your PR will be merged

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to ask questions in:
- GitHub Issues
- GitHub Discussions
- Project chat (if available)

Thank you for contributing! 🎉
