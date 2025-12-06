import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await register(username, password, fullName);
            navigate('/login');
        } catch (err) {
            console.error('Registration error:', err);
            const errorMessage =
                err?.response?.data?.detail ||
                err?.message ||
                'Registration failed. Please try again.';
            setError(errorMessage);
        }
    };

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh'
        }}>
            <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '400px' }}>
                <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Create Account</h2>

                {error && (
                    <div style={{ color: 'var(--error)', marginBottom: '1rem', textAlign: 'center' }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label className="input-label">Full Name</label>
                        <input
                            type="text"
                            className="input-field"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Username</label>
                        <input
                            type="text"
                            className="input-field"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Password</label>
                        <input
                        type="password"
                        className="input-field"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        maxLength={72}  // <-- FIXED
                        required
                    />

                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                        Register
                    </button>
                </form>

                <p style={{ marginTop: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Already have an account? <Link to="/login">Login</Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
