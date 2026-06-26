import React, { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      id: Date.now(),
      sender: "bot",
      text: "👋 Welcome to AI Law Advisor! Ask your legal question.",
      timestamp: new Date().toISOString(),
      editing: false,
      _draft: null
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("english");
  const chatBoxRef = useRef(null);

  // auto-scroll on new messages
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  // copy to clipboard
  const copyMessage = (id) => {
    const msg = messages.find(m => m.id === id);
    if (!msg) return;
    navigator.clipboard.writeText(msg._draft ?? msg.text)
      .then(() => {
        // small non-blocking feedback
        const el = document.createElement("div");
        el.textContent = "Copied ✅";
        el.className = "ala-copy-toast";
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 1200);
      })
      .catch(() => alert("Copy failed"));
  };

  // start editing user message
  const startEdit = (id) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, editing: true, _draft: m.text } : m));
  };

  const handleEditTextChange = (id, newText) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, _draft: newText } : m));
  };

  const saveEdit = (id) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, text: (m._draft ?? m.text), editing: false, _draft: undefined } : m));
  };

  const cancelEdit = (id) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, editing: false, _draft: undefined } : m));
  };

  const sendMessage = async () => {
    if (input.trim() === "") return;

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: input,
      timestamp: new Date().toISOString(),
      editing: false,
      _draft: null
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text, language })
      });
      if (!resp.ok) throw new Error("Network not ok");
      const data = await resp.json();
      setMessages(prev => [...prev, { id: Date.now()+1, sender: "bot", text: data.answer, timestamp: new Date().toISOString(), editing: false }]);
    } catch (err) {
      setMessages(prev => [...prev, { id: Date.now()+2, sender: "bot", text: "Server error — please check backend.", timestamp: new Date().toISOString(), editing: false }]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ala-container container">
      <div className="ala-header header">
        <h1>⚖️ AI Law Advisor</h1>
        <p>Get quick legal info — English / हिंदी / मराठी</p>
        <div style={{ marginTop: 10 }}>
          <select value={language} onChange={(e) => setLanguage(e.target.value)} className="ala-language-select">
            <option value="english">English</option>
            <option value="hindi">हिंदी</option>
            <option value="marathi">मराठी</option>
          </select>
        </div>
      </div>

      <div className="ala-chat-box chat-box" ref={chatBoxRef}>
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}-message`}>
            <div className="message-text">
              {msg.editing ? (
                <div className="ala-edit-row edit-row">
                  <input
                    value={msg._draft ?? msg.text}
                    onChange={(e) => handleEditTextChange(msg.id, e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") saveEdit(msg.id);
                      if (e.key === "Escape") cancelEdit(msg.id);
                    }}
                    aria-label="Edit message"
                  />
                  <button className="ala-btn ala-save" onClick={() => saveEdit(msg.id)}>Save</button>
                  <button className="ala-btn ala-cancel" onClick={() => cancelEdit(msg.id)}>Cancel</button>
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ flex: 1, whiteSpace: 'pre-wrap' }}>{msg.text}</div>
                  <div className="ala-msg-actions msg-actions">
                    <button onClick={() => copyMessage(msg.id)} title="Copy">📋</button>
                    {msg.sender === 'user' && <button onClick={() => startEdit(msg.id)} title="Edit">✏️</button>}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message bot-message">
            <div className="message-text">
              <div className="typing-indicator">
                <div className="loading"></div>
                <div className="loading"></div>
                <div className="loading"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="ala-input-area input-area">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === "Enter" ? sendMessage() : null}
          placeholder="Ask your legal question..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  );
}

export default App;
