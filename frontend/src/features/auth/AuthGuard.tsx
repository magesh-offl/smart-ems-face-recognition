/**
 * Route Guard Components
 * 
 * Provides authentication and authorization protection for routes.
 * These guards check localStorage for valid credentials on each page load
 * and redirect to login if authentication is missing or invalid.
 * 
 * Usage:
 *   <AuthGuard>        - Requires any authenticated user
 *   <AdminGuard>       - Requires super_admin or admin role
 *   <TeacherGuard>     - Requires teacher role or higher
 */
import { type ReactNode, useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { ROUTES } from '../../config';

interface GuardProps {
    children: ReactNode;
}

/**
 * Check if user is authenticated by validating localStorage token and user data.
 * Returns the user object if valid, null otherwise.
 */
function getAuthenticatedUser(): { role: string; role_id: string } | null {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    // Must have both token and user data
    if (!token || !userStr) {
        return null;
    }
    
    try {
        const user = JSON.parse(userStr);
        
        // Validate user object has required fields
        if (!user.role_id) {
            return null;
        }
        
        return user;
    } catch {
        // Invalid JSON in localStorage
        return null;
    }
}

/**
 * Clear all authentication data from localStorage
 */
function clearAuthData(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('apiKey');
}

/**
 * AuthGuard - Protects routes requiring any authenticated user.
 * Redirects to login page if not authenticated.
 */
export function AuthGuard({ children }: GuardProps) {
    const location = useLocation();
    const [isChecking, setIsChecking] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    
    useEffect(() => {
        const user = getAuthenticatedUser();
        
        if (user) {
            setIsAuthenticated(true);
        } else {
            // Clear any partial/invalid auth data
            clearAuthData();
            setIsAuthenticated(false);
        }
        
        setIsChecking(false);
    }, [location.pathname]);
    
    // Show nothing while checking (prevents flash)
    if (isChecking) {
        return null;
    }
    
    if (!isAuthenticated) {
        // Redirect to login, saving the attempted URL
        return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
    }
    
    return <>{children}</>;
}

/**
 * AdminGuard - Protects routes requiring admin or super_admin role.
 * Redirects to login if not authenticated, or dashboard if not authorized.
 */
export function AdmissionGuard({ children }: GuardProps) {
    const location = useLocation();
    const [isChecking, setIsChecking] = useState(true);
    const [authState, setAuthState] = useState<'authenticated' | 'unauthorized' | 'unauthenticated'>('unauthenticated');
    
    useEffect(() => {
        const user = getAuthenticatedUser();
        
        if (!user) {
            clearAuthData();
            setAuthState('unauthenticated');
        } else {
            // Check for admin roles: ROL0001 (super_admin) or ROL0002 (admin)
            const isAdmin = user.role_id === 'ROL0001' || user.role_id === 'ROL0002';
            // Also check role name if available
            const hasAdminRole = user.role === 'super_admin' || user.role === 'admin';
            
            if (isAdmin || hasAdminRole) {
                setAuthState('authenticated');
            } else {
                setAuthState('unauthorized');
            }
        }
        
        setIsChecking(false);
    }, [location.pathname]);
    
    if (isChecking) {
        return null;
    }
    
    if (authState === 'unauthenticated') {
        return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
    }
    
    if (authState === 'unauthorized') {
        // User is logged in but not admin - redirect to dashboard
        return <Navigate to={ROUTES.DASHBOARD} replace />;
    }
    
    return <>{children}</>;
}

/**
 * TeacherGuard - Protects routes requiring teacher, admin, or super_admin role.
 * Redirects to login if not authenticated, or dashboard if not authorized.
 */
export function TeacherGuard({ children }: GuardProps) {
    const location = useLocation();
    const [isChecking, setIsChecking] = useState(true);
    const [authState, setAuthState] = useState<'authenticated' | 'unauthorized' | 'unauthenticated'>('unauthenticated');
    
    useEffect(() => {
        const user = getAuthenticatedUser();
        
        if (!user) {
            clearAuthData();
            setAuthState('unauthenticated');
        } else {
            // Check for teacher roles: ROL0001, ROL0002, ROL0003
            const allowedRoles = ['ROL0001', 'ROL0002', 'ROL0003'];
            const allowedRoleNames = ['super_admin', 'admin', 'teacher'];
            
            const isAllowed = allowedRoles.includes(user.role_id) || 
                              (user.role && allowedRoleNames.includes(user.role));
            
            setAuthState(isAllowed ? 'authenticated' : 'unauthorized');
        }
        
        setIsChecking(false);
    }, [location.pathname]);
    
    if (isChecking) {
        return null;
    }
    
    if (authState === 'unauthenticated') {
        return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
    }
    
    if (authState === 'unauthorized') {
        return <Navigate to={ROUTES.DASHBOARD} replace />;
    }
    
    return <>{children}</>;
}
