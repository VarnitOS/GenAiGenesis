"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

interface FocusRect {
    x: number;
    y: number;
    width: number;
    height: number;
}

const LawDerFocus = ({
    borderColor = "rgb(var(--primary))",
    glowColor = "rgba(var(--primary), 0.6)",
    blurAmount = 3,
    animationDuration = 0.8,
    pauseBetweenAnimations = 2,
}) => {
    const [currentIndex, setCurrentIndex] = useState<number>(0);
    const containerRef = useRef<HTMLDivElement | null>(null);
    const wordRefs = useRef<(HTMLSpanElement | null)[]>([null, null]);
    const [focusRect, setFocusRect] = useState<FocusRect>({ x: 0, y: 0, width: 0, height: 0 });

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % 2);
        }, (animationDuration + pauseBetweenAnimations) * 1000);

        return () => clearInterval(interval);
    }, [animationDuration, pauseBetweenAnimations]);

    useEffect(() => {
        if (!wordRefs.current[currentIndex] || !containerRef.current) return;

        const parentRect = containerRef.current.getBoundingClientRect();
        const activeRect = wordRefs.current[currentIndex]!.getBoundingClientRect();

        setFocusRect({
            x: activeRect.left - parentRect.left,
            y: activeRect.top - parentRect.top,
            width: activeRect.width,
            height: activeRect.height,
        });
    }, [currentIndex]);

    return (
        <div
            className="relative flex gap-2 justify-center items-center"
            ref={containerRef}
        >
            <span
                ref={(el) => (wordRefs.current[0] = el)}
                className="relative text-[3rem] font-black cursor-pointer"
                style={{
                    filter: currentIndex === 0 ? `blur(0px)` : `blur(${blurAmount}px)`,
                    transition: `filter ${animationDuration}s ease`,
                }}
            >
                LAW
            </span>
            
            <span className="text-[3rem] font-black">-</span>
            
            <span
                ref={(el) => (wordRefs.current[1] = el)}
                className="relative text-[3rem] font-black cursor-pointer"
                style={{
                    filter: currentIndex === 1 ? `blur(0px)` : `blur(${blurAmount}px)`,
                    transition: `filter ${animationDuration}s ease`,
                }}
            >
                DER
            </span>
        </div>
    );
};

export default LawDerFocus; 