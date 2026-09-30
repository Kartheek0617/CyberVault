import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Upload, FileText, Users, Clock, Activity, Plus, CheckCircle, PenTool } from 'lucide-react';
import { casesApi, evidenceApi, usersApi, reportsApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

function UploadEvidenceModal({ caseId, onClose, onUploaded }) {
    const [file, setFile] = useState(null);
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [dragOver, setDragOver] = useState(false);

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f) setFile(f);
    };

    const handleUpload = async () => {
        if (!file) { toast.error('Please select a file'); return; }
        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        if (description) formData.append('description', description);
        try {
            const { data } = await evidenceApi.upload(caseId, formData);
            setResult(data);
            onUploaded();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && !loading && onClose()}>
            <div className="modal slide-up" style={{ maxWidth: '640px' }}>
                <div className="modal-header">
                    <div className="modal-title">🔒 Upload Evidence</div>
                    <button className="modal-close" onClick={onClose} disabled={loading}>✕</button>
                </div>

                {result ? (
                    <div className="integrity-result verified fade-in">
                        <div style={{ fontSize: '2.5rem' }}>✅</div>
                        <div className="integrity-result-status">Evidence Uploaded & Encrypted</div>
                        <div style={{ textAlign: 'left', marginTop: 'var(--space-4)' }}>
                            <div style={{ display: 'grid', gap: 'var(--space-3)' }}>
                                <div>
                                    <div className="form-label">Evidence ID</div>
                                    <div className="hash-display">{result.evidence_number}</div>
                                </div>
                                <div>
                                    <div className="form-label">SHA-256 Hash</div>
                                    <div className="hash-display">{result.sha256_hash}</div>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                                    <div>
                                        <div className="form-label">Encryption</div>
                                        <span className="badge badge-success">{result.encryption_algorithm}</span>
                                    </div>
                                    <div>
                                        <div className="form-label">MIME Type</div>
                                        <span className="badge badge-gray">{result.mime_type}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button className="btn btn-primary mt-4" onClick={onClose}>Close</button>
                    </div>
                ) : (
                    <>
                        <div
                            className={`upload-area ${dragOver ? 'drag-over' : ''}`}
                            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => document.getElementById('ev-file-input').click()}
                        >
                            <input
                                id="ev-file-input"
                                type="file"
                                style={{ display: 'none' }}
                                accept=".pdf,.txt,.csv,.jpg,.jpeg,.png,.mp4,.zip,.pcap,.dd,.json,.log,.xml,.doc,.docx"
                                onChange={e => setFile(e.target.files[0])}
                            />
                            {file ? (
                                <div>
                                    <div style={{ fontSize: '2rem', marginBottom: 'var(--space-2)' }}>📄</div>
                                    <div className="upload-text">{file.name}</div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                                        {(file.size / 1024).toFixed(1)} KB — Click to change
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <Upload className="upload-icon" size={40} />
                                    <div className="upload-text">Drop file here or click to select</div>
                                    <div className="upload-hint">PDF, TXT, CSV, JPG, PNG, MP4, ZIP, PCAP — Max 200MB</div>
                                </>
                            )}
                        </div>
                        <div className="form-group mt-4">
                            <label className="form-label">Description (optional)</label>
                            <textarea className="form-textarea" value={description} onChange={e => setDescription(e.target.value)} placeholder="Describe this evidence item..." style={{ minHeight: '70px' }} />
                        </div>
                        <div className="alert alert-info mt-4">
                            <Shield size={14} />
                            <span style={{ fontSize: '0.8rem' }}>File will be validated, SHA-256 hashed, and encrypted with AES-256-GCM before storage. Original filename is stored as metadata only.</span>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={onClose} disabled={loading}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleUpload} disabled={loading || !file} id="upload-submit">
                                {loading ? <><div className="spinner" /> Encrypting...</> : <><Shield size={16} /> Secure Upload</>}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

function AddMemberModal({ caseId, onClose }) {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState('');
    const [roleInCase, setRoleInCase] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        usersApi.list().then(r => setUsers(r.data.users || [])).catch(() => { });
    }, []);

    const handleAdd = async () => {
        if (!selectedUser) { toast.error('Select a user'); return; }
        setLoading(true);
        try {
            await casesApi.addMember(caseId, { user_id: selectedUser, role_in_case: roleInCase || null });
            toast.success('Member added');
            onClose();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to add member');
        } finally { setLoading(false); }
    };

    return (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
            <div className="modal slide-up">
                <div className="modal-header">
                    <div className="modal-title">👤 Add Case Member</div>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>
                <div className="form-group">
                    <label className="form-label">Select User</label>
                    <select className="form-select" value={selectedUser} onChange={e => setSelectedUser(e.target.value)}>
                        <option value="">-- Select --</option>
                        {users.map(u => <option key={u.id} value={u.id}>{u.full_name} ({u.role})</option>)}
                    </select>
                </div>
                <div className="form-group">
                    <label className="form-label">Role in Case</label>
                    <input className="form-input" value={roleInCase} onChange={e => setRoleInCase(e.target.value)} placeholder="e.g. Digital Forensics" />
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleAdd} disabled={loading}>
                        {loading ? <div className="spinner" /> : 'Add Member'}
                    </button>
                </div>
            </div>
        </div>
    );
}

