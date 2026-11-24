import { useEffect, useState } from "react";

type Theme = "dark" | "light";

function savedTheme(): Theme {
  return localStorage.getItem("theme") === "light" ? "light" : "dark";
}

/** Dark by default; the choice is saved so it holds on the next visit. */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(savedTheme);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);
  return {
    theme,
    toggle: () => {
      setTheme(theme === "dark" ? "light" : "dark");
    },
  };
}
