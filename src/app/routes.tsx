import { createBrowserRouter } from "react-router";
import { LandingPage } from "./pages/landing-page";
import { LoginPage } from "./pages/login-page";
import { SignUpPage } from "./pages/sign-up-page";
import { DashboardPage } from "./pages/dashboard-page";
import { CreateInputPage } from "./pages/create-input-page";
import { PersonasPage } from "./pages/personas-page";
import { ScriptPage } from "./pages/script-page";
import { AudioPage } from "./pages/audio-page";
import { CoverArtPage } from "./pages/cover-art-page";
import { PublishPage } from "./pages/publish-page";
import { PersonaLibraryPage } from "./pages/persona-library-page";
import { SettingsPage } from "./pages/settings-page";
import { MyLibraryPage } from "./pages/my-library-page";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: LandingPage,
  },
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/signup",
    Component: SignUpPage,
  },
  {
    path: "/dashboard",
    Component: DashboardPage,
  },
  {
    path: "/create/input",
    Component: CreateInputPage,
  },
  {
    path: "/create/personas",
    Component: PersonasPage,
  },
  {
    path: "/create/script",
    Component: ScriptPage,
  },
  {
    path: "/create/audio",
    Component: AudioPage,
  },
  {
    path: "/create/cover",
    Component: CoverArtPage,
  },
  {
    path: "/create/publish",
    Component: PublishPage,
  },
  {
    path: "/personas",
    Component: PersonaLibraryPage,
  },
  {
    path: "/settings",
    Component: SettingsPage,
  },
  {
    path: "/library",
    Component: MyLibraryPage,
  },
]);