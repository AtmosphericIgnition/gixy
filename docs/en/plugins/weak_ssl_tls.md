# Weak SSL/TLS Configuration Plugin

## Overview

The `weak_ssl_tls` plugin detects insecure SSL/TLS configurations that may compromise the security of encrypted connections. This includes outdated protocols, weak cipher suites, and missing security headers.

## What it detects

### 1. Insecure TLS Protocols
Detects use of deprecated protocols that are vulnerable to attacks:

| Protocol | Status | Vulnerabilities |
|----------|--------|-----------------|
| SSLv2 | ❌ Insecure | Multiple critical flaws |
| SSLv3 | ❌ Insecure | POODLE attack |
| TLSv1.0 | ❌ Insecure | BEAST, POODLE, CRIME |
| TLSv1.1 | ❌ Insecure | Weak ciphers, no AEAD |
| TLSv1.2 | ✅ Secure | Use with strong ciphers |
| TLSv1.3 | ✅ Secure | Modern, recommended |

### 2. Weak Cipher Suites
Detects cipher suites that should be avoided:

- **NULL ciphers** - No encryption at all
- **EXPORT ciphers** - Intentionally weakened (40-56 bit)
- **DES/3DES** - Vulnerable to Sweet32 attack
- **RC4** - Broken stream cipher
- **Anonymous ciphers (ADH/AECDH)** - No authentication
- **MD5-based ciphers** - Weak hash function

### 3. Server Cipher Preference
Detects when `ssl_prefer_server_ciphers` is disabled, allowing clients to choose potentially weaker ciphers.

### 4. Missing HSTS Header
Detects SSL servers missing the `Strict-Transport-Security` header, which protects against:
- Protocol downgrade attacks
- Cookie hijacking
- Man-in-the-middle attacks

### 5. Weak HSTS Configuration
Detects HSTS headers with `max-age` less than 6 months (15768000 seconds).

## Examples

### ❌ Bad: Insecure protocols enabled
```nginx
server {
    listen 443 ssl;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;  # SSLv3, TLSv1, TLSv1.1 are insecure
}
```
**Issue**: `Insecure protocols enabled: SSLv3, TLSv1, TLSv1.1`

### ❌ Bad: Weak ciphers
```nginx
server {
    listen 443 ssl;
    ssl_ciphers ALL:RC4:DES:3DES;  # Includes weak ciphers
}
```
**Issue**: `Weak ciphers found: RC4, DES, 3DES`

### ❌ Bad: Missing HSTS
```nginx
server {
    listen 443 ssl;
    ssl_protocols TLSv1.2 TLSv1.3;
    # Missing: add_header Strict-Transport-Security
}
```
**Issue**: `Missing HSTS header`

### ✅ Good: Secure configuration
```nginx
server {
    listen 443 ssl;

    # Modern protocols only
    ssl_protocols TLSv1.2 TLSv1.3;

    # Mozilla Intermediate cipher suite
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    # Server chooses cipher
    ssl_prefer_server_ciphers on;

    # HSTS with 1 year max-age
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

## Recommended Configuration

Based on [Mozilla's SSL Configuration Generator](https://ssl-config.mozilla.org/):

### Intermediate Configuration (Recommended)
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
```

### Modern Configuration (TLSv1.3 only)
```nginx
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers off;
```

## HSTS Best Practices

```nginx
# Basic HSTS (1 year)
add_header Strict-Transport-Security "max-age=31536000" always;

# With subdomains
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Preload ready (requires HTTPS on all subdomains)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

## Why This Matters

Weak SSL/TLS configurations expose your server to:

1. **POODLE Attack** (SSLv3) - Allows decryption of secure connections
2. **BEAST Attack** (TLSv1.0) - Allows decryption of HTTPS cookies
3. **Sweet32 Attack** (3DES) - Allows recovery of plaintext from long connections
4. **RC4 Bias** - Allows plaintext recovery from encrypted streams
5. **Downgrade Attacks** - Force use of weaker protocols

## Testing Your Configuration

Use these tools to verify your SSL/TLS configuration:

- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
- [Mozilla Observatory](https://observatory.mozilla.org/)
- `openssl s_client -connect yoursite.com:443`

## References

- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Mozilla Server Side TLS Guide](https://wiki.mozilla.org/Security/Server_Side_TLS)
- [OWASP TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)

--8<-- "en/snippets/nginx-extras-cta.md"
