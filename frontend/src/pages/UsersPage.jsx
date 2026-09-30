import { useState, useEffect } from 'react';
import { Users, Plus, Shield } from 'lucide-react';
import { usersApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

const ROLES = ['ADMIN', 'INVESTIGATOR', 'EVIDENCE_CUSTODIAN', 'AUDITOR', 'VIEWER'];

function CreateUserModal({ onClose, onCreated }) {
    const [form, setForm] = useState({
        username: '', full_name: '', email: '', password: '',
        role: 'INVESTIGATOR', badge_number: '', department: '',
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.username || !form.email || !form.password) {
            toast.error('Username, email, and password are required');
            return;
        }
        setLoading(true);
        try {
            const { data } = await usersApi.create(form);
            toast.success(`User ${data.username} created`);
            onCreated(data);
            onClose();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to create user');
        } finally { setLoading(false); }
    };

    return (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
            <div className="modal slide-up" style={{ maxWidth: '600px' }}>
                <div className="modal-header">
                    <div className="modal-title">👤 Create New User</div>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                        <div className="form-group">
                            <label className="form-label">Username *</label>
                            <input className="form-input" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Full Name</label>
                            <input className="form-input" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Email *</label>
                            <input className="form-input" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password *</label>
                            <input className="form-input" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="Min 12 chars" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Role</label>
                            <select className="form-select" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
                                {ROLES.map(r => <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Badge Number</label>
                            <input className="form-input" value={form.badge_number} onChange={e => setForm({ ...form, badge_number: e.target.value })} placeholder="e.g. INV-042" />
                        </div>
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label className="form-label">Department</label>
                            <input className="form-input" value={form.department} onChange={e => setForm({ ...form, department: e.target.value })} />
                        </div>
                    </div>
                    <div className="alert alert-info mt-4">
                        <Shield size={14} />
                        <span style={{ fontSize: '0.8rem' }}>Password will be hashed with Argon2id (memory: 64MB, iterations: 3, parallelism: 2)</span>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? <div className="spinner" /> : 'Create User'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function UsersPage() {
    const { hasRole } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);

    const loadUsers = async () => {
        try {
            const { data } = await usersApi.list();
            setUsers(data.users || []);
        } catch { setUsers([]); } finally { setLoading(false); }
    };

    useEffect(() => { loadUsers(); }, []);

    const roleColor = (r) => ({
        ADMIN: 'badge-danger', INVESTIGATOR: 'badge-primary',
        EVIDENCE_CUSTODIAN: 'badge-cyan', AUDITOR: 'badge-info', VIEWER: 'badge-gray'
    })[r] || 'badge-gray';

    return (
        <div className="fade-in">
            <div className="page-header">
                <div>
                    <div className="page-title"><Users size={24} style={{ color: 'var(--color-primary)' }} /> User Management</div>
                    <div className="page-subtitle">RBAC — Role-Based Access Control</div>
                </div>
                {hasRole('ADMIN') && (
                    <div className="page-actions">
                        <button className="btn btn-primary" onClick={() => setShowCreate(true)} id="create-user-btn">
                            <Plus size={16} /> New User
                        </button>
                    </div>
                )}
            </div>

            {/* RBAC Explanation */}
            <div className="card mb-6" style={{ padding: 'var(--space-5)' }}>
                <div className="card-title mb-4">Access Control Matrix</div>
                <div style={{ overflow: 'auto' }}>
                    <table>
                        <thead>
                            <tr>
                                <th>Role</th>
                                <th>View Cases</th>
                                <th>Create Cases</th>
                                <th>Upload Evidence</th>
                                <th>Transfer Evidence</th>
                                <th>Generate Reports</th>
                                <th>View Audit Log</th>
                                <th>Manage Users</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[
                                { role: 'ADMIN', caps: [true, true, true, true, true, true, true] },
                                { role: 'INVESTIGATOR', caps: [true, true, true, true, true, false, false] },
                                { role: 'EVIDENCE_CUSTODIAN', caps: ['own', false, false, true, false, false, false] },
                                { role: 'AUDITOR', caps: [true, false, false, false, false, true, true] },
                                { role: 'VIEWER', caps: ['own', false, false, false, false, false, false] },
                            ].map(item => (
                                <tr key={item.role}>
                                    <td><span className={`badge ${roleColor(item.role)}`}>{item.role.replace(/_/g, ' ')}</span></td>
                                    {item.caps.map((c, i) => (
                                        <td key={i} style={{ textAlign: 'center' }}>
                                            {c === true ? '✅' : c === false ? '❌' : '🔒 Own'}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="card">
                {loading ? (
                    <div className="loading-overlay"><div className="loading-spinner-big" /></div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>User</th><th>Role</th><th>Badge</th><th>Department</th>
                                    <th>Status</th><th>Last Login</th><th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(u => (
                                    <tr key={u.id}>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                                                <div className="user-avatar" style={{ width: 28, height: 28, fontSize: '0.7rem' }}>
                                                    {u.full_name?.charAt(0) || u.username?.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="td-primary">{u.full_name || u.username}</div>
                                                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>@{u.username}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td><span className={`badge ${roleColor(u.role)}`}>{u.role?.replace(/_/g, ' ')}</span></td>
                                        <td className="td-mono" style={{ fontSize: '0.8rem' }}>{u.badge_number || '—'}</td>
                                        <td style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{u.department || '—'}</td>
                                        <td>
                                            <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'} badge-dot`}>
                                                {u.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                            {u.last_login ? format(new Date(u.last_login), 'MMM d, HH:mm') : 'Never'}
                                        </td>
                                        <td style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                            {u.created_at ? format(new Date(u.created_at), 'MMM d, yyyy') : '—'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {showCreate && (
                <CreateUserModal
                    onClose={() => setShowCreate(false)}
                    onCreated={u => { setUsers(prev => [u, ...prev]); }}
                />
            )}
        </div>
    );
}
