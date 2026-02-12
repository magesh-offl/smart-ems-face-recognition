import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthGuard, AdmissionGuard, TeacherGuard } from './features/auth';
import { DashboardLayout } from './layouts';
import { LoginPage, ForgotPasswordPage, DashboardPage, RecognitionPage, PersonsPage, AdmissionPage } from './pages';
import { ROUTES } from './config';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 0, // Always refetch on navigation
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
          <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />

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
          {/* Admin Routes */}
          <Route
            path={ROUTES.ADMISSION}
            element={
              <AdmissionGuard>
                <DashboardLayout>
                  <AdmissionPage />
                </DashboardLayout>
              </AdmissionGuard>
            }
          />
          <Route
            path={ROUTES.RECOGNITION}
            element={
              <TeacherGuard>
                <DashboardLayout>
                  <RecognitionPage />
                </DashboardLayout>
              </TeacherGuard>
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

          {/* Redirect root to login */}
          <Route path={ROUTES.HOME} element={<Navigate to={ROUTES.LOGIN} replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

