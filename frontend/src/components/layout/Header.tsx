"use client";
import React from "react";
import { Moon, Sun, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  const [darkMode, setDarkMode] = React.useState(false);
  React.useEffect(() => { setDarkMode(document.documentElement.classList.contains("dark")); }, []);
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    if (newMode) { document.documentElement.classList.add("dark"); localStorage.setItem("theme", "dark"); }
    else { document.documentElement.classList.remove("dark"); localStorage.setItem("theme", "light"); }
  };
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-card px-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground">AI Job Recommendation System</h2>
        <p className="text-xs text-muted-foreground">Powered by NLP, TF-IDF, and Semantic Embeddings</p>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
          {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
        <div className="ml-2 h-8 w-8 rounded-full bg-primary flex items-center justify-center">
          <span className="text-sm font-bold text-primary-foreground">U</span>
        </div>
      </div>
    </header>
  );
}
