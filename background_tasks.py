import hashlib
import threading
from extensions import db


def _compute_checksum(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def process_file_version_async(app, version_id, filepath):
    """Runs in a background thread: computes checksum, updates the DB row."""
    def _run():
        with app.app_context():
            from models import FileVersion
            version = FileVersion.query.get(version_id)
            if not version:
                return
            try:
                checksum = _compute_checksum(filepath)
                version.checksum_sha256 = checksum
                version.processing_status = "done"
                db.session.commit()
            except Exception:
                version.processing_status = "failed"
                db.session.commit()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()