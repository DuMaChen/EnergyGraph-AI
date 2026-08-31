# Production Deployment & Operations Guide

> Production deployment architecture, Docker Compose orchestration, Caddy HTTPS configuration, and backup strategies.

---

## 1. Production Architecture Overview

The system runs on Docker Compose behind a Caddy reverse proxy that provides automatic SSL termination:

```text
[Internet] --> [Caddy :80/:443] 
                 ├── /         --> [Moodle Container :80]
                 ├── /agent/   --> [Agent UI Container :80]
                 └── /api/     --> [Agent Adapter :8081]
```

### Deployed Services
- **`caddy`**: Reverse proxy, SSL certificates (`energygraph.icu`), header sanitation.
- **`moodle`**: Moodle 4.5 LMS with custom `course_agent` plugin mounted.
- **`db`**: MariaDB 10.11 for Moodle persistence.
- **`agent-adapter`**: FastAPI backend service.
- **`agent-ui`**: Nginx static web server.
- **`flowise` / `qdrant`**: Knowledge base & vector experimentation services (optional/legacy).

---

## 2. Server Deployment Commands

```bash
# 1. Clone repository on server
git clone https://github.com/DuMaChen/EnergyGraph-AI.git /opt/energygraph-ai
cd /opt/energygraph-ai

# 2. Configure production environment
cp deploy/.env.example deploy/.env
# Edit deploy/.env to provide real production secrets and Xingchen keys

# 3. Validate configuration
docker compose --project-directory deploy --env-file deploy/.env config

# 4. Start core services
docker compose --project-directory deploy --env-file deploy/.env up -d --build db moodle agent-adapter agent-ui caddy

# 5. Run smoke verification
bash scripts/smoke_acceptance.sh
```

---

## 3. Backup & Disaster Recovery

- **Automated Backup**: `scripts/backup.sh` creates timestamped backups of MariaDB and Moodle data directory.
- **Cron Setup**: Run `bash scripts/install_backup_cron.sh` to schedule daily backups at 03:00 AM.
- **Recovery Drill**: `bash scripts/full_restore_rehearsal.sh` performs an isolated dry-run database restore to verify backup integrity.
