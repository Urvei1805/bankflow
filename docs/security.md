# BankFlow Security

## Authentication
- **JWT RS256**: Asymmetric signing with RSA key pair (auto-generated in Docker)
- **HS256 fallback**: Used when RSA keys are unavailable (development)
- **Access token expiry**: 15 minutes
- **Refresh token expiry**: 7 days
- **Refresh token rotation**: Old tokens are revoked on refresh

## Password Security
- **bcrypt** hashing via passlib
- Minimum 8 characters enforced
- Password never stored in plaintext

## API Key Security
- Keys are hashed before storage (bcrypt)
- Only returned once on creation
- Prefix stored for identification

## BOLA Protection
Every user-scoped endpoint validates ownership:
- Transactions: account must belong to the requesting user
- Payments: debtor account must belong to the requesting user
- Consents: consent must belong to the requesting user

## HTTP Security Headers
| Header | Value |
|--------|-------|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000 |
| Cache-Control | no-store |

## Rate Limiting
- 100 requests per minute per IP address
- Uses slowapi (based on limits library)

## CORS
- Configured per service (restrict `allow_origins` in production)

## Secrets Management
- No hardcoded secrets
- `.env` for local development
- AWS Secrets Manager for production (Terraform provisioned)

## CI/CD Security
- Bandit static analysis
- Trivy container scanning
- Dependency vulnerability checks
