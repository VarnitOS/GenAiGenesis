"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Scale } from "lucide-react";

const quotes = [
  {
    quote: "When you're backed against the wall, break the goddamn thing down.",
    author: "Harvey Specter"
  },
  {
    quote: "I don't play the odds, I play the man.",
    author: "Harvey Specter"
  },
  {
    quote: "It's going to happen, because I am going to make it happen.",
    author: "Harvey Specter"
  },
  {
    quote: "I don't have dreams, I have goals.",
    author: "Harvey Specter"
  },
  {
    quote: "Winners don't make excuses when the other side plays the game.",
    author: "Harvey Specter"
  }
];

export const SplashScreen = () => {
  const [visible, setVisible] = useState(true);
  const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];

  useEffect(() => {
    // Hide splash screen after 3 seconds
    const timer = setTimeout(() => {
      setVisible(false);
    }, 3000);

    // Add no-scroll class to body
    document.body.classList.add("overflow-hidden");

    return () => {
      clearTimeout(timer);
      document.body.classList.remove("overflow-hidden");
    };
  }, []);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8 }}
          className="fixed inset-0 bg-background z-50 flex flex-col items-center justify-center"
        >
          <div className="max-w-lg px-6 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
              className="mx-auto mb-8 relative"
            >
              <div className="bg-primary/10 rounded-full p-5 w-28 h-28 flex items-center justify-center">
                <Scale className="h-14 w-14 text-primary" />
              </div>
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5, duration: 0.5 }}
                className="absolute -right-2 -top-2 bg-primary text-white text-xs font-bold rounded-full h-8 w-8 flex items-center justify-center"
              >
                AI
              </motion.div>
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-4xl font-bold mb-2"
            >
              LAW-DER
            </motion.h1>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.5 }}
              className="mb-10"
            >
              <p className="text-muted-foreground text-lg">Legal Assistance Without Delay, Every Resolution</p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1, duration: 0.5 }}
              className="bg-card/30 backdrop-blur-sm p-6 rounded-xl border border-border/50 mb-6"
            >
              <blockquote className="italic text-xl text-primary-foreground mb-4">&ldquo;{randomQuote.quote}&rdquo;</blockquote>
              <cite className="text-sm text-muted-foreground block text-right">— {randomQuote.author}, <span className="opacity-70">Suits</span></cite>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5, duration: 0.5 }}
              className="flex justify-center"
            >
              <motion.div
                animate={{ 
                  y: [0, -8, 0],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{ 
                  duration: 1.5,
                  repeat: Infinity,
                  repeatType: "loop"
                }}
                className="text-primary text-sm"
              >
                Loading your experience...
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}; 