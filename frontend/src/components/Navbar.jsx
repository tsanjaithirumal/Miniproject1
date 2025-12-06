import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, FileText, MessageSquare, Shield } from 'lucide-react';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav style={{
            backgroundColor: 'var(--bg-card)',
            borderBottom: '1px solid var(--border)',
            padding: '1rem 0'
        }}>
            <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-main)' }}>
                    <Shield className="w-6 h-6 text-blue-500" />
                    <span>MediVault AI</span>
                </Link>

                {user ? (
                    <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                            <FileText size={18} />
                            <span>Documents</span>
                        </Link>
                        <Link to="/chat" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                            <MessageSquare size={18} />
                            <span>AI Chat</span>
                        </Link>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: '1rem' }}>
                            <span style={{ fontSize: '0.875rem' }}>{user.username}</span>
                            <button onClick={handleLogout} className="btn btn-outline" style={{ padding: '0.5rem', border: 'none' }}>
                                <LogOut size={18} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <Link to="/login" className="btn btn-outline">Login</Link>
                        <Link to="/register" className="btn btn-primary">Register</Link>
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
