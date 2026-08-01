import { lazy, Suspense } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { queryClient } from './api/client';
import { useAuthStore } from './store/authStore';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import AmbientBackground from './components/ui/AmbientBackground';

const LandingPage = lazy(() => import('./pages/LandingPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const ResourcesPage = lazy(() => import('./pages/ResourcesPage'));

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  if (!isAuthenticated) {
    return <Navigate to="/?login=true" replace />;
  }
  return <>{children}</>;
};

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
};

import { AnimatePresence, MotionConfig } from 'framer-motion';
import { PageTransition } from './components/ui/Animations';

const AnimatedRoutes = () => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <PageTransition key={location.pathname} className="relative z-10">
        <Suspense fallback={
          <div className="min-h-screen flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-[#0d9488] border-t-transparent rounded-full animate-spin" />
          </div>
        }>
          <Routes location={location} key={location.pathname}>
            <Route
              path="/"
              element={
                <PublicRoute>
                  <LandingPage />
                </PublicRoute>
              }
            />
            <Route
              path="/pricing"
              element={
                <PublicRoute>
                  <PricingPage />
                </PublicRoute>
              }
            />
            <Route
              path="/resources"
              element={
                <PublicRoute>
                  <ResourcesPage />
                </PublicRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Suspense>
      </PageTransition>
    </AnimatePresence>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MotionConfig reducedMotion="user">
        <AmbientBackground />
        <BrowserRouter>
          <ErrorBoundary>
            <AnimatedRoutes />
          </ErrorBoundary>
        </BrowserRouter>
      </MotionConfig>
    </QueryClientProvider>
  );
}

export default App;
