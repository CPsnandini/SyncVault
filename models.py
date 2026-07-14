import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FileRecord(db.Model):
    """Represents a logical file the user owns. A file can have many versions."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    versions = db.relationship(
        "FileVersion", backref="file", cascade="all, delete-orphan", order_by="FileVersion.version_number"
    )


class FileVersion(db.Model):
    """Represents one specific uploaded version of a file."""
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("file_record.id"), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    storage_name = db.Column(db.String(255), nullable=False)  # actual name on disk (UUID-based)
    size_bytes = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(120))
    checksum_sha256 = db.Column(db.String(64))   
    processing_status = db.Column(db.String(20), default="pending")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


def generate_storage_name(original_filename):
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[1]
    return f"{uuid.uuid4().hex}{ext}"