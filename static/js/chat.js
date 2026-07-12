let sessionKey = localStorage.getItem("session_key") || null;
function typeWriterEffect(element, htmlContent, speed = 15) {
    const words = htmlContent.split(/(\s+)/); // keep spaces as separate tokens
    let i = 0;
    element.innerHTML = "";

    function typeNext() {
        if (i < words.length) {
            element.innerHTML += words[i];
            i++;
            const chatWindow = document.getElementById("chat-window");
            chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });
            setTimeout(typeNext, speed);
        }
    }
    typeNext();
}
window.addEventListener("DOMContentLoaded", function () {
    loadHistory();
    loadSessionList();

    document.getElementById("collapse-btn").addEventListener("click", function () {
        document.getElementById("sidebar").classList.add("collapsed");
        document.getElementById("expand-btn").classList.remove("d-none");
    });
    document.getElementById("expand-btn").addEventListener("click", function () {
        document.getElementById("sidebar").classList.remove("collapsed");
        document.getElementById("expand-btn").classList.add("d-none");
    });

    document.getElementById("new-chat-btn").addEventListener("click", function () {
        localStorage.removeItem("session_key");
        sessionKey = null;
        document.getElementById("chat-window").innerHTML =
            `<div class="text-muted text-center mt-5">Ask a question about your uploaded documents to get started.</div>`;
        loadSessionList();
    });

    document.getElementById("chat-form").addEventListener("submit", handleSubmit);

    // Working attach/upload icon
    document.getElementById("attach-trigger").addEventListener("click", function () {
        document.getElementById("attach-file-input").click();
    });
    document.getElementById("attach-file-input").addEventListener("change", handleAttachUpload);
});

