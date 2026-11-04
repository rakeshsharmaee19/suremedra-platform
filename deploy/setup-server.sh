#!/usr/bin/env bash
# One-time server preparation for Ubuntu 24.04 (ARM64 / t4g). Run as a normal user with sudo:
#   bash deploy/setup-server.sh
set -euo pipefail

echo "==> Updating packages"
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg git unzip cron unattended-upgrades

echo "==> Adding 2 GB swap (the server has only 2 GB RAM)"
if ! swapon --show | grep -q /swapfile; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

echo "==> Installing Docker"
if ! command -v docker >/dev/null; then
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER"
fi

echo "==> Installing AWS CLI (used by the backup script)"
if ! command -v aws >/dev/null; then
  ARCH=$(uname -m)
  curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" -o /tmp/awscliv2.zip
  unzip -q -o /tmp/awscliv2.zip -d /tmp
  sudo /tmp/aws/install
fi

echo "==> Enabling automatic security updates"
sudo dpkg-reconfigure -f noninteractive unattended-upgrades

echo
echo "Done. LOG OUT AND LOG IN AGAIN so the 'docker' group takes effect, then continue with docs/AWS_SETUP.md."
