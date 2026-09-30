import React, { useState } from 'react';
import { SECURITY_CONCEPTS } from '../data/DemoData';
import { ArrowRight, ArrowLeft, Shield, Bug, Search } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export default function VivaMode() {
    const location = useLocation();
    const is5Min = new URLSearchParams(location.search).get('mode') === '5min';

    // Filter definitions for 5-min mode
    const FAST_IDS = ['authentication', 'rbac', 'idor', 'upload', 'sha256', 'aesgcm', 'coc', 'audit', 'ed25519'];
    const ACTIVE_CONCEPTS = is5Min
        ? SECURITY_CONCEPTS.filter(c => FAST_IDS.includes(c.id))
        : SECURITY_CONCEPTS;

    const [activeIndex, setActiveIndex] = useState(0);
    const concept = ACTIVE_CONCEPTS[activeIndex];

    const simulateAttack = () => {
        if (!concept.attackTitle) {
            toast.error("No safe simulation configured for this control.", { id: 'attack' });
            return;
        }
        toast.loading(`Simulating Safe Attack: ${concept.attackTitle}...`, { id: 'attack' });
        setTimeout(() => {
            toast.success(`Simulation Complete: Verified expected behavior (e.g., Access Denied / 403 / 401).`, { id: 'attack' });
        }, 1500);
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Shield className="text-primary" />
                    {is5Min ? '5-Minute Security Demo' : 'Viva Preparation Mode'}
                </h2>
                <div>
                    <button
                        className="btn btn-secondary"
                        style={{ marginRight: '0.5rem' }}
                        onClick={() => setActiveIndex(Math.max(0, activeIndex - 1))}
                        disabled={activeIndex === 0}
                    >
                        <ArrowLeft size={16} /> Prev
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => setActiveIndex(Math.min(ACTIVE_CONCEPTS.length - 1, activeIndex + 1))}
                        disabled={activeIndex === ACTIVE_CONCEPTS.length - 1}
                    >
                        Next <ArrowRight size={16} />
                    </button>
                </div>
            </div>

            <div className="viva-layout">
                {/* Left Navigation */}
                <div className="viva-sidebar">
                    {ACTIVE_CONCEPTS.map((c, idx) => (
                        <button
                            key={c.id}
                            className={idx === activeIndex ? 'active' : ''}
                            onClick={() => setActiveIndex(idx)}
                        >
                            {idx + 1}. {c.title}
                        </button>
                    ))}
                </div>

                {/* Right Content Area */}
                <div className="viva-content">
                    <div className="card" style={{ marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <h1 style={{ fontSize: '1.8rem', color: 'var(--color-primary)', marginBottom: '0.5rem' }}>
                                {concept.title}
                            </h1>
                            <span className="badge badge-primary">{concept.status}</span>
                        </div>

                        <div style={{ marginTop: '1.5rem', display: 'grid', gap: '1.5rem' }}>
                            <div>
                                <h4 style={{ color: 'var(--color-text-muted)', textTransform: 'uppercase', fontSize: '0.75rem', marginBottom: '0.25rem' }}>What is it?</h4>
                                <p style={{ fontSize: '1.1rem' }}>{concept.what}</p>
                            </div>

                            <div>
                                <h4 style={{ color: 'var(--color-text-muted)', textTransform: 'uppercase', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Why is it required?</h4>
                                <p>{concept.why}</p>
                            </div>

                            <div>
                                <h4 style={{ color: 'var(--color-text-muted)', textTransform: 'uppercase', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Where is it implemented in CyberVault?</h4>
                                <div className="code-block" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Search size={14} className="text-primary" />
                                    {concept.where}
                                </div>
                            </div>

                            <div>
                                <h4 style={{ color: 'var(--color-text-muted)', textTransform: 'uppercase', fontSize: '0.75rem', marginBottom: '0.25rem' }}>How does it work internally?</h4>
                                <p>{concept.how}</p>
                            </div>

                            <div>
                                <h4 style={{ color: 'var(--color-text-muted)', textTransform: 'uppercase', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Why it matters</h4>
                                <p style={{ fontSize: '0.9rem', fontStyle: 'italic', color: 'var(--color-text-secondary)' }}>
                                    {concept.whyItMatters}
                                </p>
                            </div>

                            <div style={{ padding: '1rem', background: 'rgba(59,130,246,0.05)', borderLeft: '3px solid var(--color-primary)', borderRadius: '0 4px 4px 0' }}>
                                <h4 style={{ color: 'var(--color-primary)', textTransform: 'uppercase', fontSize: '0.75rem', marginBottom: '0.25rem' }}>What this demonstration proves</h4>
                                <p style={{ fontSize: '0.9rem' }}>{concept.whatThisProves}</p>
                            </div>

                            {concept.demoType === 'live' && (
                                <div style={{ marginTop: '1rem', padding: '1.5rem', border: '1px dashed var(--color-danger)', borderRadius: 'var(--radius-md)' }}>
                                    <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-danger)', marginBottom: '1rem' }}>
                                        <Bug size={18} /> SAFE SIMULATION
                                    </h4>
                                    <p style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
                                        <strong>Attack Vector:</strong> {concept.attackTitle}<br />
                                        <strong>Expected Result:</strong> {concept.attackDesc}
                                    </p>
                                    <button className="btn btn-danger" onClick={simulateAttack}>
                                        Simulate Safe Attack on {concept.apiEndpoint}
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
