import { createBrowserRouter } from 'react-router';
import { LandingPage } from './pages/landing-page';
import { LoginPage } from './pages/login-page';
import { SignUpPage } from './pages/sign-up-page';
import { DashboardPage } from './pages/dashboard-page';
import { CreateInputPage } from './pages/create-input-page';
import { PersonasPage } from './pages/personas-page';
import { ScriptPage } from './pages/script-page';
import { AudioPage } from './pages/audio-page';
import { CoverArtPage } from './pages/cover-art-page';
import { PublishPage } from './pages/publish-page';
import { PersonaLibraryPage } from './pages/persona-library-page';
import { SettingsPage } from './pages/settings-page';
import { AccountPage } from './pages/settings/account-page';
import { NotificationsPage } from './pages/settings/notifications-page';
import { PrivacySecurityPage } from './pages/settings/privacy-security-page';
import { AppearancePage } from './pages/settings/appearance-page';
import { ApiIntegrationsPage } from './pages/settings/api-integrations-page';
import { MyLibraryPage } from './pages/my-library-page';
import { NotFoundPage } from './pages/not-found-page';
import { ProtectedRoute } from './components/protected-route';

export const router = createBrowserRouter([
  { path: '/', Component: LandingPage },
  { path: '/login', Component: LoginPage },
  { path: '/signup', Component: SignUpPage },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/create/input',
    element: (
      <ProtectedRoute>
        <CreateInputPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/create/personas',
    element: (
      <ProtectedRoute>
        <PersonasPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/create/script',
    element: (
      <ProtectedRoute>
        <ScriptPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/create/audio',
    element: (
      <ProtectedRoute>
        <AudioPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/create/cover',
    element: (
      <ProtectedRoute>
        <CoverArtPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/create/publish',
    element: (
      <ProtectedRoute>
        <PublishPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/personas',
    element: (
      <ProtectedRoute>
        <PersonaLibraryPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute>
        <SettingsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/account',
    element: (
      <ProtectedRoute>
        <AccountPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/notifications',
    element: (
      <ProtectedRoute>
        <NotificationsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/privacy',
    element: (
      <ProtectedRoute>
        <PrivacySecurityPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/appearance',
    element: (
      <ProtectedRoute>
        <AppearancePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/integrations',
    element: (
      <ProtectedRoute>
        <ApiIntegrationsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/library',
    element: (
      <ProtectedRoute>
        <MyLibraryPage />
      </ProtectedRoute>
    ),
  },
  { path: '*', Component: NotFoundPage },
]);
