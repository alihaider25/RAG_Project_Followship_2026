from flask import Blueprint, request, jsonify
from models.db_models import db, ChatSession, Message
from services.vector_store import search_chunks
from services.llm_service import generate_answer
import uuid

chat_bp = Blueprint("chat_bp", __name__)


from models.db_models import db, ChatSession, Message, SessionDocument

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("message")
    session_key = data.get("session_key")

    if not question:
        return jsonify({"error": "No message provided"}), 400

    session = ChatSession.query.filter_by(session_key=session_key).first()
    if not session:
        session_key = str(uuid.uuid4())
        session = ChatSession(session_key=session_key)
        db.session.add(session)
        db.session.commit()

    user_msg = Message(session_id=session.id, role="user", content=question)
    db.session.add(user_msg)
    db.session.commit()

    # NEW: get documents linked to this specific session
    links = SessionDocument.query.filter_by(session_id=session.id).all()
    doc_ids = [link.document_id for link in links]

    # If this session has specific documents attached, search only those.
    # Otherwise fall back to searching everything (for the general/global chat).
    results = search_chunks(question, top_k=3, doc_ids=doc_ids if doc_ids else None)
    context_chunks = results["documents"][0] if results["documents"] else []

    if not context_chunks:
        answer = "I don't have any indexed documents to answer that yet. Please upload a document first."
    else:
        answer = generate_answer(question, context_chunks)

    bot_msg = Message(session_id=session.id, role="assistant", content=answer)
    db.session.add(bot_msg)
    db.session.commit()

    return jsonify({
        "answer": answer,
        "session_key": session_key,
        "sources": context_chunks[:3],
        "user_time": user_msg.created_at.strftime("%I:%M %p"),
        "bot_time": bot_msg.created_at.strftime("%I:%M %p")
    })


@chat_bp.route("/chat/history/<session_key>")
def chat_history(session_key):
    session = ChatSession.query.filter_by(session_key=session_key).first()
    if not session:
        return jsonify({"messages": []})

    messages = Message.query.filter_by(session_id=session.id).order_by(Message.created_at).all()
    return jsonify({
        "messages": [{"role": m.role, "content": m.content} for m in messages]
    })

@chat_bp.route("/chat/sessions")
def list_sessions():
    sessions = ChatSession.query.order_by(ChatSession.created_at.desc()).limit(20).all()

    result = []
    for s in sessions:
        first_msg = Message.query.filter_by(session_id=s.id, role="user").order_by(Message.created_at).first()
        result.append({
            "session_key": s.session_key,
            "preview": (first_msg.content[:40] + "...") if first_msg and len(first_msg.content) > 40 else (first_msg.content if first_msg else "New chat"),
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return jsonify({"sessions": result})

@chat_bp.route("/chat/sessions/<session_key>/delete", methods=["DELETE"])
def delete_session(session_key):
    session = ChatSession.query.filter_by(session_key=session_key).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    Message.query.filter_by(session_id=session.id).delete()
    db.session.delete(session)
    db.session.commit()

    return jsonify({"message": "Session deleted"})