import { AuthLayout } from '../layouts';
import { ForgotPasswordForm } from '../features/auth';

export function ForgotPasswordPage() {
    return (
        <AuthLayout>
            <ForgotPasswordForm />
        </AuthLayout>
    );
}

