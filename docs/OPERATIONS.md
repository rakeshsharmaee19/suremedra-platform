# Operations Guide

Day-to-day tasks on the production server. Connect with `ssh -i suremedra-key.pem ubuntu@YOUR_ELASTIC_IP`, then:

```bash
cd /opt/suremedra
alias dc='docker compose --env-file .env.example.prod -f docker-compose.prod.yml'
```

(Add the alias line to `~/.bashrc` so it is always available.)

## Is everything running?

```bash
dc ps                              # all services should be "running"; api "healthy"
curl -s https://www.yourdomain.com/api/health
free -h && df -h / /data           # memory and disk
```

## Reading the logs

All backend code logs through Python's `logging` module. On the server the output goes to Docker, which keeps the last 50 MB per container.

```bash
dc logs -f --tail=100 api          # web/API requests and application events
dc logs -f --tail=100 worker       # background jobs: emails, invoice PDFs
dc logs --since 1h api | grep -E "WARNING|ERROR"
dc logs caddy --tail=50            # HTTPS / proxy problems
dc logs db --tail=50               # database (statements slower than 0.5 s are logged)
```

**Follow one request:** every log line carries a request id in square brackets, e.g. `[64caff289be7]`. Find it in the failing request's line (or in the `X-Request-ID` response header) and search for it:

```bash
dc logs --since 24h api | grep 64caff289be7
```

**What to look for**

| Log text | Meaning |
|---|---|
| `Enquiry created: ENQ-...` | A buyer submitted an enquiry |
| `Email queued` / `Email sent` | Mail was handed over / delivered to the SMTP server |
| `Email delivery failed ... attempt=N` | Sending failed; it retries automatically (up to 5 times) |
| `Invoice issued: PI/...` / `Invoice PDF stored` | Invoice created and PDF saved |
| `Honeypot triggered` / `Turnstile rejected` / `Request throttled` | Spam protection at work |
| `No admin recipients configured` | Nobody will receive new-enquiry emails: add admin users or `ADMIN_NOTIFICATION_EMAILS` |
| `Health check failed: database unreachable` | The database container is down |

**Log level and format:** set `LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`) and `LOG_FORMAT` (`text` or `json`) in `.env.prod`, then `dc up -d --force-recreate api worker`.

## Updating the site

```bash
cd /opt/suremedra && bash deploy/deploy.sh
```

This takes a database backup first, pulls the new code, rebuilds, applies migrations and restarts. Visitors may see a few seconds of interruption while containers restart.

**Roll back** a bad release: `git log --oneline -5`, then `git checkout <previous-commit>` and `bash deploy/deploy.sh` (use `git switch main` afterwards). If a database migration was involved, restore the pre-deploy backup (below).

## Changing settings

Edit `.env.prod`, then apply:

```bash
nano .env.example.prod
dc up -d --force-recreate api worker        # backend settings
dc up -d --build web                        # only needed for NEXT_PUBLIC_* / domain changes
dc up -d --force-recreate caddy             # domain changes
```

## Backups

* **Hourly dump to S3** by cron (`deploy/backup.sh`). Check it: `tail /data/backups/backup.log` (the last line should be less than an hour old).
* **Daily EBS snapshots** by Lifecycle Manager (7 kept).
* Invoice PDFs live in S3 (`media/invoices/`), which is versioned.

### Restore the database

Use a dump from S3 (or `/data/backups`):

```bash
aws s3 ls s3://YOUR_BUCKET/backups/ --recursive | tail -5
aws s3 cp s3://YOUR_BUCKET/backups/2026/10/30/suremedra_20261030T040001Z.dump /tmp/restore.dump
bash deploy/restore.sh /tmp/restore.dump           # asks you to type YES; it REPLACES the database
```

The script stops the app, recreates the database, loads the dump and starts the app again. Practise it once after setup, and again every three months.

### If the whole server is lost

1. Launch a new server exactly as in `docs/AWS_SETUP.md` Parts 4 to 8, but attach the **old data volume** (still there, because "delete on termination" was off) in place of a new one. If it is gone, create a volume from the latest **snapshot** (EC2 > Snapshots > Create volume) or restore the latest S3 dump.
2. Put `.env.prod` back (from the password manager), run `bash deploy/deploy.sh`.
3. Move the Elastic IP to the new server (or update the DNS records).

## Admin two-factor login

Enable this before real use. Everyone who logs in to the admin needs an authenticator app (Google Authenticator, Microsoft Authenticator, Authy).

