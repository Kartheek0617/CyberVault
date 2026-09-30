import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, Eye, EyeOff, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';

const DEMO_ACCOUNTS = [
    { label: 'Admin', user: 'admin', pass: 'Admin@CyberVault2026!' },
    { label: 'Investigator', user: 'inv_harrison', pass: 'Invest@Vault2026!' },
    { label: 'Custodian', user: 'cust_morgan', pass: 'Custodian@2026!' },
    { label: 'Auditor', user: 'auditor_chen', pass: 'Auditor@Vault2026!' },
];

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const { login, loading } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (!username || !password) {
            setError('Please enter your credentials.');
            return;
        }
        const result = await login(username, password);
        if (result.success) {
            toast.success('Authentication successful');
            navigate('/dashboard');
        } else {
            setError(result.error);
        }
    };

    const fillDemo = (acc) => {
        setUsername(acc.user);
        setPassword(acc.pass);
        setError('');
    };

    return (
        <div className="login-page">
            <div className="login-container fade-in">
                {/* Security warning banner */}
                <div className="alert alert-warning mb-4" style={{ fontSize: '0.75rem' }}>
                    <AlertTriangle size={14} />
                    <span>
                        <strong>Demo System</strong> — Fictional data only. Do not submit real evidence.
                    </span>
                </div>

                <div className="login-card">
                    <div className="login-header">
                        <div className="login-brand-icon">
                            <Shield size={32} color="white" />
                        </div>
                        <div className="login-title">CYBERVAULT</div>
                        <div className="login-subtitle">Secure Digital Evidence Management System</div>
                    </div>

                    {/* Demo Credentials */}
                    <div className="login-demo-creds">
                        <div className="login-demo-title">⚠ Demo Credentials (Click to Fill)</div>
                        {DEMO_ACCOUNTS.map(acc => (
                            <div key={acc.user} className="login-demo-item" onClick={() => fillDemo(acc)}>
                                [{acc.label}] {acc.user} / {acc.pass}
                            </div>
                        ))}
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label className="form-label">Username</label>
                            <input
                                id="username"
                                type="text"
                                className="form-input"
                                placeholder="Enter your username"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                autoComplete="username"
                                autoFocus
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <div style={{ position: 'relative' }}>
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    className="form-input"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    autoComplete="current-password"
                                    style={{ paddingRight: '3rem' }}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    style={{
                                        position: 'absolute', right: '12px', top: '50%',
                                        transform: 'translateY(-50%)', background: 'none',
                                        border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)',
                                        display: 'flex', alignItems: 'center',
                                    }}
                                >
                                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="alert alert-danger mb-4">
                                <Lock size={14} />
                                <span>{error}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn btn-primary w-full btn-lg"
                            disabled={loading}
                            id="login-submit"
                        >
                            {loading ? (
                                <><div className="spinner" /> Authenticating...</>
                            ) : (
                                <><Lock size={18} /> Authenticate</>
                            )}
                        </button>
                    </form>

                    <div style={{ marginTop: 'var(--space-6)', textAlign: 'center' }}>
                        <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                            🔒 Argon2id hashing · JWT tokens · AES-256-GCM encryption · Ed25519 signatures
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
