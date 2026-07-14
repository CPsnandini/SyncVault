import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import FileRecord, FileVersion, generate_storage_name
from background_tasks import process_file_version_async
from flask import current_app

file_bp = Blueprint("files", __name__, url_prefix="/files")


@file_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "no file part in request"}), 400
    upload = request.files["file"]
    if upload.filename == "":
        return jsonify({"error": "no file selected"}), 400

    original_name = secure_filename(upload.filename)

    # Does this user already have a file with this name? If so, this upload is a NEW VERSION.
    file_record = FileRecord.query.filter_by(user_id=user_id, filename=original_name).first()
    if not file_record:
        file_record = FileRecord(user_id=user_id, filename=original_name)
        db.session.add(file_record)
        db.session.flush()  # assigns file_record.id without committing yet
        next_version_number = 1
    else:
        last_version = FileVersion.query.filter_by(file_id=file_record.id).order_by(
            FileVersion.version_number.desc()
        ).first()
        next_version_number = (last_version.version_number + 1) if last_version else 1

    storage_name = generate_storage_name(original_name)
    storage_path = os.path.join(current_app.config["STORAGE_DIR"], storage_name)

    upload.save(storage_path)
    size_bytes = os.path.getsize(storage_path)

    version = FileVersion(
        file_id=file_record.id,
        version_number=next_version_number,
        storage_name=storage_name,
        size_bytes=size_bytes,
        content_type=upload.content_type,
    )
    db.session.add(version)
    db.session.commit()
    process_file_version_async(current_app._get_current_object(), version.id, storage_path)

    return jsonify({
        "file_id": file_record.id,
        "filename": file_record.filename,
        "version_number": version.version_number,
        "size_bytes": version.size_bytes,
        "processing_status": version.processing_status,
    }), 201


@file_bp.route("", methods=["GET"])
@jwt_required()
def list_files():
    user_id = int(get_jwt_identity())
    files = FileRecord.query.filter_by(user_id=user_id).order_by(FileRecord.created_at.desc()).all()

    return jsonify([{
        "file_id": f.id,
        "filename": f.filename,
        "latest_version": f.versions[-1].version_number if f.versions else None,
        "total_versions": len(f.versions),
        "created_at": f.created_at.isoformat(),
    } for f in files]), 200


@file_bp.route("/<int:file_id>/versions", methods=["GET"])
@jwt_required()
def list_versions(file_id):
    user_id = int(get_jwt_identity())
    f = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()
    if not f:
        return jsonify({"error": "file not found"}), 404

    return jsonify([{
        "version_number": v.version_number,
        "size_bytes": v.size_bytes,
        "content_type": v.content_type,
        "checksum_sha256": v.checksum_sha256,
        "processing_status": v.processing_status,
        "uploaded_at": v.uploaded_at.isoformat(),
    } for v in f.versions]), 200


@file_bp.route("/<int:file_id>/download", methods=["GET"])
@jwt_required()
def download_file(file_id):
    user_id = int(get_jwt_identity())
    f = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()
    if not f:
        return jsonify({"error": "file not found"}), 404

    version_param = request.args.get("version")
    if version_param:
        version = FileVersion.query.filter_by(file_id=f.id, version_number=int(version_param)).first()
    else:
        version = f.versions[-1] if f.versions else None

    if not version:
        return jsonify({"error": "version not found"}), 404

    storage_path = os.path.join(current_app.config["STORAGE_DIR"], version.storage_name)
    if not os.path.exists(storage_path):
        return jsonify({"error": "file missing from storage"}), 500

    return send_file(storage_path, as_attachment=True, download_name=f.filename)


@file_bp.route("/<int:file_id>", methods=["DELETE"])
@jwt_required()
def delete_file(file_id):
    user_id = int(get_jwt_identity())
    f = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()
    if not f:
        return jsonify({"error": "file not found"}), 404

    for v in f.versions:
        path = os.path.join(current_app.config["STORAGE_DIR"], v.storage_name)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(f)
    db.session.commit()
    return jsonify({"message": "file and all versions deleted"}), 200