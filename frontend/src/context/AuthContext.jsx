import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(() => {
        try {
            const stored = localStorage.getItem('cv_user');
            return stored ? JSON.parse(stored) : null;
        } catch {
            return null;
        }
    });
    const [loading, setLoading] = useState(false);

    const login = useCallback(async (username, password) => {
        setLoading(true);
        try {
            const { data } = await authApi.login({ username, password });
            localStorage.setItem('cv_token', data.access_token);
            const userData = {
                id: data.user_id,
                username: data.username,
                role: data.role,
                full_name: data.full_name,
            };
            localStorage.setItem('cv_user', JSON.stringify(userData));
            setUser(userData);
            return { success: true };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Login failed.';
            return { success: false, error: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            await authApi.logout();
        } catch { }
        localStorage.removeItem('cv_token');
        localStorage.removeItem('cv_user');
        setUser(null);
    }, []);

    const hasRole = useCallback((...roles) => {
        return user && roles.includes(user.role);
    }, [user]);

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
}
