import { AlertTriangle, RefreshCw } from 'lucide-react';
import { dashboardApi } from '../services/api';
import { useEffect, useState } from 'react';
import { format } from 'date-fns';

export default function SecurityEventsPage() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const { data } = await dashboardApi.securityEvents();
            setEvents(data.events || []);
        } catch { setEvents([]); } finally { setLoading(false); }
    };

    useEffect(() => { load(); }, []);

    const severityBadge = (s) => ({ HIGH: 'badge-danger', MEDIUM: 'badge-warning', LOW: 'badge-primary', CRITICAL: 'badge-danger' })[s] || 'badge-gray';

    return (
        <div className="fade-in">
            <div className="page-header">
                <div>
                    <div className="page-title"><AlertTriangle size={24} style={{ color: 'var(--color-danger)' }} /> Security Events</div>
                    <div className="page-subtitle">System-generated security alerts and anomaly detections</div>
                </div>
                <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /> Refresh</button>
            </div>

            <div className="card">
                {loading ? (
                    <div className="loading-overlay"><div className="loading-spinner-big" /></div>
                ) : events.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">✅</div>
                        <div className="empty-state-title">No security events detected</div>
                        <p className="text-muted text-sm mt-2">The system is operating normally.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr><th>Event Type</th><th>Severity</th><th>Description</th><th>Time</th><th>Resolved</th></tr>
                            </thead>
                            <tbody>
                                {events.map(e => (
                                    <tr key={e.id}>
                                        <td className="td-primary" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{e.event_type}</td>
                                        <td><span className={`badge ${severityBadge(e.severity)}`}>{e.severity}</span></td>
                                        <td style={{ fontSize: '0.85rem', maxWidth: '350px' }}>{e.description}</td>
                                        <td style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
                                            {e.timestamp ? format(new Date(e.timestamp), 'MMM d, HH:mm:ss') : '—'}
                                        </td>
                                        <td>{e.resolved ? '✅ Resolved' : <span className="badge badge-warning badge-dot">Open</span>}</td>
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
