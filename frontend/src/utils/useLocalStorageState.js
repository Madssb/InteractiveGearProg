import { useEffect, useState } from 'react';

export function useLocalStorageState(key, defaultValue) {
  const [state, setState] = useState(() => {
    try {
      const saved = localStorage.getItem(key);
      return saved !== null ? JSON.parse(saved) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

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







export function useLocalStorageSet(key, defaultValue = new Set()) {
  const [setValue, setSetValue] = useState(defaultValue);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          setSetValue(new Set(parsed));
        }
      }
    } catch (err) {
      console.error(`Failed to parse saved set for ${key}`, err);
    }
  }, [key]);

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