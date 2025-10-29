/**
 * YAGO v8.0 - i18n Configuration
 * Multi-language support for 7 languages
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translations
import enTranslation from './locales/en.json';
import frTranslation from './locales/fr.json';
import trTranslation from './locales/tr.json';
import deTranslation from './locales/de.json';
import esTranslation from './locales/es.json';
import itTranslation from './locales/it.json';
import ptTranslation from './locales/pt.json';

// Language resources
const resources = {
  en: { translation: enTranslation },
  fr: { translation: frTranslation },
  tr: { translation: trTranslation },
  de: { translation: deTranslation },
  es: { translation: esTranslation },
  it: { translation: itTranslation },
  pt: { translation: ptTranslation },
};

// Supported languages configuration
export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', flag: '🇹🇷' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹' },
] as const;

export type SupportedLanguage = typeof SUPPORTED_LANGUAGES[number]['code'];

// Initialize i18next
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: import.meta.env.DEV,

    // Language detection
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'yago_language',
    },

    // Interpolation
    interpolation: {
      escapeValue: false, // React already escapes
    },

    // React specific
    react: {
      useSuspense: true,
    },

    // Backend configuration (if using HTTP backend)
    backend: {
      loadPath: '/locales/{{lng}}.json',
    },

    // Namespace configuration
    defaultNS: 'translation',
    ns: ['translation'],

    // Missing key handling
    saveMissing: import.meta.env.DEV,
    missingKeyHandler: (lng, ns, key) => {
      if (import.meta.env.DEV) {
        console.warn(`Missing translation: ${lng}:${ns}:${key}`);
      }
    },
  });

export default i18n;
