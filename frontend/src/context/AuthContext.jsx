import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkUser = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const response = await api.get('/auth/me');
                    setUser(response.data);
                } catch (error) {
                    localStorage.removeItem('token');
                }
            }
            setLoading(false);
        };
        checkUser();
    }, []);

    const login = async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await api.post('/auth/login', formData);
        localStorage.setItem('token', response.data.access_token);

        const userResponse = await api.get('/auth/me');
        setUser(userResponse.data);
    };

    const register = async (username, password, fullName) => {
        return await api.post('/auth/register', {
            username,
            password,
            full_name: fullName
        });
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
