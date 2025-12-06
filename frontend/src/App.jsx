import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Navbar from './components/Navbar';

const PrivateRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    return user ? children : <Navigate to="/login" />;
};

const Layout = ({ children }) => {
    return (
        <div className="app-layout">
            <Navbar />
            <main className="container" style={{ marginTop: '2rem' }}>
                {children}
            </main>
        </div>
    );
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/" element={
                        <PrivateRoute>
                            <Layout>
                                <Dashboard />
                            </Layout>
                        </PrivateRoute>
                    } />
                    <Route path="/chat" element={
                        <PrivateRoute>
                            <Layout>
                                <Chat />
                            </Layout>
                        </PrivateRoute>
                    } />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
