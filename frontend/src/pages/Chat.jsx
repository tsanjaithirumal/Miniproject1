import React, { useState, useRef, useEffect } from 'react';
import api from '../api';
import { Send, Bot, User, Loader2 } from 'lucide-react';

const Chat = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your medical AI assistant. Ask me anything about your uploaded medical records.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await api.post('/chat/', { message: userMessage.content });
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error processing your request.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="animate-fade-in" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
            <div className="card" style={{ flex: 1, marginBottom: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {messages.map((msg, index) => (
                    <div key={index} style={{
                        display: 'flex',
                        gap: '1rem',
                        alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%',
                        flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                    }}>
                        <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            background: msg.role === 'user' ? 'var(--primary)' : 'var(--bg-dark)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                        }}>
                            {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                        </div>
                        <div style={{
                            padding: '1rem',
                            borderRadius: '1rem',
                            background: msg.role === 'user' ? 'var(--primary)' : 'rgba(30, 41, 59, 0.5)',
                            border: msg.role === 'user' ? 'none' : '1px solid var(--border)',
                            color: 'var(--text-main)',
                            lineHeight: '1.5'
                        }}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div style={{ display: 'flex', gap: '1rem', maxWidth: '80%' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--bg-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Bot size={18} />
                        </div>
                        <div style={{ padding: '1rem', borderRadius: '1rem', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid var(--border)' }}>
                            <Loader2 className="animate-spin" size={18} />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSubmit} className="card" style={{ padding: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                <input
                    type="text"
                    className="input-field"
                    style={{ marginBottom: 0, border: 'none', background: 'transparent' }}
                    placeholder="Ask about your medical history..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                />
                <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
                    <Send size={18} />
                </button>
            </form>
        </div>
    );
};

export default Chat;
