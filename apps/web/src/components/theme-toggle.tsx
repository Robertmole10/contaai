'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button
        className="icon-button"
        type="button"
        aria-label="Se încarcă tema"
      >
        <Moon size={19} />
      </button>
    );
  }

  const isDark = resolvedTheme === 'dark';

  return (
    <button
      className="icon-button"
      type="button"
      aria-label={isDark ? 'Activează tema luminoasă' : 'Activează tema întunecată'}
      title={isDark ? 'Temă luminoasă' : 'Temă întunecată'}
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
    >
      {isDark ? <Sun size={19} /> : <Moon size={19} />}
    </button>
  );
}
