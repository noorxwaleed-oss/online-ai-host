import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { GenerationResult, ProjectDetail } from '@/lib/api';

export type InputType = 'url' | 'pdf';

export interface InputDraft {
  input_type: InputType;
  /** URL string when input_type === 'url'; uploaded file name when 'pdf'. */
  content: string;
  pdf_file: File | null;
  podcast_name: string;
  language: 'EN' | 'AR';
}

export interface PersonaDraft {
  host_name: string;
  host_gender: 'male' | 'female';
  host_style: string;
  voice_id_host: string;
  guest_name: string;
  guest_gender: 'male' | 'female';
  guest_style: string;
  voice_id_guest: string;
}

interface GenerationContextValue {
  input: InputDraft;
  personas: PersonaDraft;
  setInput: (next: Partial<InputDraft>) => void;
  setPersonas: (next: Partial<PersonaDraft>) => void;

  /** Set to true while POST / is in flight. */
  isGenerating: boolean;
  setIsGenerating: (v: boolean) => void;

  /** Response from POST /. */
  result: GenerationResult | null;
  setResult: (r: GenerationResult | null) => void;

  /** Hydrated from GET /api/projects/{user_id}/latest after generation. */
  project: ProjectDetail | null;
  setProject: (p: ProjectDetail | null) => void;

  /** The script JSON fetched from project.script_url. */
  scriptLines: ScriptLine[] | null;
  setScriptLines: (s: ScriptLine[] | null) => void;

  reset: () => void;
}

export interface ScriptLine {
  speaker: 'HOST' | 'GUEST';
  text: string;
}

const DEFAULT_INPUT: InputDraft = {
  input_type: 'url',
  content: '',
  pdf_file: null,
  podcast_name: '',
  language: 'EN',
};

const DEFAULT_PERSONAS: PersonaDraft = {
  host_name: '',
  host_gender: 'male',
  host_style: 'professional',
  voice_id_host: '',
  guest_name: '',
  guest_gender: 'female',
  guest_style: 'energetic',
  voice_id_guest: '',
};

const GenerationContext = createContext<GenerationContextValue | undefined>(undefined);

export function GenerationProvider({ children }: { children: ReactNode }) {
  const [input, setInputState] = useState<InputDraft>(DEFAULT_INPUT);
  const [personas, setPersonasState] = useState<PersonaDraft>(DEFAULT_PERSONAS);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [scriptLines, setScriptLines] = useState<ScriptLine[] | null>(null);

  const setInput = useCallback(
    (next: Partial<InputDraft>) => setInputState((prev) => ({ ...prev, ...next })),
    [],
  );
  const setPersonas = useCallback(
    (next: Partial<PersonaDraft>) => setPersonasState((prev) => ({ ...prev, ...next })),
    [],
  );

  const reset = useCallback(() => {
    setInputState(DEFAULT_INPUT);
    setPersonasState(DEFAULT_PERSONAS);
    setIsGenerating(false);
    setResult(null);
    setProject(null);
    setScriptLines(null);
  }, []);

  const value = useMemo<GenerationContextValue>(
    () => ({
      input,
      personas,
      setInput,
      setPersonas,
      isGenerating,
      setIsGenerating,
      result,
      setResult,
      project,
      setProject,
      scriptLines,
      setScriptLines,
      reset,
    }),
    [input, personas, setInput, setPersonas, isGenerating, result, project, scriptLines, reset],
  );

  return <GenerationContext.Provider value={value}>{children}</GenerationContext.Provider>;
}

export function useGeneration() {
  const ctx = useContext(GenerationContext);
  if (!ctx) throw new Error('useGeneration must be used within a GenerationProvider');
  return ctx;
}
