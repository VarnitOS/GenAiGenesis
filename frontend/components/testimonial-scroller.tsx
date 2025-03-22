"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Quote } from "lucide-react";

interface Testimonial {
  id: number;
  name: string;
  role: string;
  content: string;
  avatar?: string;
}

interface TestimonialScrollerProps {
  testimonials: Testimonial[];
  autoScroll?: boolean;
  scrollDuration?: number;
}

export const TestimonialScroller = ({
  testimonials,
  autoScroll = true,
  scrollDuration = 5000
}: TestimonialScrollerProps) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  
  useEffect(() => {
    if (!autoScroll || isHovered) return;
    
    const interval = setInterval(() => {
      setActiveIndex((current) => (current + 1) % testimonials.length);
    }, scrollDuration);
    
    return () => clearInterval(interval);
  }, [autoScroll, isHovered, testimonials.length, scrollDuration]);
  
  return (
    <div 
      className="relative overflow-hidden bg-card/80 backdrop-blur-sm border border-border/50 rounded-xl shadow-lg"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="absolute top-6 left-6 text-primary/20 -z-0">
        <Quote className="h-24 w-24" />
      </div>
      
      <div className="flex justify-between items-center p-4 border-b border-border/50 bg-background/50">
        <h3 className="text-xl font-semibold">Client Testimonials</h3>
        <div className="flex space-x-2">
          {testimonials.map((_, index) => (
            <button
              key={index}
              onClick={() => setActiveIndex(index)}
              className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
                index === activeIndex ? "bg-primary scale-125" : "bg-border hover:bg-primary/50"
              }`}
              aria-label={`View testimonial ${index + 1}`}
            />
          ))}
        </div>
      </div>
      
      <div className="p-6 h-[340px] relative">
        <div className="h-full">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, x: index > activeIndex ? 100 : -100 }}
              animate={{ 
                opacity: index === activeIndex ? 1 : 0,
                x: index === activeIndex ? 0 : index > activeIndex ? 100 : -100,
                position: index === activeIndex ? "relative" : "absolute"
              }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className={`h-full w-full flex flex-col justify-between ${
                index === activeIndex ? "" : "pointer-events-none absolute inset-0"
              }`}
            >
              <div>
                <div className="flex items-center space-x-4 mb-6">
                  <div className="relative">
                    <div className="w-14 h-14 bg-primary/10 rounded-full flex items-center justify-center overflow-hidden">
                      {testimonial.avatar ? (
                        <img 
                          src={testimonial.avatar} 
                          alt={testimonial.name} 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <span className="text-2xl">{testimonial.name.charAt(0)}</span>
                      )}
                    </div>
                    <motion.div 
                      className="absolute -inset-1 rounded-full border-2 border-primary/30"
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
                
                <motion.blockquote 
                  className="italic text-lg text-muted-foreground"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  "{testimonial.content}"
                </motion.blockquote>
              </div>
              
              <motion.div 
                className="mt-6 flex items-center justify-end"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <div className="h-1 bg-primary/30 w-16 rounded-full mr-2" />
                <p className="text-sm text-primary">{index + 1} of {testimonials.length}</p>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 w-full">
        <motion.div 
          className="h-1 bg-primary/50"
          initial={{ width: "0%" }}
          animate={{ width: isHovered ? "0%" : "100%" }}
          transition={{ duration: scrollDuration / 1000, ease: "linear", repeat: isHovered ? 0 : Infinity }}
        />
      </div>
    </div>
  );
};

export const testimonialData = [
  {
    id: 1,
    name: "Sarah Johnson",
    role: "Small Business Owner",
    content: "LAW-DER transformed how I handle legal matters for my business. Their AI-powered assistance guided me through complex compliance issues that would have cost thousands in legal fees. The interface is intuitive, and the advice is surprisingly comprehensive. It's like having a legal advisor available 24/7.",
    avatar: "https://randomuser.me/api/portraits/women/32.jpg"
  },
  {
    id: 2,
    name: "Michael Chen",
    role: "Tenant Rights Advocate",
    content: "I've referred dozens of tenants to LAW-DER when they couldn't afford traditional legal help. The platform breaks down housing laws in plain language and provides actionable steps. It's empowering to see people successfully defend their rights using this technology. A true game-changer for accessibility to justice.",
    avatar: "https://randomuser.me/api/portraits/men/22.jpg"
  },
  {
    id: 3,
    name: "Priya Patel",
    role: "Immigration Applicant",
    content: "Navigating the immigration process seemed impossible until I found LAW-DER. The platform helped me understand my options, prepare the right documents, and avoid costly mistakes. Their step-by-step guidance made a complex legal journey manageable. I'm now a permanent resident thanks to their assistance!",
    avatar: "https://randomuser.me/api/portraits/women/45.jpg"
  },
  {
    id: 4,
    name: "James Wilson",
    role: "Recent Divorcee",
    content: "During my divorce, I couldn't afford full-time legal representation. LAW-DER filled that gap perfectly, helping me understand my rights and prepare for mediation sessions. The platform's document review saved me from making several critical errors in my agreements. I felt empowered rather than intimidated by the legal process.",
    avatar: "https://randomuser.me/api/portraits/men/44.jpg"
  },
  {
    id: 5,
    name: "Elena Rodriguez",
    role: "Community Organizer",
    content: "LAW-DER has been instrumental for our nonprofit's advocacy work. We use it to educate community members about their legal rights in multiple languages. The AI's ability to simplify complex legal concepts while remaining accurate is remarkable. It's democratizing legal knowledge in ways I never thought possible.",
    avatar: "https://randomuser.me/api/portraits/women/68.jpg"
  },
  {
    id: 6,
    name: "David Okafor",
    role: "Tech Startup Founder",
    content: "As a startup founder, legal expenses were a major concern. LAW-DER helped us with everything from drafting contracts to navigating IP protection. The platform's document builder saved us at least $15,000 in legal fees during our first year. It's been an essential tool for our growth and compliance strategy.",
    avatar: "https://randomuser.me/api/portraits/men/67.jpg"
  },
  {
    id: 7,
    name: "Sophia Kim",
    role: "Law Student",
    content: "I started using LAW-DER during my first year of law school, and it's been an incredible learning tool. The case database and explanations help me understand legal precedents better than some textbooks. I even landed my internship by demonstrating knowledge I gained through the platform. Every law student should use this!",
    avatar: "https://randomuser.me/api/portraits/women/90.jpg"
  }
]; 