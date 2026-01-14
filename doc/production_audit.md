# Production Audit Report
Date: 2026-01-14

## Django Deployment Check (`check --deploy`)

The following issues were identified by the Django deployment check:

```
?: (security.W004) You have not set SECURE_HSTS_SECONDS to a non-zero value.
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True. Unless your site should be available over both SSL and non-SSL connections, you may want to set this to True.
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.
?: (security.W012) SESSION_COOKIE_SECURE is not set to True. Using a secure-only session cookie makes it more difficult for network traffic sniffers to hijack user sessions.
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
?: (security.W018) You should not have DEBUG set to True in deployment.
```

## Recommendations

1.  **SECURE_HSTS_SECONDS**: Set this to a non-zero integer (e.g., 31536000) to enable HTTP Strict Transport Security.
2.  **SECURE_SSL_REDIRECT**: Set to `True` to force all traffic to HTTPS.
3.  **SECRET_KEY**: Generate a new, long, random secret key for production and set it via the `Django_SECRET_KEY` environment variable.
4.  **SESSION_COOKIE_SECURE** & **CSRF_COOKIE_SECURE**: Set both to `True` to ensure cookies are only sent over HTTPS.
5.  **DEBUG**: Ensure `DEBUG` is set to `False` in the production environment variables (`.env`).

*Note: Some of these warnings (like DEBUG) may appear because the check is running in a development environment where DEBUG is intentionally True.*
