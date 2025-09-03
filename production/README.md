Production deployment

- Use `scripts/deploy-production.sh` to generate a per-instance compose file under `production/` and bring it up.
- Integrate with your reverse proxy (e.g., Traefik or NGINX) using the instance port.
- Configure environment secrets via a secure store (e.g., Docker secrets, Azure Key Vault).