1. Log in to the admin (with `ADMIN_2FA=false`).
2. Open **Otp_Totp > TOTP devices > Add**. Choose your user, give the device a name (for example `phone`), leave the key as generated, and **Save and continue editing**.
3. On the device page, click the **QR code** link and scan it with the app. (The page shows the code only now; if you lose it, delete the device and add a new one.)
4. Repeat for every staff user (each person must scan their own code).
5. Set `ADMIN_2FA=true` in `.env.prod` and run `dc up -d --force-recreate api`.
6. Log out and log in: the login form now asks for a **one-time token**.

**Emergency codes:** `dc run --rm api python manage.py addstatictoken USERNAME` prints a single-use code that works instead of the app.
**Locked out completely:** set `ADMIN_2FA=false`, recreate `api`, log in, fix the device, turn it back on.

## Users and roles

1. Run once: `dc run --rm api python manage.py setup_roles` (creates the groups; safe to repeat after updates).
2. Admin > **Users > Add user**. Tick **Staff status**, enter the email address (needed for alerts), and under **Groups** choose:
   * **Admin**: manage the catalogue, handle enquiries, issue invoices. Cannot delete masters or void invoices.
   * **SuperAdmin**: everything, including users, deleting records and voiding invoices.
3. Everyone in these groups (and superusers) gets in-app notifications and email alerts for new enquiries.

## Common admin tasks

* **Add a medicine:** Admin > Medicines > Add. Choose the brand, type and pack, then add one row per composition with its strength. The public listing (Formulation) is created automatically.
* **Bulk import:** Medicines > **Import CSV** (tick "Check only" first). Format is in `backend/sample_data/medicines_sample.csv`.
* **Hide a medicine from the website:** untick **Is active**.
* **Add text for Google to a listing:** Admin > Formulations > open one > Description. Untick **Is indexable** to keep a thin page out of Google.
* **Answer an enquiry:** open it, set Availability / Medicine / Unit price (and GST if different) on each line, **Save**, then **Generate invoice**.
* **Correct an invoice:** issued invoices cannot be edited. A Super Admin voids it (Invoices > action "Void selected invoices"), then you issue a new one from the enquiry.
* **Resend an invoice email:** Invoices > select > "Re-generate PDF and email to buyer".
* **Failed emails:** Admin > **Email logs** > filter Status = Failed > select > "Retry sending selected emails". The `Error` field shows why (for example Gmail rejecting the app password).

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| Browser shows a certificate error | DNS does not point to the Elastic IP yet, or ports 80/443 are closed in the security group. `dc logs caddy`. |
| 502 Bad Gateway | A container is still starting or crashed. `dc ps`, then `dc logs api` or `dc logs web`. |
| Admin: "CSRF verification failed" | `CSRF_TRUSTED_ORIGINS` must contain `https://admin.yourdomain.com`; recreate `api`. |
| `Invalid HTTP_HOST header` in the logs | Add the hostname to `DJANGO_ALLOWED_HOSTS`; recreate `api`. |
| Catalogue is empty | No **active** medicine has a composition. Check Medicines in the admin. |
| Catalogue shows "temporarily unavailable" | The `api` container is down or `API_INTERNAL_URL` is wrong. `dc ps`. |
| No emails arrive | Admin > Email logs. If Failed: check `EMAIL_HOST_USER` and the Google app password. If Queued: the worker is not running (`dc logs worker`). |
| Invoice PDF fails | `dc logs worker` shows the WeasyPrint error; rebuild the backend image (`dc build api worker`). |
| Image build killed (out of memory) | Check swap with `free -h`. Or build on your laptop and push the images to ECR (ask for a short guide). |
| Disk filling up | `docker system df`, `docker image prune -af`, check `/data/backups` is rotating. |
| Everyone gets "429 Too Many Requests" | The enquiry limit is 5 per hour per IP (`THROTTLE_ENQUIRY`). Raise it only if many buyers share one office IP. |

## Security checklist before launch

- [ ] `DJANGO_DEBUG=false` and a long random `DJANGO_SECRET_KEY`
- [ ] `ADMIN_2FA=true` and every admin has a device
- [ ] SSH restricted to your IP; the key file is stored safely
- [ ] S3 bucket has "Block all public access" on
- [ ] Billing alert and CloudWatch alarms confirmed (you received the confirmation emails)
- [ ] Backup restored successfully at least once
- [ ] `.env.prod` stored in the password manager and not in Git
- [ ] Privacy Policy and Terms reviewed by the company's advisers
