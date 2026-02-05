import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthGuard } from './features/auth';
import { DashboardLayout } from './layouts';
import { LoginPage, DashboardPage, RecognitionPage, PersonsPage } from './pages';
import { ROUTES } from './config';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path={ROUTES.LOGIN} element={<LoginPage />} />

          {/* Protected Routes */}
          <Route
            path={ROUTES.DASHBOARD}
            element={
              <AuthGuard>
                <DashboardLayout>
                  <DashboardPage />
                </DashboardLayout>
              </AuthGuard>
            }
          />
          <Route
            path={ROUTES.RECOGNITION}
            element={
              <AuthGuard>
                <DashboardLayout>
                  <RecognitionPage />
                </DashboardLayout>
              </AuthGuard>
            }
          />
          <Route
            path={ROUTES.PERSONS}
            element={
              <AuthGuard>
                <DashboardLayout>
                  <PersonsPage />
                </DashboardLayout>
              </AuthGuard>
            }
          />

          {/* Redirect root to dashboard */}
          <Route path={ROUTES.HOME} element={<Navigate to={ROUTES.DASHBOARD} replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
