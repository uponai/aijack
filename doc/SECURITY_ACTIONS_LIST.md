# Security Actions Implementation List

Based on the [Security Checklist](SECURITY_CHECKLIST.md) and current project analysis.

## I. Django Application Layer (Priority: High)
*Target: `config/settings.py`*

- [ ] **Force HTTPS**
    - Set `SECURE_SSL_REDIRECT = True`
    - Set `SECURE_HSTS_SECONDS = 31536000` (1 year)
    - Set `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
    - Set `SECURE_HSTS_PRELOAD = True`
- [ ] **Secure Cookies**
    - Set `SESSION_COOKIE_SECURE = True`
    - Set `CSRF_COOKIE_SECURE = True`
- [ ] **Security Headers**
    - Set `SECURE_CONTENT_TYPE_NOSNIFF = True` (`X-Content-Type-Options: nosniff`)
    - Verify `X_FRAME_OPTIONS = 'DENY'` or `'SAMEORIGIN'` (Already in middleware, check value)
- [ ] **Content Security Policy (CSP)**
    - Install `django-csp`
    - Define `CSP_DEFAULT_SRC`, `CSP_SCRIPT_SRC`, `CSP_STYLE_SRC`, etc. to mitigate XSS.
- [ ] **Django Brute Force Protection**
    - Install `django-axes` or similar.
    - Configure `AXES_FAILURE_LIMIT` (e.g., 5 attempts).
    - Configure `AXES_COOLOFF_TIME` (e.g., 1 hour).
    - Ensure it is properly integrated with authentication views.

## II. Infrastructure Layer (Apache) (Priority: Medium)
*Target: `apache/aijack.conf` or global Apache config*

- [ ] **Web Application Firewall (WAF)**
    - Install `libapache2-mod-security2`.
    - Enable OWASP Core Rule Set (CRS).
    - Verify configuration in `/etc/apache2/mods-enabled/security2.conf`.
- [ ] **Rate Limiting / DoS Protection**
    - Install `libapache2-mod-evasive`.
    - Configure `DOSHashTableSize`, `DOSPageCount`, `DOSSiteCount`, `DOSPageInterval` in `/etc/apache2/mods-enabled/evasive.conf`.
- [ ] **Information Leakage Prevention**
    - Add to global config (or VirtualHost):
        ```apache
        ServerTokens Prod
        ServerSignature Off
        ```
    - Ensure Directory Listing is disabled:
        ```apache
        <Directory /var/www/html>
            Options -Indexes
        </Directory>
        ```
- [ ] **SSL/TLS Hardening**
    - Ensure only TLS 1.2 and 1.3 are enabled.
    - Verify Cipher Suites are strong (e.g., using Mozilla SSL Configuration Generator recommendations).

## III. Maintenance & Dependencies (Priority: Ongoing)

- [ ] **Dependency Scanning**
    - Add `pip-audit` to `requirements.txt`.
    - Run `pip-audit` in CI/CD pipeline or manually before deployments.
- [ ] **Secret Management**
    - Rotate `DJANGO_SECRET_KEY` in production environment.
    - Ensure `.env` file permissions are restricted (e.g., `600`).
- [ ] **Logging & Monitoring**
    - Review `aijack_error.log` and `aijack_access.log` settings.
    - Set up a log rotation strategy (`logrotate`).
