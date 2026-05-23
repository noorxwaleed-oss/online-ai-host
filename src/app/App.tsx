import { RouterProvider } from 'react-router';
import { router } from './routes';
import { ErrorBoundary } from './components/error-boundary';
import { AuthProvider } from './providers/auth-provider';

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ErrorBoundary>
  );
}
