# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in OrionAI, please report it by:

1. **Do NOT** open a public issue
2. Email the maintainers directly (if available)
3. Or open a private security advisory on GitHub

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Best Practices

When deploying OrionAI:

1. **API Keys**: Never commit API keys. Use environment variables or `.env` files.
2. **Network**: Deploy behind a firewall or reverse proxy in production.
3. **Authentication**: Add authentication layer for production deployments.
4. **Input Validation**: Sanitize user inputs before processing.
5. **Rate Limiting**: Implement rate limiting to prevent abuse.
6. **Monitoring**: Enable logging and monitoring for suspicious activity.
7. **Updates**: Keep dependencies updated regularly.

## Known Security Considerations

- OrionAI does not include built-in authentication. Add your own auth layer.
- API endpoints are open by default. Secure them in production.
- LLM outputs are not sanitized. Validate before displaying to users.
- Cost tracking is in-memory. Persist to database for production.
