import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [sessionId, setSessionId] = useState(uuidv4());
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hello! I am your premium product assistant. How can I help you find the perfect product today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [pastSessions, setPastSessions] = useState([]);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  const fetchSessions = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/chat/sessions');
      const data = await res.json();
      setPastSessions(data.sessions || []);
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    // Initialize WebSocket connection
    wsRef.current = new WebSocket('ws://localhost:8000/api/chat/stream');
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.error) {
        console.error(data.error);
        setIsTyping(false);
        return;
      }
      
      if (data.done) {
        setIsTyping(false);
        return;
      }
      
      if (data.chunk) {
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMsg = newMessages[newMessages.length - 1];
          if (lastMsg.role === 'bot' && lastMsg.isStreaming) {
            newMessages[newMessages.length - 1] = {
              ...lastMsg,
              content: lastMsg.content + data.chunk
            };
          } else {
            newMessages.push({ role: 'bot', content: data.chunk, isStreaming: true });
          }
          return newMessages;
        });
      }
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsTyping(false);
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket connection closed.");
      setIsTyping(false);
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleSend = () => {
    if (!input.trim() || !wsRef.current) return;
    
    const userMessage = input;
    setInput('');
    setMessages(prev => {
      const msgs = [...prev];
      if (msgs.length > 0 && msgs[msgs.length - 1].isStreaming) {
        msgs[msgs.length - 1].isStreaming = false;
      }
      return [...msgs, { role: 'user', content: userMessage }];
    });
    setIsTyping(true);

    if (wsRef.current.readyState !== WebSocket.OPEN) {
      console.error("WebSocket is not open. Try refreshing or clicking New Chat.");
      setMessages(prev => [...prev, { role: 'bot', content: "Connection lost. Please refresh the page." }]);
      return;
    }

    try {
      wsRef.current.send(JSON.stringify({ session_id: sessionId, message: userMessage }));
      
      // Update past sessions list after first message
      const sessionExists = pastSessions.find(s => s.id === sessionId);
      if (!sessionExists) {
        setTimeout(fetchSessions, 1000);
      }
    } catch (e) {
      console.error("Send error:", e);
      setIsTyping(false);
    }
  };

  const loadSession = async (id) => {
    setSessionId(id);
    try {
      const res = await fetch(`http://localhost:8000/api/chat/sessions/${id}`);
      const data = await res.json();
      if (data.history && data.history.length > 0) {
        setMessages(data.history);
      } else {
        setMessages([{ role: 'bot', content: 'Hello! I am your premium product assistant.' }]);
      }
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.CLOSED) {
        wsRef.current = new WebSocket('ws://localhost:8000/api/chat/stream');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const startNewChat = () => {
    setSessionId(uuidv4());
    setMessages([{ role: 'bot', content: 'Hello! I am your premium product assistant. How can I help you find the perfect product today?' }]);
    if (wsRef.current && wsRef.current.readyState === WebSocket.CLOSED) {
      wsRef.current = new WebSocket('ws://localhost:8000/api/chat/stream');
    }
  };

  const handleDeleteSession = async (id, e) => {
    e.stopPropagation();
    try {
      await fetch(`http://localhost:8000/api/chat/sessions/${id}`, { method: 'DELETE' });
      setPastSessions(prev => prev.filter(s => s.id !== id));
      if (sessionId === id) {
        startNewChat();
      }
    } catch (err) {
      console.error("Failed to delete session", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar glass">
        <button className="new-chat-btn" onClick={startNewChat}>+ New Chat</button>
        <div className="history-list">
          <div 
            className={`history-item ${!pastSessions.find(s => s.id === sessionId) ? 'active' : ''}`}
            onClick={startNewChat}
          >
            Current Conversation
          </div>
          {pastSessions.map(session => (
            <div 
              key={session.id} 
              className={`history-item session-item ${sessionId === session.id ? 'active' : ''}`}
              onClick={() => loadSession(session.id)}
            >
              <span className="session-title">
                {session.title.length > 25 ? session.title.slice(0, 25) + '...' : session.title}
              </span>
              <button 
                className="delete-session-btn" 
                onClick={(e) => handleDeleteSession(session.id, e)}
                title="Delete Chat"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </aside>
      <div className="main-content">
        <header className="glass header">
          <h1>Product Assistant</h1>
        </header>
        <main className="chat-interface">
          <div className="messages-area glass">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}-message`}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            ))}
            {isTyping && (
              <div className="message bot-message">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="input-area glass">
            <input 
              type="text" 
              placeholder="Ask about our products..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button className="send-btn" onClick={handleSend}>
              Send
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
