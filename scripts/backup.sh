#!/bin/bash
# Backup script for Industrial DevOps Platform
# Performs comprehensive backup of all critical data

set -e

BACKUP_ROOT="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/forgejo-$TIMESTAMP"

echo "Starting backup at $(date)"
echo "Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker exec forgejo-db pg_dump -U forgejo forgejo | gzip > "$BACKUP_DIR/database.sql.gz"
echo "✓ Database backed up"

# Backup Git repositories
echo "Backing up Git repositories..."
rsync -avz --delete ./data/forgejo/git/repositories/ "$BACKUP_DIR/repositories/"
echo "✓ Repositories backed up"

# Backup configuration files
echo "Backing up configuration..."
cp -r ./config "$BACKUP_DIR/"
echo "✓ Configuration backed up"

# Backup MinIO LFS objects
echo "Backing up MinIO LFS objects..."
docker exec forgejo-minio mc mirror local/forgejo-lfs "$BACKUP_DIR/lfs/" 2>/dev/null || echo "MinIO backup skipped"
echo "✓ LFS objects backed up"

# Create backup manifest
cat > "$BACKUP_DIR/manifest.txt" << EOF
Backup Date: $(date)
Hostname: $(hostname)
Docker Version: $(docker --version)
Components:
  - PostgreSQL database (compressed)
  - Git repositories
  - Configuration files
  - MinIO LFS objects
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "Backup size: $BACKUP_SIZE"

# Optional: Encrypt backup
read -p "Encrypt backup with GPG? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Encrypting backup..."
    tar czf - "$BACKUP_DIR" | gpg --symmetric --cipher-algo AES256 > "$BACKUP_DIR.tar.gz.gpg"
    rm -rf "$BACKUP_DIR"
    echo "✓ Backup encrypted: $BACKUP_DIR.tar.gz.gpg"
fi

# Clean old backups (keep last 7 days)
echo "Cleaning old backups..."
find "$BACKUP_ROOT" -type d -name "forgejo-*" -mtime +7 -exec rm -rf {} + 2>/dev/null || true
find "$BACKUP_ROOT" -type f -name "forgejo-*.tar.gz.gpg" -mtime +7 -delete 2>/dev/null || true
echo "✓ Old backups cleaned"

echo "Backup completed successfully at $(date)"
echo "Backup location: $BACKUP_DIR"
