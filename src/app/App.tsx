import { RouterProvider } from 'react-router';
import { router } from './routes';
import { ErrorBoundary } from './components/error-boundary';
import { AuthProvider } from './providers/auth-provider';
import { GenerationProvider } from './providers/generation-provider';

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <GenerationProvider>
          <RouterProvider router={router} />
        </GenerationProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
