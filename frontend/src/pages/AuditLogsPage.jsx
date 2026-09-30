import { useState, useEffect } from 'react';
import { Activity, RefreshCw, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { auditApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

const ACTION_COLORS = {
    USER_LOGIN: 'badge-success',
    USER_LOGIN_FAILED: 'badge-danger',
    ACCESS_DENIED: 'badge-danger',
    CASE_CREATED: 'badge-primary',
    EVIDENCE_UPLOADED: 'badge-cyan',
    EVIDENCE_VERIFIED: 'badge-success',
    EVIDENCE_TAMPERED: 'badge-danger',
    EVIDENCE_TRANSFERRED: 'badge-warning',
    REPORT_GENERATED: 'badge-info',
    SIGNATURE_VERIFIED: 'badge-success',
    AUDIT_VERIFIED: 'badge-success',
    USER_CREATED: 'badge-primary',
};

export default function AuditLogsPage() {
    const { hasRole } = useAuth();
    const [logs, setLogs] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [verifying, setVerifying] = useState(false);
    const [verifyResult, setVerifyResult] = useState(null);
    const [showSecurityOnly, setShowSecurityOnly] = useState(false);
    const [offset, setOffset] = useState(0);
    const LIMIT = 50;

    const loadLogs = async () => {
        setLoading(true);
        try {
            const { data } = await auditApi.list({
                limit: LIMIT,
                offset,
                is_security: showSecurityOnly,
            });
            setLogs(data.audit_logs || []);
            setTotal(data.total || 0);
        } catch { setLogs([]); } finally { setLoading(false); }
    };

    useEffect(() => { loadLogs(); }, [showSecurityOnly, offset]);

    const handleVerifyIntegrity = async () => {
        setVerifying(true);
        setVerifyResult(null);
        try {
            const { data } = await auditApi.verify();
            setVerifyResult(data);
            if (data.is_valid) {
                toast.success('Audit log integrity VERIFIED — no tampering detected!', { duration: 5000 });
            } else {
                toast.error('🚨 TAMPERING DETECTED in audit log!', { duration: 8000 });
            }
            loadLogs();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Verification failed');
        } finally { setVerifying(false); }
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <div>
                    <div className="page-title"><Activity size={24} style={{ color: 'var(--color-primary)' }} /> Audit Log</div>
                    <div className="page-subtitle">Tamper-evident hash-chained audit trail</div>
                </div>
                <div className="page-actions">
                    <button
                        className={`btn btn-secondary btn-sm`}
                        onClick={() => { setShowSecurityOnly(!showSecurityOnly); setOffset(0); }}
                    >
                        {showSecurityOnly ? '👁 Show All' : '⚠ Security Only'}
                    </button>
                    <button className="btn btn-secondary btn-sm" onClick={loadLogs}>
                        <RefreshCw size={14} /> Refresh
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={handleVerifyIntegrity}
                        disabled={verifying}
                        id="verify-audit-btn"
                    >
                        {verifying ? <><div className="spinner" /> Verifying...</> : <><Shield size={16} /> Verify Chain Integrity</>}
                    </button>
                </div>
            </div>

            {/* Verification Result */}
            {verifyResult && (
                <div className={`card mb-6 slide-up`} style={{
                    borderColor: verifyResult.is_valid ? 'var(--color-success)' : 'var(--color-danger)',
                    background: verifyResult.is_valid ? 'var(--color-success-dim)' : 'var(--color-danger-dim)',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                        <div style={{ fontSize: '2.5rem' }}>{verifyResult.is_valid ? '✅' : '🚨'}</div>
                        <div>
                            <div style={{ fontSize: '1.1rem', fontWeight: 800, color: verifyResult.is_valid ? 'var(--color-success)' : 'var(--color-danger)' }}>
                                {verifyResult.message}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
                                {verifyResult.total_entries} entries verified · {verifyResult.checked_at ? format(new Date(verifyResult.checked_at), 'PPpp') : ''}
                            </div>
                            {verifyResult.first_tampering_sequence && (
                                <div className="alert alert-danger mt-4">
                                    ⚠ First tampering detected at sequence #{verifyResult.first_tampering_sequence}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Explanation card */}
            <div className="card mb-6" style={{ padding: 'var(--space-5)' }}>
                <div style={{ display: 'flex', gap: 'var(--space-6)' }}>
                    {[
                        { icon: '🔗', title: 'Hash Chain', desc: 'Each log entry contains a SHA-256 hash of the previous entry, creating a tamper-evident chain' },
                        { icon: '🔢', title: 'Sequence Numbers', desc: 'Monotonically increasing sequence numbers prevent insertion or deletion attacks' },
                        { icon: '🛡', title: 'Immutable', desc: 'Entries are write-only. Any modification to any entry invalidates the entire subsequent chain' },
                    ].map(item => (
                        <div key={item.title} style={{ flex: 1 }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: 'var(--space-2)' }}>{item.icon}</div>
                            <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px' }}>{item.title}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{item.desc}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                        {showSecurityOnly ? '⚠ Security events only · ' : ''}{total} total entries
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                        <button className="btn btn-ghost btn-sm" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - LIMIT))}>← Previous</button>
                        <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', padding: 'var(--space-2)' }}>
                            {offset + 1}–{Math.min(offset + LIMIT, total)}
                        </span>
                        <button className="btn btn-ghost btn-sm" disabled={offset + LIMIT >= total} onClick={() => setOffset(offset + LIMIT)}>Next →</button>
                    </div>
                </div>

                {loading ? (
                    <div className="loading-overlay"><div className="loading-spinner-big" /></div>
                ) : logs.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">📋</div>
                        <div className="empty-state-title">No audit log entries</div>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th><th>Action</th><th>User</th><th>Resource</th>
                                    <th>Timestamp</th><th>Hash</th><th>Security</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.map(log => (
                                    <tr key={log.id} style={{ background: log.is_security_event ? 'rgba(239,68,68,0.04)' : '' }}>
                                        <td className="td-mono" style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>{log.sequence_number}</td>
                                        <td>
                                            <span className={`badge ${ACTION_COLORS[log.action] || 'badge-gray'} badge-dot`}>
                                                {log.action?.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td style={{ fontSize: '0.8rem' }}>{log.user_id ? <>{log.username || log.user_id.slice(0, 8)}</> : 'SYSTEM'}</td>
                                        <td style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                                            {log.resource_type}{log.resource_id && <span className="mono" style={{ fontSize: '0.7rem' }}> · {log.resource_id.slice(0, 8)}</span>}
                                        </td>
                                        <td style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
                                            {log.timestamp ? format(new Date(log.timestamp), 'MMM d, HH:mm:ss') : '—'}
                                        </td>
                                        <td>
                                            <span className="mono" style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }} title={log.entry_hash}>
                                                {log.entry_hash?.slice(0, 12)}…
                                            </span>
                                        </td>
                                        <td>
                                            {log.is_security_event ? (
                                                <span title="Security Event"><AlertTriangle size={14} style={{ color: 'var(--color-danger)' }} /></span>
                                            ) : (
                                                <span title="Normal Event"><CheckCircle size={14} style={{ color: 'var(--color-text-muted)' }} /></span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
