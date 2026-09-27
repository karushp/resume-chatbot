const HISTORY_LIMIT = 4;
const REQUEST_TIMEOUT_MS = 30000;
const API_URL =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5001/ask"
        : "https://resume-chatbot-162o.onrender.com/ask";

const chatHistory = [];
let isSending = false;

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

/** Light markdown → safe HTML (escape first, then bold + line breaks). */
function formatBotHtml(text) {
    return escapeHtml(text)
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/^[-*] (.+)$/gm, "• $1")
        .replace(/\n/g, "<br>");
}

function createMessageRow(role, contentHtmlOrText, { isHtml = false } = {}) {
    const row = document.createElement("div");
    row.className = `chat-message ${role}`;

    if (role === "user") {
        const avatar = document.createElement("div");
        avatar.className = "user-avatar";
        avatar.textContent = "U";
        row.appendChild(avatar);
    } else {
        const avatar = document.createElement("img");
        avatar.src = "frontend/photo.jpeg";
        avatar.alt = "Bot";
        avatar.className = "message-avatar";
        row.appendChild(avatar);
    }

    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${role}`;
    if (isHtml) {
        bubble.innerHTML = contentHtmlOrText;
    } else {
        bubble.textContent = contentHtmlOrText;
    }
    row.appendChild(bubble);
    return row;
}

function createLoadingRow() {
    const row = document.createElement("div");
    row.id = "loading-" + (crypto.randomUUID?.() ?? String(Date.now()));
    row.className = "loading-container";
    row.setAttribute("aria-live", "polite");
    row.setAttribute("aria-busy", "true");

    const avatar = document.createElement("img");
    avatar.src = "frontend/photo.jpeg";
    avatar.alt = "";
    avatar.className = "loading-avatar";

    const bubble = document.createElement("div");
    bubble.className = "loading-bubble";

    const spinner = document.createElement("div");
    spinner.className = "loading-spinner";
    spinner.setAttribute("aria-hidden", "true");

    const label = document.createElement("span");
    label.className = "loading-text";
    label.textContent = "Bot is thinking...";

    bubble.appendChild(spinner);
    bubble.appendChild(label);
    row.appendChild(avatar);
    row.appendChild(bubble);
    return row;
}

function setSendingState(sending, sendButton, input) {
    isSending = sending;
    sendButton.disabled = sending;
    input.disabled = sending;
    sendButton.innerHTML = sending
        ? '<span class="send-icon" aria-hidden="true">\u22EF</span>'
        : '<span class="send-icon" aria-hidden="true">\u2191</span>';
}

async function sendMessage() {
    if (isSending) return;

    const input = document.getElementById("userInput");
    const chat = document.getElementById("chat");
    const sendButton = document.querySelector(".send-btn");
    const status = document.getElementById("chat-status");

    const userMessage = input.value.trim();
    if (!userMessage) return;

    input.value = "";
    setSendingState(true, sendButton, input);

    chat.appendChild(createMessageRow("user", userMessage));
    if (status) status.textContent = "Bot is thinking…";

    const loadingRow = createLoadingRow();
    chat.appendChild(loadingRow);
    chat.scrollTop = chat.scrollHeight;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: userMessage,
                history: chatHistory.slice(-HISTORY_LIMIT)
            }),
            signal: controller.signal
        });

        let data = null;
        try {
            data = await response.json();
        } catch (_) {
            throw new Error("Invalid response from server");
        }

        if (!response.ok) {
            const detail = typeof data?.error === "string" ? data.error : `Request failed (${response.status})`;
            throw new Error(detail);
        }

        if (typeof data?.answer !== "string" || !data.answer.trim()) {
            throw new Error("Empty or invalid answer from server");
        }

        const answer = data.answer.trim();
        loadingRow.remove();
        chat.appendChild(createMessageRow("bot", formatBotHtml(answer), { isHtml: true }));

        chatHistory.push({ role: "user", content: userMessage });
        chatHistory.push({ role: "assistant", content: answer });
        if (chatHistory.length > HISTORY_LIMIT) {
            chatHistory.splice(0, chatHistory.length - HISTORY_LIMIT);
        }

        if (status) status.textContent = "";
    } catch (error) {
        loadingRow.remove();
        const message =
            error.name === "AbortError"
                ? "Request timed out. Please try again."
                : (error.message || "Something went wrong");
        chat.appendChild(
            createMessageRow("bot", message)
        );
        if (status) status.textContent = "Error sending message.";
    } finally {
        clearTimeout(timeoutId);
        setSendingState(false, sendButton, input);
        chat.scrollTop = chat.scrollHeight;
        input.focus();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    if (form) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            sendMessage();
        });
    }
});