async function handleAttachUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Ensure a session exists before uploading, so the doc can be linked
    if (!sessionKey) {
        sessionKey = crypto.randomUUID();
        localStorage.setItem("session_key", sessionKey);
    }

    const chip = document.getElementById("attached-chip");
    chip.classList.remove("d-none");
    chip.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Uploading ${file.name}...`;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_key", sessionKey);   // NEW

    try {
        const response = await fetch("/upload", { method: "POST", body: formData });
        const data = await response.json();

        if (response.ok) {
            chip.innerHTML = `<i class="bi bi-file-earmark-check"></i> ${data.filename} indexed (${data.chunk_count} chunks)`;
            setTimeout(() => chip.classList.add("d-none"), 4000);
            loadSessionList();
        } else {
            chip.innerHTML = `<i class="bi bi-exclamation-circle"></i> Upload failed: ${data.error}`;
        }
    } catch (err) {
        chip.innerHTML = `<i class="bi bi-exclamation-circle"></i> Upload failed: ${err}`;
    }

    e.target.value = "";
}

function renderUserMsg(text, time) {
    return `<div class="msg-block">
        <div class="chat-bubble-user">${text}</div>
        <div class="msg-time-user">${time || ""}</div>
    </div>`;
}

function renderBotMsg(html, time, citationsHtml = "") {
    return `<div class="msg-block">
        <div class="chat-bubble-bot">${html}${citationsHtml}</div>
        <div class="msg-time-bot">${time || ""}</div>
    </div>`;
}

async function loadHistory() {
    if (!sessionKey) return;
    try {
        const response = await fetch(`/chat/history/${sessionKey}`);
        const data = await response.json();
        if (data.messages && data.messages.length > 0) {
            const chatWindow = document.getElementById("chat-window");
            chatWindow.innerHTML = "";
            data.messages.forEach(msg => {
                if (msg.role === "user") {
                    chatWindow.innerHTML += renderUserMsg(msg.content, msg.time);
                } else {
                    chatWindow.innerHTML += renderBotMsg(marked.parse(msg.content), msg.time);
                }
            });
            chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });
        }
    } catch (err) { console.error(err); }
}

async function loadSessionList() {
    try {
        const response = await fetch("/chat/sessions");
        const data = await response.json();
        const historyList = document.getElementById("history-list");
        historyList.innerHTML = "";

        if (!data.sessions.length) {
            historyList.innerHTML = `<div class="text-muted small px-2">No past chats yet.</div>`;
            return;
        }

        historyList.innerHTML += `<div class="history-group-label">Recent</div>`;
        data.sessions.forEach(s => {
            const isActive = s.session_key === sessionKey;
            const div = document.createElement("div");
            div.className = "history-item" + (isActive ? " active" : "");
            div.innerHTML = `
                <div class="history-item-text">
                    <div class="history-item-title">${s.preview}</div>
                    <div class="history-item-time">${s.created_at}</div>
                </div>
                <button class="history-menu-btn"><i class="bi bi-three-dots"></i></button>
            `;
            div.querySelector(".history-item-text").addEventListener("click", () => switchSession(s.session_key));
            div.querySelector(".history-menu-btn").addEventListener("click", (e) => {
                e.stopPropagation();
                toggleDropdown(div, s.session_key);
            });
            historyList.appendChild(div);
        });
    } catch (err) { console.error(err); }
}

function toggleDropdown(container, key) {
    const existing = document.querySelector(".history-dropdown");
    if (existing) existing.remove();

    const dropdown = document.createElement("div");
    dropdown.className = "history-dropdown";
    dropdown.innerHTML = `<button class="danger delete-btn">Delete</button>`;
    container.appendChild(dropdown);

    dropdown.querySelector(".delete-btn").addEventListener("click", async (e) => {
        e.stopPropagation();
        if (!confirm("Delete this chat?")) return;
        await fetch(`/chat/sessions/${key}/delete`, { method: "DELETE" });
        if (key === sessionKey) {
            sessionKey = null;
            localStorage.removeItem("session_key");
            document.getElementById("chat-window").innerHTML =
                `<div class="text-muted text-center mt-5">Ask a question about your uploaded documents to get started.</div>`;
        }
        loadSessionList();
    });

    document.addEventListener("click", function closeMenu() {
        dropdown.remove();
        document.removeEventListener("click", closeMenu);
    }, { once: true });
}

function switchSession(key) {
    sessionKey = key;
    localStorage.setItem("session_key", key);
    loadHistory();
    loadSessionList();
}

async function handleSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    const chatWindow = document.getElementById("chat-window");
    if (chatWindow.querySelector(".text-muted.text-center")) chatWindow.innerHTML = "";

    chatWindow.innerHTML += renderUserMsg(message, "");
    input.value = "";
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });

    const loadingId = "loading-" + Date.now();
    chatWindow.innerHTML += `<div class="msg-block" id="${loadingId}"><div class="chat-bubble-bot"><span class="spinner-border spinner-border-sm"></span> Thinking...</div></div>`;
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message, session_key: sessionKey })
        });

        if (!response.ok) {
            document.getElementById(loadingId).outerHTML = `<div class="msg-block"><div class="chat-bubble-bot text-danger">Server error (${response.status}).</div></div>`;
            return;
        }

        const data = await response.json();

        if (data.session_key) {
            sessionKey = data.session_key;
            localStorage.setItem("session_key", sessionKey);
            loadSessionList();
        }

        let citationsHtml = "";
        if (data.sources && data.sources.length > 0) {
            citationsHtml = `<div class="mt-2">` +
                data.sources.map((src, i) =>
                    `<span class="badge" title="${src.replace(/"/g, '&quot;')}"><i class="bi bi-file-earmark-text"></i> Source ${i + 1}</span>`
                ).join(" ") +
                `</div>`;
        }

        const msgBlock = document.createElement("div");
        msgBlock.className = "msg-block";
        msgBlock.innerHTML = `<div class="chat-bubble-bot"></div><div class="msg-time-bot">${data.bot_time || ""}</div>`;
        document.getElementById(loadingId).replaceWith(msgBlock);

        const bubbleEl = msgBlock.querySelector(".chat-bubble-bot");
        typeWriterEffect(bubbleEl, marked.parse(data.answer) + citationsHtml, 12);

    } catch (err) {
        document.getElementById(loadingId).outerHTML = `<div class="msg-block"><div class="chat-bubble-bot text-danger">Network error: ${err}</div></div>`;
    }
}