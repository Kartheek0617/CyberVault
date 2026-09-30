import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Folder, FileText, Shield, AlertTriangle,
    CheckCircle, Clock, Users, Activity, ArrowRight
} from 'lucide-react';
import { dashboardApi, casesApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { formatDistanceToNow, format } from 'date-fns';

function StatCard({ icon: Icon, value, label, accentColor, accentGlow, onClick }) {
    return (
        <div
            className="stat-card"
            style={{ '--accent-color': accentColor, '--accent-glow': accentGlow, cursor: onClick ? 'pointer' : 'default' }}
            onClick={onClick}
        >
            <div className="stat-card-icon">
                <Icon size={22} />
            </div>
            <div className="stat-card-value">{value ?? '—'}</div>
            <div className="stat-card-label">{label}</div>
        </div>
    );
}

function ActionBadge({ action }) {
    const colors = {
        USER_LOGIN: 'badge-success',
        USER_LOGIN_FAILED: 'badge-danger',
        CASE_CREATED: 'badge-primary',
        EVIDENCE_UPLOADED: 'badge-cyan',
        EVIDENCE_VERIFIED: 'badge-success',
        EVIDENCE_TRANSFERRED: 'badge-warning',
        REPORT_GENERATED: 'badge-info',
        ACCESS_DENIED: 'badge-danger',
        SIGNATURE_VERIFIED: 'badge-success',
        default: 'badge-gray',
    };
    return (
        <span className={`badge ${colors[action] || colors.default} badge-dot`}>
            {action.replace(/_/g, ' ')}
        </span>
    );
}

export default function Dashboard() {
    const { user, hasRole } = useAuth();
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [activity, setActivity] = useState([]);
    const [securityEvents, setSecurityEvents] = useState([]);
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [statsRes, activityRes, casesRes, eventsRes] = await Promise.all([
                    dashboardApi.stats(),
                    dashboardApi.recentActivity(),
                    casesApi.list(),
                    dashboardApi.securityEvents(),
                ]);
                setStats(statsRes.data);
                setActivity(activityRes.data.activity || []);
                setCases((casesRes.data.cases || []).slice(0, 5));
                setSecurityEvents((eventsRes.data.events || []).slice(0, 5));
            } catch {
                /* use empty state */
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="loading-content">
                    <div className="loading-spinner-big" />
                    <p className="text-muted">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    const priorityBadge = (p) => ({
        CRITICAL: 'badge-danger', HIGH: 'badge-warning', MEDIUM: 'badge-warning', LOW: 'badge-primary'
    })[p] || 'badge-gray';

    const statusBadge = (s) => ({
        ACTIVE: 'badge-success', CLOSED: 'badge-gray', ARCHIVED: 'badge-gray', PENDING: 'badge-warning'
    })[s] || 'badge-gray';

    return (
        <div className="fade-in">
            <div className="page-header">
                <div>
                    <div className="page-title">
                        <Activity size={24} style={{ color: 'var(--color-primary)' }} />
                        Operations Dashboard
                    </div>
                    <div className="page-subtitle">
                        Welcome back, {user?.full_name || user?.username} · {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="stat-cards">
                <StatCard
                    icon={Folder}
                    value={stats?.active_cases}
                    label="Active Cases"
                    accentColor="var(--color-primary)"
                    accentGlow="var(--color-primary-glow)"
                    onClick={() => navigate('/cases')}
                />
                <StatCard
                    icon={CheckCircle}
                    value={stats?.closed_cases}
                    label="Closed Cases"
                    accentColor="var(--color-success)"
                    accentGlow="var(--color-success-glow)"
                />
                <StatCard
                    icon={FileText}
                    value={stats?.total_evidence}
                    label="Total Evidence"
                    accentColor="var(--color-cyan)"
                    accentGlow="var(--color-cyan-glow)"
                />
                <StatCard
                    icon={Clock}
                    value={stats?.pending_transfers}
                    label="Pending Transfers"
                    accentColor="var(--color-warning)"
                    accentGlow="var(--color-warning-glow)"
                />
                <StatCard
                    icon={Shield}
                    value={stats?.verified_evidence}
                    label="Verified Evidence"
                    accentColor="var(--color-success)"
                    accentGlow="var(--color-success-glow)"
                />
                <StatCard
                    icon={AlertTriangle}
                    value={stats?.integrity_alerts}
                    label="Integrity Alerts"
                    accentColor="var(--color-danger)"
                    accentGlow="var(--color-danger-glow)"
                />
                {hasRole('ADMIN') && (
                    <StatCard
                        icon={Users}
                        value={stats?.total_users}
                        label="Total Users"
                        accentColor="var(--color-info)"
                        accentGlow="var(--color-info-glow)"
                        onClick={() => navigate('/users')}
                    />
                )}
                <StatCard
                    icon={AlertTriangle}
                    value={stats?.recent_security_events}
                    label="Security Events (24h)"
                    accentColor="var(--color-danger)"
                    accentGlow="var(--color-danger-glow)"
                    onClick={() => navigate('/security')}
                />
            </div>

            {/* Two-column layout */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
                {/* Recent Cases */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title"><Folder size={18} /> Recent Cases</div>
                        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/cases')}>
                            View All <ArrowRight size={14} />
                        </button>
                    </div>
                    {cases.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📁</div>
                            <div className="empty-state-title">No cases yet</div>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Case</th>
                                        <th>Priority</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {cases.map(c => (
                                        <tr key={c.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/cases/${c.id}`)}>
                                            <td>
                                                <div className="td-primary" style={{ fontSize: '0.8rem' }}>{c.case_number}</div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</div>
                                            </td>
                                            <td><span className={`badge ${priorityBadge(c.priority)}`}>{c.priority}</span></td>
                                            <td><span className={`badge ${statusBadge(c.status)} badge-dot`}>{c.status}</span></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Recent Activity */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title"><Activity size={18} /> Recent Activity</div>
                        {hasRole('ADMIN', 'AUDITOR') && (
                            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/audit-logs')}>
                                View All <ArrowRight size={14} />
                            </button>
                        )}
                    </div>
                    {activity.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📋</div>
                            <div className="empty-state-title">No activity yet</div>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            {activity.slice(0, 8).map(a => (
                                <div key={a.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-2) 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                                    <div>
                                        <ActionBadge action={a.action} />
                                        <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                                            {a.username}
                                        </div>
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', textAlign: 'right' }}>
                                        {formatDistanceToNow(new Date(a.timestamp), { addSuffix: true })}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Security Events */}
            {securityEvents.length > 0 && (
                <div className="card mt-6">
                    <div className="card-header">
                        <div className="card-title">
                            <AlertTriangle size={18} style={{ color: 'var(--color-danger)' }} /> Security Alerts
                        </div>
                        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/security')}>
                            View All <ArrowRight size={14} />
                        </button>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                        {securityEvents.map(e => (
                            <div key={e.id} className="alert alert-danger" style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                <AlertTriangle size={14} />
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 600, fontSize: '0.8rem' }}>{e.event_type.replace(/_/g, ' ')}</div>
                                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>{e.description}</div>
                                </div>
                                <div style={{ fontSize: '0.7rem', opacity: 0.7, whiteSpace: 'nowrap' }}>
                                    {formatDistanceToNow(new Date(e.timestamp), { addSuffix: true })}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
