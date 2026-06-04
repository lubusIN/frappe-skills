```markdown
# SSL Setup Reference

## Overview
Configure SSL/TLS for Frappe Manager sites using Let's Encrypt or custom certificates.

## Let's Encrypt (Automatic)

### HTTP-01 Challenge
For servers accessible on port 80:

```bash
fm create example.com \
  --apps erpnext:version-15 \
  --environment prod \
  --ssl letsencrypt \
  --letsencrypt-preferred-challenge http01 \
  --letsencrypt-email admin@example.com
```

**Requirements:**
- Domain must point to your server
- Port 80 must be accessible
- Valid email for certificate notifications

### DNS-01 Challenge
For servers behind firewalls or without port 80:

```bash
fm create example.com \
  --apps erpnext:version-15 \
  --environment prod \
  --ssl letsencrypt \
  --letsencrypt-preferred-challenge dns01 \
  --letsencrypt-email admin@example.com
```

**Process:**
1. FM will display a TXT record to add
2. Add the TXT record to your DNS
3. Wait for DNS propagation
4. FM verifies and issues certificate

### Certificate Renewal
Let's Encrypt certificates auto-renew. Check status:

```bash
fm ssl example.com status
```

## Custom Certificates

### Using Existing Certificate
```bash
fm ssl example.com custom \
  --cert-path /path/to/fullchain.pem \
  --key-path /path/to/privkey.pem
```

### Self-Signed (Development)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout selfsigned.key \
  -out selfsigned.crt \
  -subj "/CN=example.localhost"

# Apply to site
fm ssl example.localhost custom \
  --cert-path selfsigned.crt \
  --key-path selfsigned.key
```

## Wildcard Certificates

For multiple subdomains:

```bash
# Requires DNS-01 challenge
fm create *.example.com \
  --ssl letsencrypt \
  --letsencrypt-preferred-challenge dns01 \
  --letsencrypt-email admin@example.com
```

## SSL Management Commands

```bash
# Check SSL status
fm ssl mysite status

# Renew certificate
fm ssl mysite renew

# Disable SSL
fm ssl mysite disable

# Re-enable SSL
fm ssl mysite enable
```

## Nginx SSL Configuration

For manual Nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Proxy to Frappe
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

## Troubleshooting

### Certificate Not Issued
```bash
# Check domain DNS
dig example.com

# Verify port 80 is accessible
curl -v http://example.com

# Check certbot logs
fm logs mysite | grep -i certbot
```

### Certificate Expired
```bash
# Force renewal
fm ssl mysite renew --force

# Check certificate expiry
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Mixed Content Warnings
Ensure `site_config.json` has correct URL:

```json
{
  "host_name": "https://example.com"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Rate limit exceeded | Too many certificate requests | Wait 1 hour, use staging first |
| DNS not propagated | TXT record not available | Wait 5-10 minutes, verify with dig |
| Port 80 blocked | Firewall/ISP restriction | Use DNS-01 challenge |
| CAA record issue | DNS CAA restricts issuers | Add `CAA 0 issue "letsencrypt.org"` |

Sources: Let's Encrypt, Certbot, Nginx SSL (official docs)
```