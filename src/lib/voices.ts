/**
 * Voice catalogues mirrored from the backend.
 * Keep in sync with BackEnd voice configs (ENGLISH_VOICES, MUNSIT_VOICES).
 */

export type Gender = 'male' | 'female';
export type VoiceStyle =
  | 'calm'
  | 'energetic'
  | 'professional'
  | 'warm'
  | 'authoritative'
  | 'clear'
  | 'natural';

export interface VoiceOption {
  /** Key the backend expects in voice_id_host / voice_id_guest. */
  id: string;
  /** Display name. */
  name: string;
  gender: Gender;
  style: VoiceStyle;
  /** Munsit-only — purely informational for the UI. */
  dialect?: 'saudi' | 'hijazi' | 'kuwaiti' | 'fusha';
}

export const ENGLISH_VOICES: VoiceOption[] = [
  { id: 'pNInz6obpgDQGcFmaJgB', name: 'Adam',    gender: 'male',   style: 'professional' },
  { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Sarah',   gender: 'female', style: 'professional' },
  { id: 'JBFqnCBsd6RMkjVDRZzb', name: 'George',  gender: 'male',   style: 'warm' },
  { id: 'Xb7hH8MSUJpSbSDYk0k2', name: 'Alice',   gender: 'female', style: 'calm' },
  { id: 'IKne3meq5aSn9XLyUdCD', name: 'Charlie', gender: 'male',   style: 'energetic' },
  { id: 'hpp4J3VqNfWAUOO0d1Us', name: 'Bella',   gender: 'female', style: 'warm' },
];

export const ARABIC_VOICES: VoiceOption[] = [
  { id: 'ar-najdi-male-2',     name: 'Fahad', gender: 'male',   style: 'professional', dialect: 'saudi' },
  { id: 'ar-najdi-female-1',   name: 'Maha',  gender: 'female', style: 'calm',         dialect: 'saudi' },
  { id: 'ar-egyptian-male-1',  name: 'Ahmed', gender: 'male',   style: 'natural',      dialect: 'saudi' },
  { id: 'ar-hijazi-female-1',  name: 'Lama',  gender: 'female', style: 'warm',         dialect: 'hijazi' },
  { id: 'ar-kuwaiti-male-1',   name: 'Hamad', gender: 'male',   style: 'energetic',    dialect: 'kuwaiti' },
];

export const STYLE_OPTIONS: VoiceStyle[] = [
  'professional',
  'calm',
  'energetic',
  'warm',
  'authoritative',
  'clear',
  'natural',
];

export function voicesFor(language: 'EN' | 'AR'): VoiceOption[] {
  return language === 'AR' ? ARABIC_VOICES : ENGLISH_VOICES;
}

export function findVoice(language: 'EN' | 'AR', id: string): VoiceOption | undefined {
  return voicesFor(language).find((v) => v.id === id);
}