function GenerateReportModal({ caseId, evidenceItems, onClose, onGenerated }) {
    const [title, setTitle] = useState('');
    const [selectedEvidence, setSelectedEvidence] = useState([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleGenerate = async () => {
        if (!title) { toast.error('Please enter a report title'); return; }
        if (selectedEvidence.length === 0) { toast.error('Please select at least one evidence item'); return; }

        setLoading(true);
        try {
            const { data } = await casesApi.createReport(caseId, {
                title,
                evidence_ids: selectedEvidence
            });
            setResult(data);
            toast.success('Report generated and digitally signed');
            onGenerated();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to generate report');
        } finally {
            setLoading(false);
        }
    };

    const toggleEvidence = (id) => {
        setSelectedEvidence(prev =>
            prev.includes(id) ? prev.filter(e => e !== id) : [...prev, id]
        );
    };

    return (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && !loading && onClose()}>
            <div className="modal slide-up" style={{ maxWidth: '640px' }}>
                <div className="modal-header">
                    <div className="modal-title"><PenTool size={20} style={{ display: 'inline', marginRight: '8px' }} /> Generate Signed Report</div>
                    <button className="modal-close" onClick={onClose} disabled={loading}>✕</button>
                </div>

                {result ? (
                    <div className="integrity-result verified fade-in">
                        <div style={{ fontSize: '2.5rem' }}>✅</div>
                        <div className="integrity-result-status">Report Signed with Ed25519</div>
                        <div style={{ textAlign: 'left', marginTop: 'var(--space-4)' }}>
                            <div style={{ display: 'grid', gap: 'var(--space-3)' }}>
                                <div>
                                    <div className="form-label">Report ID</div>
                                    <div className="hash-display">{result.report_number}</div>
                                </div>
                                <div>
                                    <div className="form-label">Report Hash (SHA-256)</div>
                                    <div className="hash-display">{result.report_hash}</div>
                                </div>
                                <div>
                                    <div className="form-label">Digital Signature</div>
                                    <div className="hash-display" style={{
                                        whiteSpace: 'normal',
                                        wordBreak: 'break-all',
                                        fontSize: '0.65rem'
                                    }}>
                                        {result.digital_signature}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button className="btn btn-primary mt-4" onClick={onClose}>Close</button>
                    </div>
                ) : (
                    <>
                        <div className="form-group mt-4">
                            <label className="form-label">Report Title *</label>
                            <input className="form-input" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Initial Forensics Report" />
                        </div>

                        <div className="form-group mt-4" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                            <label className="form-label">Select Evidence Items *</label>
                            {evidenceItems.length === 0 ? (
                                <div className="text-muted text-sm pb-2">No active evidence in this case.</div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    {evidenceItems.map(ev => (
                                        <label key={ev.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', padding: '8px', background: 'var(--color-bg-elevated)', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
                                            <input
                                                type="checkbox"
                                                checked={selectedEvidence.includes(ev.id)}
                                                onChange={() => toggleEvidence(ev.id)}
                                            />
                                            <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--color-cyan)' }}>{ev.evidence_number}</span>
                                            <span style={{ fontSize: '0.85rem' }}>{ev.original_filename}</span>
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="alert alert-info mt-4">
                            <Shield size={14} />
                            <span style={{ fontSize: '0.8rem' }}>The report content and custody chains will be cryptographically signed with your Ed25519 private key to ensure non-repudiation.</span>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={onClose} disabled={loading}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleGenerate} disabled={loading || selectedEvidence.length === 0} id="generate-report-submit">
                                {loading ? <><div className="spinner" /> Signing...</> : <><PenTool size={16} /> Sign & Generate</>}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default function CaseDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { hasRole } = useAuth();
    const [caseData, setCaseData] = useState(null);
    const [reportsData, setReportsData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showUpload, setShowUpload] = useState(false);
    const [showAddMember, setShowAddMember] = useState(false);
    const [showGenerateReport, setShowGenerateReport] = useState(false);
    const [activeTab, setActiveTab] = useState('evidence');
    const [verifyingReportId, setVerifyingReportId] = useState(null);

    const loadCase = async () => {
        try {
            const { data } = await casesApi.get(id);
            setCaseData(data);

            try {
                const repRes = await casesApi.listReports(id);
                setReportsData(repRes.data.reports || []);
            } catch (e) {
                console.warn("Could not load reports");
            }
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to load case');
            navigate('/cases');
        } finally { setLoading(false); }
    };

    useEffect(() => { loadCase(); }, [id]);

    if (loading) return <div className="loading-overlay"><div className="loading-spinner-big" /></div>;
    if (!caseData) return null;

    const priorityBadge = (p) => ({ CRITICAL: 'badge-danger', HIGH: 'badge-warning', MEDIUM: 'badge-warning', LOW: 'badge-primary' })[p] || 'badge-gray';
    const statusBadge = (s) => ({ ACTIVE: 'badge-success', CLOSED: 'badge-gray', ARCHIVED: 'badge-gray' })[s] || 'badge-gray';
    const integrityBadge = (s) => ({ VERIFIED: 'badge-success', FAILED: 'badge-danger', PENDING: 'badge-warning' })[s] || 'badge-gray';

    return (
        <div className="fade-in">
            <div className="page-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => navigate('/cases')}><ArrowLeft size={16} /> Back</button>
                    <div>
                        <div className="page-title">
                            <span className="mono" style={{ color: 'var(--color-cyan)' }}>{caseData.case_number}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-1)' }}>
                            <h2 style={{ fontSize: '1.1rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>{caseData.title}</h2>
                            <span className={`badge ${priorityBadge(caseData.priority)}`}>{caseData.priority}</span>
                            <span className={`badge ${statusBadge(caseData.status)} badge-dot`}>{caseData.status}</span>
                        </div>
                    </div>
                </div>
                <div className="page-actions">
                    {hasRole('ADMIN', 'INVESTIGATOR') && (
                        <>
                            <button className="btn btn-secondary btn-sm" onClick={() => setShowAddMember(true)}>
                                <Users size={14} /> Add Member
                            </button>
                            <button className="btn btn-primary" onClick={() => setShowUpload(true)} id="upload-evidence-btn">
                                <Upload size={16} /> Upload Evidence
                            </button>
                        </>
                    )}
                    {hasRole('ADMIN', 'AUDITOR') && (
                        <button className="btn btn-info" onClick={() => setShowGenerateReport(true)}>
                            <FileText size={16} /> Generate Report
                        </button>
                    )}
                </div>
            </div>

            {/* Case Info Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
                {[
                    { label: 'Case Type', value: caseData.case_type?.replace(/_/g, ' '), icon: '🔍' },
                    { label: 'Evidence Items', value: caseData.evidence_summary?.length ?? 0, icon: '📁' },
                    { label: 'Team Members', value: caseData.members?.length ?? 0, icon: '👥' },
                    { label: 'Created', value: caseData.created_at ? format(new Date(caseData.created_at), 'MMM d, yyyy') : '—', icon: '📅' },
                ].map(item => (
                    <div key={item.label} className="card" style={{ padding: 'var(--space-4)' }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: 'var(--space-2)' }}>{item.icon}</div>
                        <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--color-text-primary)' }}>{item.value}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{item.label}</div>
                    </div>
                ))}
            </div>

            {/* Description */}
            {caseData.description && (
                <div className="card mb-6">
                    <div className="card-title mb-4" style={{ marginBottom: 'var(--space-3)' }}>Case Description</div>
                    <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>{caseData.description}</p>
                </div>
            )}

            {/* Tabs */}
            <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-5)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-2)' }}>
                {[
                    { id: 'evidence', label: '📄 Evidence', count: caseData.evidence_summary?.length },
                    { id: 'members', label: '👥 Team Members', count: caseData.members?.length },
                    { id: 'reports', label: '📑 Reports', count: reportsData.length },
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        style={{
                            background: activeTab === tab.id ? 'var(--color-primary-glow)' : 'none',
                            border: 'none', borderRadius: 'var(--radius-md)', padding: 'var(--space-2) var(--space-4)',
                            color: activeTab === tab.id ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                            fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', transition: 'var(--transition)',
                        }}
                    >
                        {tab.label} {tab.count !== undefined && <span className="badge badge-gray" style={{ fontSize: '0.7rem' }}>{tab.count}</span>}
                    </button>
                ))}
            </div>

            {/* Evidence Tab */}
            {activeTab === 'evidence' && (
                <div className="card fade-in">
                    {caseData.evidence_summary?.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📂</div>
                            <div className="empty-state-title">No evidence uploaded yet</div>
                            {hasRole('ADMIN', 'INVESTIGATOR') && (
                                <button className="btn btn-primary mt-4" onClick={() => setShowUpload(true)}>
                                    <Upload size={16} /> Upload First Evidence
                                </button>
                            )}
                        </div>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Evidence #</th><th>Filename</th><th>SHA-256</th><th>Integrity</th><th>Encryption</th><th>Status</th><th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {caseData.evidence_summary.map(e => (
                                        <tr key={e.id}>
                                            <td className="td-mono">{e.evidence_number}</td>
                                            <td className="td-primary">{e.original_filename}</td>
                                            <td>
                                                <div className="hash-display" style={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={e.sha256_hash}>
                                                    {e.sha256_hash?.slice(0, 16)}…
                                                </div>
                                            </td>
                                            <td><span className={`badge ${integrityBadge(e.integrity_status)} badge-dot`}>{e.integrity_status}</span></td>
                                            <td><span className="badge badge-success">AES-256-GCM</span></td>
                                            <td><span className="badge badge-primary badge-dot">{e.status}</span></td>
                                            <td>
                                                <button className="btn btn-ghost btn-sm" onClick={() => navigate(`/evidence/${e.id}`)}>View</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Members Tab */}
            {activeTab === 'members' && (
                <div className="card fade-in">
                    {caseData.members?.length === 0 ? (
                        <div className="empty-state"><div className="empty-state-title">No members</div></div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            {caseData.members.map(m => (
                                <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                                    <div className="user-avatar">{m.full_name?.charAt(0)}</div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{m.full_name}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{m.username}</div>
                                    </div>
                                    <span className="badge badge-primary">{m.role}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Reports Tab */}
            {activeTab === 'reports' && (
                <div className="card fade-in">
                    {reportsData.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-state-icon">📑</div>
                            <div className="empty-state-title">No reports generated yet</div>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Report #</th><th>Title</th><th>Generated By</th><th>Date</th><th>Signature</th><th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {reportsData.map(r => (
                                        <tr key={r.id}>
                                            <td className="td-mono">{r.report_number}</td>
                                            <td className="td-primary">{r.title}</td>
                                            <td>{r.generated_by_user?.username || '—'}</td>
                                            <td>{format(new Date(r.created_at), 'MMM d, HH:mm')}</td>
                                            <td>
                                                {r.is_signed ? <span className="badge badge-success">Ed25519</span> : <span className="badge badge-gray">None</span>}
                                            </td>
                                            <td>
                                                <button
                                                    className="btn btn-ghost btn-sm"
                                                    disabled={verifyingReportId === r.id}
                                                    onClick={async () => {
                                                        setVerifyingReportId(r.id);
                                                        try {
                                                            const { data } = await reportsApi.verifySignature(r.id);
                                                            if (data.is_valid) {
                                                                toast.success('Signature VERIFIED automatically');
                                                            } else {
                                                                toast.error('Signature verification FAILED');
                                                            }
                                                        } catch (e) {
                                                            toast.error('Verification request failed');
                                                        } finally {
                                                            setVerifyingReportId(null);
                                                        }
                                                    }}
                                                >
                                                    {verifyingReportId === r.id ? 'Verifying...' : 'Verify Signature'}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {showUpload && <UploadEvidenceModal caseId={id} onClose={() => setShowUpload(false)} onUploaded={loadCase} />}
            {showAddMember && <AddMemberModal caseId={id} onClose={() => { setShowAddMember(false); loadCase(); }} />}
            {showGenerateReport && <GenerateReportModal caseId={id} evidenceItems={caseData.evidence_summary || []} onClose={() => setShowGenerateReport(false)} onGenerated={loadCase} />}
        </div>
    );
}
