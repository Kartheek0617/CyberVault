import { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
    Shield, LayoutDashboard, Folder, FileText,
    Users, Activity, AlertTriangle, LogOut, ChevronRight, ShieldAlert, GraduationCap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const NAV_ITEMS = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: null },
    { path: '/cases', label: 'Cases', icon: Folder, roles: null },
    { section: 'Security' },
    { path: '/audit-logs', label: 'Audit Log', icon: Activity, roles: ['ADMIN', 'AUDITOR'] },
    { path: '/security', label: 'Security Events', icon: AlertTriangle, roles: ['ADMIN', 'AUDITOR'] },
    { section: 'Admin' },
    { path: '/users', label: 'Users & RBAC', icon: Users, roles: ['ADMIN'] },
    { section: 'Assessment & Viva' },
    { path: '/demo', label: 'Security Demo', icon: ShieldAlert, roles: null },
    { path: '/viva', label: 'Viva Mode', icon: GraduationCap, roles: null },
];

const ROLE_COLORS = {
    ADMIN: { bg: 'rgba(239,68,68,0.15)', color: 'var(--color-danger)' },
    INVESTIGATOR: { bg: 'rgba(59,130,246,0.15)', color: 'var(--color-primary)' },
    EVIDENCE_CUSTODIAN: { bg: 'rgba(6,182,212,0.15)', color: 'var(--color-cyan)' },
    AUDITOR: { bg: 'rgba(139,92,246,0.15)', color: 'var(--color-info)' },
    VIEWER: { bg: 'rgba(71,85,105,0.15)', color: 'var(--color-text-muted)' },
};

export default function AppLayout({ children }) {
    const { user, logout, hasRole } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        toast.success('Logged out securely');
        navigate('/login');
    };

    const roleStyle = ROLE_COLORS[user?.role] || ROLE_COLORS.VIEWER;

    return (
        <div className="app-layout">
            {/* Sidebar */}
            <aside className="sidebar">
                {/* Brand */}
                <div className="sidebar-brand">
                    <div className="brand-logo">
                        <div className="brand-icon">
                            <Shield size={20} color="white" />
                        </div>
                        <div>
                            <div className="brand-name">CYBERVAULT</div>
                        </div>
                    </div>
                    <div className="brand-subtitle">Digital Evidence Management</div>
                </div>

                {/* Navigation */}
                <nav className="sidebar-nav">
                    {NAV_ITEMS.map((item, idx) => {
                        if (item.section) {
                            return <div key={idx} className="nav-section-label">{item.section}</div>;
                        }
                        if (item.roles && !hasRole(...item.roles)) return null;
                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                            >
                                <item.icon size={18} />
                                {item.label}
                            </NavLink>
                        );
                    })}
                </nav>

                {/* Footer */}
                <div className="sidebar-footer">
                    <div className="user-info">
                        <div className="user-avatar">{user?.full_name?.charAt(0) || user?.username?.charAt(0)}</div>
                        <div className="user-details">
                            <div className="user-name">{user?.full_name || user?.username}</div>
                            <div className="user-role" style={{ color: roleStyle.color }}>{user?.role?.replace(/_/g, ' ')}</div>
                        </div>
                        <button
                            onClick={handleLogout}
                            title="Secure Logout"
                            style={{
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: 'var(--color-text-muted)', padding: '4px',
                                borderRadius: 'var(--radius-sm)', transition: 'var(--transition)',
                                display: 'flex', alignItems: 'center',
                            }}
                            onMouseEnter={e => e.currentTarget.style.color = 'var(--color-danger)'}
                            onMouseLeave={e => e.currentTarget.style.color = 'var(--color-text-muted)'}
                        >
                            <LogOut size={16} />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <main className="main-content">
                <div className="topbar">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                        <div style={{
                            width: 8, height: 8, borderRadius: '50%',
                            background: 'var(--color-success)',
                            boxShadow: '0 0 8px var(--color-success)',
                            animation: 'pulseGlow 2s ease-in-out infinite',
                        }} />
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                            System Operational
                        </span>
                        <span style={{ color: 'var(--color-border)', fontSize: '0.75rem' }}>|</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                            🔒 AES-256-GCM · Ed25519 · Argon2id · SHA-256
                        </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                        <div
                            style={{
                                padding: '3px 10px',
                                borderRadius: '999px',
                                background: roleStyle.bg,
                                color: roleStyle.color,
                                fontSize: '0.7rem',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                letterSpacing: '0.06em',
                            }}
                        >
                            {user?.role?.replace(/_/g, ' ')}
                        </div>
                    </div>
                </div>

                <div className="page-content">
                    {children}
                </div>
            </main>
        </div>
    );
}
