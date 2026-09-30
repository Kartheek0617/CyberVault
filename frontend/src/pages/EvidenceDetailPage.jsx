import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, CheckCircle, AlertTriangle, Send, Download, Clock } from 'lucide-react';
import { evidenceApi, usersApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

function TransferModal({ evidenceId, onClose, onTransferred }) {
    const [users, setUsers] = useState([]);
    const [toUserId, setToUserId] = useState('');
    const [reason, setReason] = useState('');
    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        usersApi.list().then(r => setUsers(r.data.users || [])).catch(() => { });
    }, []);

    const handleTransfer = async () => {
        if (!toUserId || !reason) { toast.error('Select recipient and provide reason'); return; }
        setLoading(true);
        try {
            await evidenceApi.transfer(evidenceId, { to_user_id: toUserId, reason, notes: notes || null });
            toast.success('Evidence transferred successfully');
            onTransferred();
            onClose();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Transfer failed');
        } finally { setLoading(false); }
    };

    return (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
            <div className="modal slide-up">
                <div className="modal-header">
                    <div className="modal-title">🔄 Transfer Evidence</div>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>
                <div className="form-group">
                    <label className="form-label">Transfer To</label>
                    <select className="form-select" value={toUserId} onChange={e => setToUserId(e.target.value)}>
                        <option value="">-- Select recipient --</option>
                        {users.map(u => <option key={u.id} value={u.id}>{u.full_name} ({u.role})</option>)}
                    </select>
                </div>
                <div className="form-group">
                    <label className="form-label">Reason *</label>
                    <input className="form-input" value={reason} onChange={e => setReason(e.target.value)} placeholder="Reason for transfer..." />
                </div>
                <div className="form-group">
                    <label className="form-label">Additional Notes</label>
                    <textarea className="form-textarea" value={notes} onChange={e => setNotes(e.target.value)} style={{ minHeight: '70px' }} />
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleTransfer} disabled={loading} id="confirm-transfer-btn">
                        {loading ? <div className="spinner" /> : <><Send size={14} /> Transfer Custody</>}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default function EvidenceDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user, hasRole } = useAuth();
    const [evidence, setEvidence] = useState(null);
    const [custody, setCustody] = useState([]);
    const [loading, setLoading] = useState(true);
    const [verifying, setVerifying] = useState(false);
    const [verifyResult, setVerifyResult] = useState(null);
    const [showTransfer, setShowTransfer] = useState(false);
    const [receiving, setReceiving] = useState(false);

    const loadEvidence = async () => {
        try {
            const [evRes, custRes] = await Promise.all([
                evidenceApi.get(id),
                evidenceApi.getCustody(id),
            ]);
            setEvidence(evRes.data);
            setCustody(custRes.data.events || []);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Not found or access denied');
            navigate(-1);
        } finally { setLoading(false); }
    };

    useEffect(() => { loadEvidence(); }, [id]);

    const handleVerify = async () => {
        setVerifying(true);
        setVerifyResult(null);
        try {
            const { data } = await evidenceApi.verify(id);
            setVerifyResult(data);
            loadEvidence();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Verification failed');
        } finally { setVerifying(false); }
    };

    const handleReceive = async () => {
        setReceiving(true);
        try {
            await evidenceApi.receive(id);
            toast.success('Evidence receipt confirmed');
            loadEvidence();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to confirm receipt');
        } finally { setReceiving(false); }
    };

    if (loading) return <div className="loading-overlay"><div className="loading-spinner-big" /></div>;
    if (!evidence) return null;

    const isCurrentCustodian = evidence.current_custodian_id === user?.id;
    const custodyActionColors = {
        UPLOADED: 'var(--color-primary)',
        VERIFIED: 'var(--color-success)',
        TRANSFERRED: 'var(--color-warning)',
        RECEIVED: 'var(--color-cyan)',
        VIEWED: 'var(--color-text-muted)',
        INTEGRITY_CHECK: 'var(--color-success)',
        default: 'var(--color-text-muted)',
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)}><ArrowLeft size={16} /> Back</button>
                    <div>
                        <div className="page-title">
                            <span className="mono" style={{ color: 'var(--color-cyan)' }}>{evidence.evidence_number}</span>
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>{evidence.original_filename}</div>
                    </div>
                </div>
                <div className="page-actions">
                    {isCurrentCustodian && evidence.status === 'TRANSFERRED' && (
                        <button className="btn btn-success" onClick={handleReceive} disabled={receiving} id="receive-evidence-btn">
                            {receiving ? <div className="spinner" /> : <><CheckCircle size={16} /> Confirm Receipt</>}
                        </button>
                    )}
                    {(hasRole('ADMIN', 'INVESTIGATOR', 'EVIDENCE_CUSTODIAN')) && evidence.status !== 'TRANSFERRED' && (
                        <button className="btn btn-secondary" onClick={() => setShowTransfer(true)} id="transfer-btn">
                            <Send size={16} /> Transfer
                        </button>
                    )}
                    <button className="btn btn-primary" onClick={handleVerify} disabled={verifying} id="verify-integrity-btn">
                        {verifying ? <><div className="spinner" /> Verifying...</> : <><Shield size={16} /> Verify Integrity</>}
                    </button>
                </div>
            </div>

            {/* Integrity verification result */}
            {verifyResult && (
                <div className={`integrity-result ${verifyResult.match ? 'verified' : 'failed'} mb-6 slide-up`}>
                    <div className="integrity-result-icon">{verifyResult.match ? '✅' : '🚨'}</div>
                    <div className="integrity-result-status">{verifyResult.status}</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', textAlign: 'left', marginTop: 'var(--space-4)' }}>
                        <div>
                            <div className="form-label">Stored Hash (Original)</div>
                            <div className="hash-display">{verifyResult.stored_hash}</div>
                        </div>
                        <div>
                            <div className="form-label">Computed Hash (Verification)</div>
                            <div className="hash-display" style={{ color: verifyResult.match ? 'var(--color-success)' : 'var(--color-danger)' }}>
                                {verifyResult.computed_hash}
                            </div>
                        </div>
                    </div>
                    <div style={{ marginTop: 'var(--space-3)', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                        Verified by {verifyResult.verified_by} at {format(new Date(verifyResult.verified_at), 'PPpp')}
                    </div>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
                {/* Evidence Metadata */}
                <div>
                    <div className="card mb-6">
                        <div className="card-title mb-4">Evidence Metadata</div>
                        <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
                            {[
                                { label: 'Original Filename', value: evidence.original_filename },
                                { label: 'MIME Type', value: evidence.mime_type },
                                { label: 'File Size', value: `${(evidence.file_size_bytes / 1024).toFixed(2)} KB` },
                                { label: 'Uploaded By', value: evidence.uploaded_by?.full_name || '—' },
                                { label: 'Current Custodian', value: evidence.current_custodian?.full_name || '—' },
                                { label: 'Upload Date', value: evidence.created_at ? format(new Date(evidence.created_at), 'PPpp') : '—' },
                            ].map(item => (
                                <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: 'var(--space-2) 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{item.label}</span>
                                    <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Security Status Panel */}
                    <div className="card">
                        <div className="card-title mb-4">Security Status</div>
                        <div className="security-indicator">
                            <div className="security-item">
                                <span className="security-item-label">Integrity</span>
                                <span className={`security-item-value ${evidence.integrity_status === 'VERIFIED' ? 'verified' : evidence.integrity_status === 'FAILED' ? 'danger' : 'warning'}`}>
                                    {evidence.integrity_status === 'VERIFIED' ? '✓' : evidence.integrity_status === 'FAILED' ? '⚠' : '○'} {evidence.integrity_status}
                                </span>
                            </div>
                            <div className="security-item">
                                <span className="security-item-label">Encryption</span>
                                <span className="security-item-value verified">✓ {evidence.encryption_algorithm}</span>
                            </div>
                            <div className="security-item">
                                <span className="security-item-label">Custody Chain</span>
                                <span className="security-item-value verified">✓ {custody.length} Events</span>
                            </div>
                            <div className="security-item">
                                <span className="security-item-label">Status</span>
                                <span className="security-item-value verified">● {evidence.status}</span>
                            </div>
                        </div>

                        <div className="mt-4">
                            <div className="form-label">SHA-256 Hash (Original File)</div>
                            <div className="hash-display">{evidence.sha256_hash}</div>
                        </div>
                    </div>
                </div>

                {/* Chain of Custody */}
                <div>
                    <div className="card">
                        <div className="card-title mb-4">
                            <Clock size={18} /> Chain of Custody ({custody.length} events)
                        </div>
                        {custody.length === 0 ? (
                            <div className="empty-state">No custody events</div>
                        ) : (
                            <div className="custody-timeline">
                                {custody.map((event, idx) => (
                                    <div key={event.id} className="custody-event">
                                        <div className="custody-event-header">
                                            <span className="custody-event-action" style={{ color: custodyActionColors[event.action] || custodyActionColors.default }}>
                                                {event.action.replace(/_/g, ' ')}
                                            </span>
                                            <span className="custody-event-time">
                                                {event.timestamp ? format(new Date(event.timestamp), 'MMM d, HH:mm') : '—'}
                                            </span>
                                        </div>
                                        <div className="custody-event-actor">
                                            👤 {event.actor?.full_name || '—'}
                                            {event.new_custodian && event.action === 'TRANSFERRED' && (
                                                <> → {event.new_custodian?.full_name || '—'}</>
                                            )}
                                        </div>
                                        {event.reason && <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>{event.reason}</div>}
                                        <div className="custody-event-hash" title={`Hash: ${event.event_hash}`}>
                                            🔗 {event.event_hash?.slice(0, 32)}…
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {showTransfer && (
                <TransferModal
                    evidenceId={id}
                    onClose={() => setShowTransfer(false)}
                    onTransferred={loadEvidence}
                />
            )}
        </div>
    );
}
