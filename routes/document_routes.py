import os
import uuid
from flask import Blueprint, request, jsonify, render_template
from models.db_models import db, Document
from services.document_service import extract_text, chunk_text
from services.vector_store import add_document_chunks, delete_document_chunks
from models.db_models import db, Document, ChatSession, SessionDocument
document_bp = Blueprint("document_bp", __name__)

UPLOAD_FOLDER = "static/uploads"

@document_bp.route("/documents")
def documents_page():
    documents = Document.query.order_by(Document.upload_date.desc()).all()
    return render_template("documents.html", documents=documents)



@document_bp.route("/upload", methods=["POST"])
def upload_document():
    file = request.files.get("file")
    session_key = request.form.get("session_key")  # NEW

    if not file:
        return jsonify({"error": "No file provided"}), 400

    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    new_doc = Document(filename=file.filename, status="processing")
    db.session.add(new_doc)
    db.session.commit()

    try:
        text = extract_text(filepath)
        chunks = chunk_text(text)
        add_document_chunks(new_doc.id, chunks)

        new_doc.status = "indexed"
        new_doc.chunk_count = len(chunks)
        db.session.commit()

        # NEW: link this document to the current chat session
        if session_key:
            session = ChatSession.query.filter_by(session_key=session_key).first()
            if not session:
                session = ChatSession(session_key=session_key)
                db.session.add(session)
                db.session.commit()

            link = SessionDocument(session_id=session.id, document_id=new_doc.id)
            db.session.add(link)
            db.session.commit()

        return jsonify({
            "message": "File uploaded and indexed",
            "id": new_doc.id,
            "filename": new_doc.filename,
            "status": new_doc.status,
            "chunk_count": new_doc.chunk_count
        })

    except Exception as e:
        new_doc.status = "failed"
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@document_bp.route("/documents/<int:doc_id>/delete", methods=["DELETE"])
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    delete_document_chunks(doc_id)
    db.session.delete(doc)
    db.session.commit()

    return jsonify({"message": "Document deleted"})