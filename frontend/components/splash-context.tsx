"use client";

import { createContext, useState, useContext, ReactNode } from "react";

interface SplashContextType {
  splashFinished: boolean;
  setSplashFinished: (value: boolean) => void;
}

const SplashContext = createContext<SplashContextType | undefined>(undefined);

export const SplashProvider = ({ children }: { children: ReactNode }) => {
  const [splashFinished, setSplashFinished] = useState(false);

  return (
    <SplashContext.Provider value={{ splashFinished, setSplashFinished }}>
      {children}
    </SplashContext.Provider>
  );
};

export const useSplash = () => {
  const context = useContext(SplashContext);
  if (context === undefined) {
    throw new Error("useSplash must be used within a SplashProvider");
  }
  return context;
}; 