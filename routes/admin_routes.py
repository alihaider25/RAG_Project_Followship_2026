from flask import Blueprint, render_template
from models.db_models import db, Document, ChatSession, Message
from sqlalchemy import func

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/admin")
def admin_dashboard():
    total_documents = Document.query.count()
    indexed_documents = Document.query.filter_by(status="indexed").count()
    total_sessions = ChatSession.query.count()
    total_messages = Message.query.filter_by(role="user").count()

    # Most recent questions (last 10 user messages)
    recent_questions = (
        Message.query.filter_by(role="user")
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )

    # Documents with chunk counts
    documents = Document.query.order_by(Document.upload_date.desc()).all()

    return render_template(
        "admin_dashboard.html",
        total_documents=total_documents,
        indexed_documents=indexed_documents,
        total_sessions=total_sessions,
        total_messages=total_messages,
        recent_questions=recent_questions,
        documents=documents
    )