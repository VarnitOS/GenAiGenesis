"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSplash } from "./splash-context";

export const SplashScreen = () => {
  const [visible, setVisible] = useState(true);
  const [wordIndex, setWordIndex] = useState(0);
  const [exitStarted, setExitStarted] = useState(false);
  const { setSplashFinished } = useSplash();
  
  const words = ["Legislature", "Executive", "Judiciary"];

  useEffect(() => {
    // Hide the navbar when splash screen is active
    document.body.classList.add("splash-active");
    
    // Words animation timing
    const wordTimers = [
      setTimeout(() => setWordIndex(1), 2000),
      setTimeout(() => setWordIndex(2), 4000),
      setTimeout(() => {
        // Start final transition animation
        setExitStarted(true);
        
        setTimeout(() => {
          setVisible(false);
          document.body.classList.remove("splash-active");
          setSplashFinished(true);
        }, 1200);
      }, 6000)
    ];

    // Prevent scrolling during splash screen
    document.body.classList.add("overflow-hidden");

    return () => {
      wordTimers.forEach(clearTimeout);
      document.body.classList.remove("overflow-hidden");
      document.body.classList.remove("splash-active");
    };
  }, [setSplashFinished]);

  // New smooth animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.04, delayChildren: 0.1 } },
    exit: { 
      opacity: 0, 
      transition: { 
        staggerChildren: 0.02, 
        staggerDirection: -1,
        when: "afterChildren" 
      } 
    }
  };

  const letterVariants = {
    hidden: { 
      opacity: 0,
      y: 10,
      scale: 0.95
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: { 
        type: "spring",
        damping: 12,
        stiffness: 100
      }
    },
    exit: { 
      opacity: 0,
      y: -10,
      transition: { 
        duration: 0.2,
        ease: "easeInOut"
      }
    }
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1 }}
          className="fixed inset-0 z-[9999] flex items-center justify-center overflow-hidden bg-background"
        >
          {/* Background with stronger opacity */}
          <motion.div 
            className="absolute inset-0 bg-background"
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
          />
          
          {/* Gradient with increased opacity */}
          <motion.div 
            className="absolute inset-0 bg-gradient-radial from-primary/20 to-transparent"
            animate={{ 
              scale: [1, 1.1, 1],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              repeatType: "reverse"
            }}
          />
          
          {/* Animated lines in background */}
          <div className="absolute inset-0 overflow-hidden opacity-30">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={`line-${i}`}
                className="absolute h-px bg-primary"
                style={{
                  top: `${20 + i * 15}%`,
                  left: 0,
                  right: 0,
                }}
                initial={{ scaleX: 0, originX: i % 2 === 0 ? 0 : 1 }}
                animate={{ scaleX: 1 }}
                transition={{
                  duration: 2.5 + i * 0.4,
                  delay: 0.2 * i,
                  ease: [0.22, 1, 0.36, 1],
                }}
              />
            ))}
          </div>
          
          {/* Words animation with smooth transitions */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-full max-w-4xl px-6 relative flex items-center justify-center">
              <AnimatePresence mode="wait">
                {words.map((word, index) => (
                  wordIndex === index && (
                    <motion.div
                      key={word}
                      className="relative text-center py-12"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.4 }}
                    >
                      {/* Top decorative accent */}
                      <motion.div
                        className="absolute top-0 left-1/2 transform -translate-x-1/2"
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "50%" }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.8 }}
                      >
                        <div className="h-0.5 bg-gradient-to-r from-transparent via-primary/60 to-transparent" />
                      </motion.div>
                      
                      {/* Animated word with smooth letter animations */}
                      <motion.div
                        className="flex justify-center overflow-hidden py-8"
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        exit="exit"
                      >
                        {word.split("").map((letter, i) => (
                          <motion.span
                            key={`${letter}-${i}`}
                            variants={letterVariants}
                            className={`text-7xl tracking-wider font-extralight inline-block mx-[2px] text-primary ${
                              index === 0 ? 'font-light' : ''
                            }`}
                            style={index === 0 ? { 
                              textShadow: '0 0 12px rgba(var(--primary), 0.5)' 
                            } : {}}
                          >
                            {letter === " " ? "\u00A0" : letter}
                          </motion.span>
                        ))}
                      </motion.div>
                      
                      {/* Bottom decorative accent */}
                      <motion.div
                        className="absolute bottom-0 left-1/2 transform -translate-x-1/2"
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "50%" }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.8 }}
                      >
                        <div className="h-0.5 bg-gradient-to-r from-transparent via-primary/60 to-transparent" />
                      </motion.div>
                    </motion.div>
                  )
                ))}
              </AnimatePresence>
            </div>
          </div>
          
          {/* Subtle glow effect */}
          <motion.div 
            className="absolute inset-0 opacity-20"
            style={{
              background: "radial-gradient(circle at center, rgba(var(--primary), 0.2) 0%, transparent 70%)",
              backgroundSize: "150% 150%",
            }}
            animate={{
              backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
            }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}; 