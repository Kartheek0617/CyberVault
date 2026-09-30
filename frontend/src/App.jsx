import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, GuestRoute } from './components/ProtectedRoute';
import AppLayout from './components/AppLayout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import CasesPage from './pages/CasesPage';
import CaseDetailPage from './pages/CaseDetailPage';
import EvidenceDetailPage from './pages/EvidenceDetailPage';
import AuditLogsPage from './pages/AuditLogsPage';
import UsersPage from './pages/UsersPage';
import SecurityEventsPage from './pages/SecurityEventsPage';
import SecurityDemoCenter from './pages/SecurityDemoCenter';
import VivaMode from './pages/VivaMode';

function LayoutWrapper({ children }) {
    return (
        <ProtectedRoute>
            <AppLayout>{children}</AppLayout>
        </ProtectedRoute>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Toaster
                    position="top-right"
                    toastOptions={{
                        style: {
                            background: 'var(--color-bg-card)',
                            color: 'var(--color-text-primary)',
                            border: '1px solid var(--color-border)',
                            fontFamily: 'var(--font-sans)',
                            fontSize: '0.875rem',
                        },
                        success: { iconTheme: { primary: '#10b981', secondary: '#022c22' } },
                        error: { iconTheme: { primary: '#ef4444', secondary: '#450a0a' } },
                    }}
                />

                <Routes>
                    {/* Public routes */}
                    <Route
                        path="/login"
                        element={<GuestRoute><LoginPage /></GuestRoute>}
                    />

                    {/* Protected routes */}
                    <Route path="/dashboard" element={<LayoutWrapper><Dashboard /></LayoutWrapper>} />
                    <Route path="/cases" element={<LayoutWrapper><CasesPage /></LayoutWrapper>} />
                    <Route path="/cases/:id" element={<LayoutWrapper><CaseDetailPage /></LayoutWrapper>} />
                    <Route path="/evidence/:id" element={<LayoutWrapper><EvidenceDetailPage /></LayoutWrapper>} />
                    <Route path="/audit-logs" element={
                        <ProtectedRoute roles={['ADMIN', 'AUDITOR']}>
                            <AppLayout><AuditLogsPage /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/security" element={
                        <ProtectedRoute roles={['ADMIN', 'AUDITOR']}>
                            <AppLayout><SecurityEventsPage /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/users" element={
                        <ProtectedRoute roles={['ADMIN']}>
                            <AppLayout><UsersPage /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/demo" element={
                        <ProtectedRoute>
                            <AppLayout><SecurityDemoCenter /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/viva" element={
                        <ProtectedRoute>
                            <AppLayout><VivaMode /></AppLayout>
                        </ProtectedRoute>
                    } />

                    {/* Fallback */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}
