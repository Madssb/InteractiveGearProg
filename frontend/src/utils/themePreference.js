export const THEME_PREFERENCE_KEY = 'themePreference';
export const THEME_PREFERENCES = ['system', 'light', 'dark'];

export function normalizeThemePreference(value) {
  return THEME_PREFERENCES.includes(value) ? value : 'system';
}

export function getSavedThemePreference() {
  try {
    return normalizeThemePreference(JSON.parse(localStorage.getItem(THEME_PREFERENCE_KEY)));
  } catch {
    return 'system';
  }
}

export function applyThemePreference(preference) {
  const normalized = normalizeThemePreference(preference);
  const root = document.documentElement;

  if (normalized === 'system') {
    root.removeAttribute('data-theme');
    root.style.removeProperty('color-scheme');
    return;
  }

  root.dataset.theme = normalized;
  root.style.colorScheme = normalized;
}
