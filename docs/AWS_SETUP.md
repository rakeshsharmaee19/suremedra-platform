# AWS Setup and First Deployment

A step-by-step guide for putting the platform live on **one small AWS server**. It assumes you have never used AWS before. Go in order and do not skip the checks.

> AWS changes its screens from time to time. If a button has moved, search for the name in the AWS console search bar. Prices quoted are estimates (Mumbai region, excluding GST). Check the AWS Pricing Calculator before you commit.

**What you will have at the end**

```
Internet -> Caddy (HTTPS, automatic certificates) on one EC2 server
              |-- www.yourdomain.com   -> Next.js website  (+ /api/* -> Django)
              |-- admin.yourdomain.com -> Django admin portal
              `-- Docker containers: PostgreSQL, Redis, Celery worker
S3 bucket: invoice PDFs + hourly database backups
```

**Estimated running cost: about USD 19 per month** (EC2 about 8, disks about 4.5, public IP about 3.7, small extras about 2.5). New AWS accounts may receive free credits; see the proposal.

> **Why no CloudFront yet?** CloudFront (a CDN) adds more settings (certificates in another region, cache rules). Phase 1 traffic (about 1,000 users) does not need it, and Caddy gets HTTPS certificates by itself. You can add CloudFront later (Appendix A) without changing the code.

---

## Part 0. Gather these first

- [ ] The **domain** the client bought, and login access to wherever its DNS is managed (the registrar).
- [ ] A **company email address** for the AWS account (use the client's, so they own the account).
- [ ] A credit/debit card that works for international online payments.
- [ ] A **Google Workspace mailbox** on the company domain for sending notifications, for example `notifications@yourdomain.com`.
- [ ] The code in a **private GitHub repository** (create one and push this project).
- [ ] A password manager to store every secret you create.

---

## Part 1. Create and secure the AWS account

1. Go to https://aws.amazon.com and choose **Create an AWS account**. Use the company email and the company name. Choose the **paid plan** (the credits for new accounts still apply; the free plan expires after 6 months and restricts services).
2. Sign in as the **root user**, then turn on **MFA** (Account name, top right > **Security credentials** > **Assign MFA device**, use an authenticator app).
3. Create a daily-use user so you never use root again: search for **IAM** > **Users** > **Create user** (name `admin-yourname`), tick **Provide user access to the AWS Management Console**, choose **Attach policies directly** > `AdministratorAccess`. Then add MFA for this user too. Sign out of root and sign in as this user from now on.
4. **Billing alert:** search **Billing** > **Budgets** > **Create budget** > Cost budget > monthly, amount **USD 50**, alert at **80%** to your email. This warns you if something is left running by mistake.
5. Set the **region** (top right) to **Asia Pacific (Mumbai) ap-south-1**. Every step below must be done in this region.

**Check:** MFA is on for root and for your user; you can see the Mumbai region selected.

---

## Part 2. Create the S3 bucket (invoice PDFs and backups)

1. Search **S3** > **Create bucket**.
2. Name: `suremedra-prod-files-xxxx` (names are global, so add a few random letters or digits). Region: Mumbai.
3. Leave **Block all public access** **ON** (all four boxes ticked). Turn **Bucket Versioning** to **Enable**. Create the bucket.
4. Open the bucket > **Management** > **Create lifecycle rule**:
   - Name `expire-backups`, scope: **prefix** `backups/`.
   - Actions: **Expire current versions** after **90 days**; **Permanently delete noncurrent versions** after **7 days**; **Delete expired object delete markers and incomplete multipart uploads** (7 days).
5. Note the bucket name. You will paste it in `.env.prod` twice (`AWS_STORAGE_BUCKET_NAME` and `BACKUP_S3_BUCKET`).

---

## Part 3. Give the server permission to use the bucket (IAM role)

The server gets permission through a **role**, so no secret keys are ever stored on it.

1. **IAM** > **Policies** > **Create policy** > **JSON**. Paste this (replace `BUCKET` with your bucket name, twice):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::BUCKET",
      "Condition": { "StringLike": { "s3:prefix": ["media/*", "backups/*"] } }
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::BUCKET/media/*", "arn:aws:s3:::BUCKET/backups/*"]
    }
  ]
}
```

Name it `suremedra-s3-access` and create it.

