# SyncVault

A secure file synchronization platform supporting versioned uploads, metadata tracking,
and background file processing, built with Flask and JWT authentication.

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Storage:** Local filesystem with UUID-based naming, metadata in SQL
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Concurrency:** Python threading for background checksum computation
- **Frontend:** Vanilla HTML/CSS/JS

## Features
- JWT-authenticated signup/login
- File upload with automatic version detection (re-uploading the same filename creates a new version, not an overwrite)
- Download any specific version, or the latest by default
- Background SHA-256 checksum computation per uploaded version, with live processing status
- Per-user file isolation, enforced at the query level
- File and version deletion (cleans up both database rows and on-disk files)

## Local setup
\`\`\`bash
git clone https://github.com/your-username/SyncVault.git
cd SyncVault
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
\`\`\`

Create a `.env` file:
\`\`\`
SECRET_KEY=your-random-secret
JWT_SECRET_KEY=your-random-jwt-secret
\`\`\`

\`\`\`bash
python app.py
\`\`\`
Visit `http://127.0.0.1:5001`.

## API Overview
| Route | Method | Description |
|---|---|---|
| `/auth/signup` | POST | Create a user |
| `/auth/login` | POST | Get a JWT |
| `/files/upload` | POST | Upload a file (creates a new version if filename exists) |
| `/files` | GET | List all files owned by the user |
| `/files/<id>/versions` | GET | List all versions of a file |
| `/files/<id>/download` | GET | Download latest version (or `?version=N`) |
| `/files/<id>` | DELETE | Delete a file and all its versions |

## Live URL
https://syncvault-production.up.railway.app/