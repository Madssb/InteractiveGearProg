import React, { useEffect, useState } from 'react';

/**
 * Get JSON object from local storage if it exists.
 * @param key Key of JSON Object
 * @returns JSON object if it exists, or undefined.
 */
function readSavedState(key: string) {
  const saved = localStorage.getItem(key);
  return saved !== null ? JSON.parse(saved) : undefined;
}

export function useLocalStorageState<T>(
  key: string, 
  defaultValue: T, 
  legacyKeys: string[] = []
): [T, React.Dispatch<React.SetStateAction<T>>]{
  // why is this being done again?
  const legacyKeySignature = legacyKeys.join("|");
  const [state, setState] = useState(() => {
    try {
      const saved = readSavedState(key);
      // found stored object
      if (saved !== undefined) return saved;


      const legacySaved = legacyKeys
        .map(readSavedState)
        .find(value => value !== undefined);
      return legacySaved !== undefined ? legacySaved : defaultValue;
    } catch {
      // what are we catching
      return defaultValue;
    }
  });

  useEffect(() => {
    try {
      const fallbackKeys = legacyKeySignature ? legacyKeySignature.split("|") : [];
      const saved = readSavedState(key);
      if (saved !== undefined) {
        setState(saved);
        return;
      }

      const legacySaved = fallbackKeys
        .map(readSavedState)
        .find(value => value !== undefined);
      if (legacySaved !== undefined) setState(legacySaved);
    } catch {
      // Keep the existing state when saved values cannot be parsed.
    }
  }, [key, legacyKeySignature]);

  useEffect(() => {
    try {
      if (state === undefined || state === null) {
        localStorage.removeItem(key);
      } else {
        localStorage.setItem(key, JSON.stringify(state));
      }
    } catch (err) {
      console.error(`Failed to save state for ${key}`, err);
    }
  }, [key, state]);

  return [state, setState];
}

function readSavedSet(key: string) {
  const saved = localStorage.getItem(key);
  if (!saved) return null;

  const parsed = JSON.parse(saved);
  return Array.isArray(parsed) ? new Set(parsed) : null;
}

export function useLocalStorageSet<T>(
  key: string,
  defaultValue: Set<T> = new Set(),
  legacyKeys: string[] = []
): [Set<T>, React.Dispatch<React.SetStateAction<Set<T>>>] {
  const legacyKeySignature = legacyKeys.join("|");
  const [setValue, setSetValue] = useState(() => {
    try {
      return readSavedSet(key)
        ?? legacyKeys.map(readSavedSet).find(Boolean)
        ?? defaultValue;
    } catch (err) {
      console.error(`Failed to parse saved set for ${key}`, err);
      return defaultValue;
    }
  });

  useEffect(() => {
    try {
      const fallbackKeys = legacyKeySignature ? legacyKeySignature.split("|") : [];
      const saved = readSavedSet(key)
        ?? fallbackKeys.map(readSavedSet).find(Boolean);
      if (saved) setSetValue(saved);
    } catch (err) {
      console.error(`Failed to parse saved set for ${key}`, err);
    }
  }, [key, legacyKeySignature]);

  useEffect(() => {
    try {
      if (setValue.size > 0) {
        localStorage.setItem(key, JSON.stringify([...setValue]));
      } else {
        localStorage.removeItem(key);
      }
    } catch (err) {
      console.error(`Failed to save set for ${key}`, err);
    }
  }, [key, setValue]);

  return [setValue, setSetValue];
}