2. **IAM** > **Roles** > **Create role** > trusted entity **AWS service** > **EC2**. Attach two policies: `suremedra-s3-access` and `AmazonSSMManagedInstanceCore` (this lets you open a terminal from the browser if SSH ever fails). Name the role `suremedra-ec2-role`.

---

## Part 4. Firewall (security group)

**EC2** > **Security Groups** > **Create security group**, name `suremedra-web-sg`, default VPC. Inbound rules:

| Type | Port | Source |
|---|---|---|
| HTTP | 80 | Anywhere IPv4 (0.0.0.0/0) |
| HTTPS | 443 | Anywhere IPv4 (0.0.0.0/0) |
| Custom UDP | 443 | Anywhere IPv4 (optional, faster HTTP/3) |
| SSH | 22 | **My IP** (only your own address) |

Leave outbound as it is. If your home or office IP changes later, edit the SSH rule.

---

## Part 5. Launch the server (EC2)

**EC2** > **Instances** > **Launch instances**:

| Setting | Value |
|---|---|
| Name | `suremedra-prod` |
| AMI | **Ubuntu Server 24.04 LTS**, architecture **64-bit (Arm)** |
| Instance type | **t4g.small** (2 vCPU, 2 GB RAM) |
| Key pair | **Create new key pair**, name `suremedra-key`, type ED25519, format `.pem`. It downloads once: store it safely (password manager or encrypted drive). |
| Network | Default VPC, a public subnet, **Auto-assign public IP: Enable** |
| Security group | Select existing: `suremedra-web-sg` |
| Storage | Volume 1 (root): **20 GiB gp3**. Click **Add new volume**: **20 GiB gp3** (this is the database disk). For this second volume set **Delete on termination: No**. |
| Advanced details | **IAM instance profile**: `suremedra-ec2-role`. **Termination protection**: Enable. |

Click **Launch instance**.

**Name the disks** (so you can recognise them): **EC2** > **Volumes**, select each volume > **Manage tags**. Add tag `Name = suremedra-root` and `Name = suremedra-data`. On **both** also add `Backup = daily` (used in Part 12).

---

## Part 6. Fixed IP address and DNS

1. **EC2** > **Elastic IPs** > **Allocate Elastic IP address** > Allocate. Select it > **Actions** > **Associate Elastic IP address** > choose your instance > Associate. Write the IP down.
2. At the **domain registrar's DNS settings** add three **A records** pointing to that IP:

| Host / Name | Type | Value |
|---|---|---|
| `@` (the bare domain) | A | your Elastic IP |
| `www` | A | your Elastic IP |
| `admin` | A | your Elastic IP |

   Use a short TTL (300 seconds) while setting up. If the registrar already has a default parking record for `@` or `www`, delete it.
3. **Check** (takes 5 to 60 minutes): `nslookup www.yourdomain.com` should show your Elastic IP. **Do not start the site until all three names resolve**, because the HTTPS certificates are requested at first start.

---

## Part 7. Connect and prepare the server

1. On your computer (Mac, Linux, or Windows PowerShell):

```bash
chmod 400 suremedra-key.pem          # Windows: skip this line
ssh -i suremedra-key.pem ubuntu@YOUR_ELASTIC_IP
```

   Type `yes` when asked about the fingerprint. If it hangs, your IP has changed (fix the SSH rule in Part 4). Fallback: **EC2** > select instance > **Connect** > **Session Manager**.

2. Create a deploy key so the server can read your private repository:

