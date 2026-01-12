import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_id: null,
          user_id: 'demo-user'
        })
      });

      const data = await response.json();
      const assistantMessage = { 
        role: 'assistant', 
        content: data.response,
        sources: data.sources 
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const exampleQuestions = [
    "Can I build apartments in Melbourne?",
    "What's the minimum lot size for R-1 in Satellite Beach?",
    "What are setback requirements in Indian Harbour Beach?",
    "What uses are allowed in Palm Bay C-1 zones?"
  ];

  return (
    <div className="app">
      <header className="header">
        <h1>🏘️ ZoneWise</h1>
        <p>Brevard County Zoning Intelligence</p>
      </header>

      <main className="main">
        <div className="chat-container">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Ask me about zoning in Brevard County!</h2>
              <p>Covering all 17 municipalities with complete zoning data</p>
              
              <div className="examples">
                <h3>Try asking:</h3>
                {exampleQuestions.map((q, i) => (
                  <button 
                    key={i}
                    className="example-btn"
                    onClick={() => setInput(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <div className="message-content">
                  <strong>{msg.role === 'user' ? 'You' : 'ZoneWise'}:</strong>
                  <p>{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      <small>Sources: {msg.sources.join(', ')}</small>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message assistant">
                <div className="message-content">
                  <strong>ZoneWise:</strong>
                  <p className="loading">Analyzing zoning regulations...</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about zoning in any Brevard municipality..."
            disabled={loading}
          />
          <button 
            onClick={sendMessage} 
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </main>

      <footer className="footer">
        <p>ZoneWise • Covering 17 Brevard County Municipalities • 1,207 Zoning Rules</p>
      </footer>
    </div>
  );
}

export default App;
