# Production deployment

This stack serves the Next.js site and Django API from one HTTPS origin. It
does not start without required secrets, host names, and TLS files.

1. Copy `.env.production.example` to `.env` and replace every placeholder with
   a unique secret. Set `SITE_DOMAIN`, `DJANGO_ALLOWED_HOSTS`, and
   `DJANGO_CSRF_TRUSTED_ORIGINS` to the real domain.
2. Create `ssl/fullchain.pem` and `ssl/privkey.pem` from your certificate
   authority. Point DNS for `SITE_DOMAIN` at this host before issuing a
   certificate. These files must never be committed.
3. From this directory, run `docker compose --env-file .env -f
   docker-compose.prod.yml config` and review the rendered configuration.
4. Start it with `docker compose --env-file .env -f docker-compose.prod.yml up
   -d --build`. Django migrations run before Gunicorn starts.
5. Import and validate the production data before enabling public traffic. The
   tracked database dump is SQLite-formatted, while this production service
   uses MySQL; it is **not** mounted or imported automatically. Test the
   conversion in staging and verify record counts, source URLs, and Kannada
   text before cutover.
6. Verify `https://SITE_DOMAIN/api/v1/health/`, a representative frontend page,
   the certificate chain, and the database backup/restore procedure.

The public proxy deliberately blocks the Django admin. If administration is
needed, expose it only through a separate VPN/bastion ingress with IP access
control. Do not remove that control merely by making the path obscure.

Before each release, run the frontend lint/build, Django checks/tests in a
fresh environment built from `requirements.txt`, and a smoke test against a
staging deployment. Configure external uptime/error monitoring and automated,
encrypted database backups; they cannot be supplied by this repository.
