"use client";

import { useCallback, useEffect, useState } from "react";
import Particles from "react-particles";
import type { Engine } from "tsparticles-engine";
import { loadSlim } from "tsparticles-slim";
import { useTheme } from "next-themes";

export function ParticlesBackground() {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const particlesInit = useCallback(async (engine: Engine) => {
    await loadSlim(engine);
  }, []);

  const isDarkTheme = mounted && (theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches));

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        background: {
          color: {
            value: "transparent",
          },
        },
        fpsLimit: 120,
        interactivity: {
          events: {
            onClick: {
              enable: true,
              mode: "push",
            },
            onHover: {
              enable: true,
              mode: "repulse",
              parallax: {
                enable: true,
                force: 60,
                smooth: 10
              }
            },
            resize: true,
          },
          modes: {
            push: {
              quantity: 4,
            },
            repulse: {
              distance: 150,
              duration: 0.4,
            },
            grab: {
              distance: 200,
              links: {
                opacity: 0.5
              }
            }
          },
        },
        particles: {
          color: {
            value: isDarkTheme ? ["#4f46e5", "#818cf8", "#6366f1", "#a78bfa"] : ["#4f46e5", "#6366f1", "#3730a3", "#4338ca"],
          },
          links: {
            color: isDarkTheme ? "#6366f1" : "#4f46e5",
            distance: 150,
            enable: true,
            opacity: 0.3,
            width: 1,
            triangles: {
              enable: true,
              opacity: 0.05
            }
          },
          collisions: {
            enable: true,
          },
          move: {
            direction: "none",
            enable: true,
            outModes: {
              default: "bounce",
            },
            random: true,
            speed: 1.5,
            straight: false,
            attract: {
              enable: false,
              rotateX: 600,
              rotateY: 1200
            }
          },
          number: {
            density: {
              enable: true,
              area: 800,
            },
            value: 80,
            max: 90,
          },
          opacity: {
            value: {
              min: 0.1,
              max: 0.4
            },
            animation: {
              enable: true,
              speed: 0.3,
              sync: false
            }
          },
          shape: {
            type: ["circle", "triangle", "polygon"],
            options: {
              polygon: {
                sides: 5
              }
            }
          },
          size: {
            value: { min: 1, max: 4 },
            animation: {
              enable: true,
              speed: 2,
              minimumValue: 0.5,
              sync: false
            }
          },
          twinkle: {
            lines: {
              enable: true,
              frequency: 0.005,
              opacity: 0.3,
              color: {
                value: isDarkTheme ? "#a78bfa" : "#6366f1"
              }
            },
            particles: {
              enable: true,
              frequency: 0.01,
              opacity: 0.7,
              color: {
                value: isDarkTheme ? "#818cf8" : "#4f46e5"
              }
            }
          }
        },
        detectRetina: true,
      }}
    />
  );
}