import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Folder, Plus, Search, Filter } from 'lucide-react';
import { casesApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

const CASE_TYPES = ['CYBERCRIME', 'FRAUD', 'DATA_BREACH', 'MALWARE', 'NETWORK_INTRUSION', 'INSIDER_THREAT', 'OTHER'];
const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

function CreateCaseModal({ onClose, onCreated }) {
    const [form, setForm] = useState({ title: '', description: '', case_type: 'CYBERCRIME', priority: 'MEDIUM' });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.title.trim()) { toast.error('Title is required'); return; }
        setLoading(true);
        try {
            const { data } = await casesApi.create(form);
            toast.success(`Case ${data.case_number} created!`);
            onCreated(data);
            onClose();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to create case');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
            <div className="modal slide-up">
                <div className="modal-header">
                    <div className="modal-title">🗂 Create New Case</div>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Case Title *</label>
                        <input className="form-input" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="e.g. Unauthorized Access Investigation" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Description</label>
                        <textarea className="form-textarea" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Describe the incident..." />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                        <div className="form-group">
                            <label className="form-label">Case Type</label>
                            <select className="form-select" value={form.case_type} onChange={e => setForm({ ...form, case_type: e.target.value })}>
                                {CASE_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Priority</label>
                            <select className="form-select" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })}>
                                {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? <><div className="spinner" /> Creating...</> : 'Create Case'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function CasesPage() {
    const { hasRole } = useAuth();
    const navigate = useNavigate();
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [showCreate, setShowCreate] = useState(false);

    const load = async () => {
        try {
            const { data } = await casesApi.list(statusFilter || undefined);
            setCases(data.cases || []);
        } catch { setCases([]); } finally { setLoading(false); }
    };

    useEffect(() => { load(); }, [statusFilter]);

    const filtered = cases.filter(c =>
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        c.case_number.toLowerCase().includes(search.toLowerCase())
    );

    const priorityBadge = (p) => ({ CRITICAL: 'badge-danger', HIGH: 'badge-warning', MEDIUM: 'badge-warning', LOW: 'badge-primary' })[p] || 'badge-gray';
    const statusBadge = (s) => ({ ACTIVE: 'badge-success', CLOSED: 'badge-gray', ARCHIVED: 'badge-gray', PENDING: 'badge-warning' })[s] || 'badge-gray';

    return (
        <div className="fade-in">
            <div className="page-header">
                <div>
                    <div className="page-title"><Folder size={24} style={{ color: 'var(--color-primary)' }} /> Cases</div>
                    <div className="page-subtitle">Manage investigation cases</div>
                </div>
                {hasRole('ADMIN', 'INVESTIGATOR') && (
                    <div className="page-actions">
                        <button className="btn btn-primary" onClick={() => setShowCreate(true)} id="create-case-btn">
                            <Plus size={16} /> New Case
                        </button>
                    </div>
                )}
            </div>

            <div className="card">
                <div style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-5)' }}>
                    <div style={{ position: 'relative', flex: 1 }}>
                        <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                        <input
                            className="form-input"
                            style={{ paddingLeft: '36px' }}
                            placeholder="Search cases..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                    </div>
                    <select className="form-select" style={{ width: 'auto' }} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
                        <option value="">All Statuses</option>
                        <option value="ACTIVE">Active</option>
                        <option value="CLOSED">Closed</option>
                        <option value="ARCHIVED">Archived</option>
                    </select>
                </div>

                {loading ? (
                    <div className="loading-overlay"><div className="loading-spinner-big" /></div>
                ) : filtered.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">📁</div>
                        <div className="empty-state-title">No cases found</div>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Case Number</th>
                                    <th>Title</th>
                                    <th>Type</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Evidence</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map(c => (
                                    <tr key={c.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/cases/${c.id}`)}>
                                        <td className="td-mono">{c.case_number}</td>
                                        <td>
                                            <div className="td-primary">{c.title}</div>
                                            {c.creator && <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{c.creator.full_name}</div>}
                                        </td>
                                        <td><span className="badge badge-gray">{c.case_type?.replace(/_/g, ' ')}</span></td>
                                        <td><span className={`badge ${priorityBadge(c.priority)}`}>{c.priority}</span></td>
                                        <td><span className={`badge ${statusBadge(c.status)} badge-dot`}>{c.status}</span></td>
                                        <td><span className="badge badge-cyan">{c.evidence_count ?? 0} items</span></td>
                                        <td style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>
                                            {c.created_at ? format(new Date(c.created_at), 'MMM d, yyyy') : '—'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {showCreate && (
                <CreateCaseModal
                    onClose={() => setShowCreate(false)}
                    onCreated={newCase => setCases(prev => [newCase, ...prev])}
                />
            )}
        </div>
    );
}