```bash
ssh-keygen -t ed25519 -C "suremedra-server" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

   Copy the output. In GitHub: your repository > **Settings** > **Deploy keys** > **Add deploy key** > paste, leave "Allow write access" **unticked**.

3. Download the code and run the one-time setup script (installs Docker, adds swap memory, installs the AWS CLI, turns on automatic security updates):

```bash
sudo mkdir -p /opt/suremedra && sudo chown ubuntu:ubuntu /opt/suremedra
git clone git@github.com:YOUR_ORG/YOUR_REPO.git /opt/suremedra
cd /opt/suremedra
bash deploy/setup-server.sh
```

4. **Log out and log in again** (`exit`, then `ssh ...`) so Docker permissions apply. Check:

```bash
docker --version && docker compose version && aws --version && free -h
```

   `free -h` should show about 2 GB of swap.

---

## Part 8. Mount the database disk

The second 20 GB disk must be formatted once and mounted at `/data`. **Be careful: formatting the wrong disk erases it.**

```bash
lsblk
```

You will see two disks. The one with a partition mounted at `/` is the root disk (small partitions, usually `nvme0n1`). The **other 20 GB disk with no mount point** (usually `nvme1n1`) is the data disk.

```bash
sudo file -s /dev/nvme1n1        # must print just "data" (an empty disk). If it names a filesystem, STOP.
sudo mkfs -t ext4 /dev/nvme1n1
sudo mkdir -p /data
sudo mount /dev/nvme1n1 /data
echo "UUID=$(sudo blkid -s UUID -o value /dev/nvme1n1) /data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mkdir -p /data/postgres /data/backups
sudo chown ubuntu:ubuntu /data/backups
df -h /data
```

**Check:** `df -h /data` shows about 20 GB. Reboot test (optional): `sudo reboot`, log back in, and `df -h /data` still works.

---

## Part 9. Configure the application

```bash
cd /opt/suremedra
cp .env.example.prod.example .env.example.prod
nano .env.example.prod
```

Fill in every value (Ctrl+O then Enter saves, Ctrl+X exits). Useful commands for secrets:

```bash
openssl rand -hex 24                                        # database password (letters and digits only)
python3 -c "import secrets; print(secrets.token_urlsafe(50))"   # DJANGO_SECRET_KEY
```

Points to get right:

- `DOMAIN` = `www.yourdomain.com`, `REDIRECT_DOMAIN` = `yourdomain.com`, `ADMIN_DOMAIN` = `admin.yourdomain.com` (no `https://`).
- Use the **same database password** in `POSTGRES_PASSWORD` and inside `DATABASE_URL`.
- `DJANGO_ALLOWED_HOSTS` must include `api` and `localhost` as in the example.
- `AWS_STORAGE_BUCKET_NAME` and `BACKUP_S3_BUCKET` = your bucket name.
- **Email:** `EMAIL_HOST_USER` is the Workspace mailbox. For `EMAIL_HOST_PASSWORD` create an **app password**: sign in to that Google account > **Security** > turn on **2-Step Verification** > **App passwords** > create one > paste the 16 characters without spaces. (Google's rules change; if the option is missing, ask the Workspace administrator to allow app passwords or SMTP relay.)
- `ADMIN_NOTIFICATION_EMAILS`: people who should get new-enquiry emails (comma separated).
- Keep `ADMIN_2FA=false` for now. You enable it in Part 11.

**Save a copy of `.env.prod` in the password manager.** It is not in Git and you need it if the server must be rebuilt.

---

## Part 10. First start

```bash
cd /opt/suremedra
bash deploy/deploy.sh
```

The first run builds the images (about 5 to 15 minutes on this small server; the swap file prevents out-of-memory failures), applies the database migrations and starts everything.

Then create the roles, your login, and load data:

```bash
alias dc='docker compose --env-file .env.example.prod -f docker-compose.prod.yml'
dc ps                                           # every service should be "running" (api "healthy")
dc run --rm api python manage.py setup_roles
dc run --rm api python manage.py createsuperuser
```

To import the first medicines, copy your CSV from your computer (run this on **your computer**, not the server):

```bash
scp -i suremedra-key.pem medicines.csv ubuntu@YOUR_ELASTIC_IP:/tmp/medicines.csv
```

Then on the server (try the dry run first; it saves nothing):

```bash
docker cp /tmp/medicines.csv $(dc ps -q api):/tmp/medicines.csv
dc exec api python manage.py import_medicines /tmp/medicines.csv --dry-run
dc exec api python manage.py import_medicines /tmp/medicines.csv
```

(You can also upload the CSV in the admin: **Medicines** > **Import CSV**.)

---

## Part 11. Smoke test

- [ ] `https://www.yourdomain.com` opens, with a padlock. `https://yourdomain.com` redirects to `www`.
- [ ] `https://www.yourdomain.com/catalogue` lists medicines; search for a composition works.
- [ ] `https://www.yourdomain.com/api/health` shows `{"status": "ok", "database": "up"}`.
- [ ] `https://admin.yourdomain.com` shows the admin login. Log in.
- [ ] Submit a test enquiry from the website. Within a minute: you see the notification on the admin dashboard and receive the emails.
- [ ] Open the enquiry in the admin, fill availability/medicine/price, click **Generate invoice**, and check the PDF arrives by email.
- [ ] Look at the logs (`dc logs --tail=50 api worker`) and confirm the lines for the test enquiry are there.

**Turn on admin two-factor login** (see `docs/OPERATIONS.md`, section "Admin two-factor login"). Do this **before** real users get access.

If HTTPS does not work, the cause is almost always DNS (the name does not point to the Elastic IP yet). Check `dc logs caddy`; Caddy retries automatically.

---

## Part 12. Backups (do not skip)

1. **Hourly database dump to S3.** Test it once by hand:

```bash
cd /opt/suremedra && bash deploy/backup.sh && cat /data/backups/backup.log
```

   Then open the S3 console and confirm a file appeared under `backups/`. Schedule it:

```bash
crontab -e
```

   Add this line at the bottom, save and exit:

```
0 * * * * /opt/suremedra/deploy/backup.sh >> /data/backups/cron.log 2>&1
```

2. **Daily disk snapshots.** **EC2** > **Lifecycle Manager** > **Create lifecycle policy** > **EBS snapshot policy**. Target resource type **Volume**, target tag `Backup = daily`, schedule **daily** at e.g. 21:00 UTC, retain **7** snapshots, use the default role. Create.
3. **Restore drill.** Do this once now, while nothing depends on it: follow "Restore the database" in `docs/OPERATIONS.md` using a dump from S3. A backup you have never restored is only a hope.

---

## Part 13. Alerts

1. **Server health:** **CloudWatch** > **Alarms** > **Create alarm** > metric **EC2 > Per-Instance Metrics > StatusCheckFailed_System** for your instance, condition `>= 1` for 2 periods of 1 minute. Actions: **Notification** to a new SNS topic with your email (confirm the email AWS sends), and **EC2 action: Recover this instance**.
2. **CPU credits** (this server type slows down when credits run out): same screen, metric **CPUCreditBalance**, condition `< 20` for 15 minutes, notify the same topic.
3. **Website down:** register the URL `https://www.yourdomain.com/api/health` in a free uptime monitor (for example UptimeRobot) with email alerts.
4. **Disk space** (check monthly): `df -h /data /` and `docker system df`.

---

## Part 14. After launch

- Verify the domain in **Google Search Console** (Domain property, DNS TXT record), submit `https://www.yourdomain.com/sitemap.xml`, and request indexing of the home, About, Certifications and Contact pages. Create the **Google Business Profile**. Both are free.
- Add real descriptions to the main formulations (admin > **Formulations**) so those pages have useful text for Google.
- Updating the site later is one command: `cd /opt/suremedra && bash deploy/deploy.sh`.

---

## Appendix A. Adding CloudFront later (optional)

Add it when you see slow pages for overseas visitors or traffic grows. In outline: request a certificate in **us-east-1** (ACM) for `www.yourdomain.com`; create a CloudFront distribution with the origin `origin.yourdomain.com` (a new A record to the Elastic IP, with its own Caddy site block), forward all headers/cookies/query strings for `/api/*`, `/admin*` and `/_next/data*`, cache `/_next/static/*` for a year; then point `www` at CloudFront. Keep the admin subdomain direct to the server.

## Appendix B. Moving to RDS and Amazon SES (Phase 2 or 3)

- **RDS:** create a PostgreSQL 16 instance (`db.t4g.micro`, not publicly accessible, security group allowing port 5432 only from the server's group). Take a fresh dump with `deploy/backup.sh`, restore it into RDS with `pg_restore`, change `DATABASE_URL`, remove the `db` service, redeploy. Move when payments start, when a second app server is added, or when you need point-in-time recovery.
- **SES:** verify the domain (add the DKIM, SPF and DMARC DNS records AWS gives you), request **production access**, create SMTP credentials, then change only `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env.prod`. No code changes.

## Appendix C. Cost checklist

| Item | Approx. per month |
|---|---|
| EC2 t4g.small | USD 8.2 |
| EBS disks 40 GB + snapshots | USD 4.5 |
| Public IPv4 address | USD 3.7 |
| S3, CloudWatch alarms, small extras | USD 2.3 |
| **Total AWS** | **about USD 19** |
| Google Workspace mailbox | per user, billed by Google |
| Domain | yearly, billed by the registrar |

To stop all charges: terminate the instance, delete the volumes and snapshots, release the Elastic IP, empty and delete the bucket. (Termination protection must be turned off first.)
