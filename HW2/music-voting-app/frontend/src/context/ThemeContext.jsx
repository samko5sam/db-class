import React, { createContext, useState, useEffect } from "react";

// 1. Create the context
export const ThemeContext = createContext();

// 2. Create the provider component
export const ThemeProvider = ({ children }) => {
  // 3. State to hold the current theme. Initialize from localStorage or default to 'light'.
  const [theme, setTheme] = useState(
    () => localStorage.getItem("theme") || "light",
  );

  // 4. Effect to apply the theme to the <html> element whenever the theme state changes.
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // 5. Function to toggle the theme
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
    location.reload();
  };

  // 6. Provide the theme and the toggle function to children
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
