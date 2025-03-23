"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useScroll, useTransform, useInView } from "framer-motion";
import { Scale, Gavel, BookOpen, FileText, ArrowRight, ChevronDown, Star, Shield, Database, Brain, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ParticlesBackground } from "@/components/particles-background";
import { TestimonialScroller, testimonialData } from "@/components/testimonial-scroller";
import Link from "next/link";
import { AnimatePresence } from "framer-motion";
import LawDerFocus from "@/components/law-der-focus";
import { useSplash } from "@/components/splash-context";

export default function Home() {
  const scrollRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: scrollRef,
    offset: ["start start", "end start"]
  });
  
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.8]);
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 100]);
  
  const statsRef = useRef(null);
  const isStatsInView = useInView(statsRef, { once: true, amount: 0.3 });
  
  const testimonialRef = useRef(null);
  const isTestimonialInView = useInView(testimonialRef, { once: true, amount: 0.3 });

  const features = [
    {
      icon: Brain,
      title: "AI Assistant",
      description: "Your 24/7 legal companion powered by advanced AI technology. Get instant answers to legal questions and personalized guidance for your specific situation.",
      tagline: "Justice never sleeps, neither does our AI"
    },
    {
      icon: FileText,
      title: "Document Manager",
      description: "Intelligent document analysis and management system that helps you organize, understand, and generate legal documents with ease.",
      tagline: "The paper chase ends here"
    },
    {
      icon: Database,
      title: "Law Case Database",
      description: "Comprehensive repository of legal precedents and case histories, searchable by relevance to your specific legal questions and concerns.",
      tagline: "Order in the digital court"
    },
    {
      icon: Globe,
      title: "Law Blog",
      description: "Latest insights from legal experts across various domains, keeping you informed about changes and developments in the legal landscape.",
      tagline: "Where law meets clarity"
    }
  ];
  
  const stats = [
    { value: "30K+", label: "Legal Documents Generated" },
    { value: "XX%", label: "User Satisfaction" },
    { value: "XXK+", label: "Legal Questions Answered" },
    { value: "24/7", label: "AI Availability" }
  ];

  const { splashFinished } = useSplash();
  const [showHero, setShowHero] = useState(false);
  
  useEffect(() => {
    if (splashFinished) {
      // Slight delay to ensure smooth transition
      const timer = setTimeout(() => {
        setShowHero(true);
      }, 300);
      
      return () => clearTimeout(timer);
    }
  }, [splashFinished]);

  return (
    <main className="flex flex-col items-center">
      {/* Hero section - increased top padding to push content down */}
      <section className="w-full flex flex-col items-center justify-start text-center px-4 pt-40 md:pt-48 pb-16">
        <div className="absolute inset-0 -z-10">
          <ParticlesBackground />
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.08 }}
            transition={{ duration: 1.5 }}
            className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1589994965851-a8f479c573a9?q=80&w=2000')] bg-cover bg-center"
          />
        </div>
        
        <AnimatePresence>
          {showHero && (
            <>
              {/* LAW-DER heading */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
                className="mb-6"
              >
                <motion.h1 
                  className="text-6xl md:text-8xl font-bold tracking-tight"
                  animate={{ 
                    textShadow: ['0 0 0px rgba(var(--primary), 0)', '0 0 20px rgba(var(--primary), 0.3)', '0 0 0px rgba(var(--primary), 0)'] 
                  }}
                  transition={{ 
                    duration: 3, 
                    repeat: Infinity, 
                    repeatType: "reverse" 
                  }}
                >
                  <span className="text-primary">LAW</span>
                  <span className="text-primary/80">-</span>
                  <span className="text-primary">DER</span>
                </motion.h1>
              </motion.div>
              
              {/* Tagline - increased spacing below */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1, delay: 0.4 }}
                className="text-xl md:text-2xl text-muted-foreground mb-16"
              >
                LAW AND ORDER JUST GOT LOUDER
              </motion.p>

              {/* Mission statement - adjusted spacing */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1, delay: 0.8 }}
                className="text-lg text-muted-foreground/90 max-w-3xl mb-16"
              >
                Democratizing legal assistance through AI-powered solutions. Equal access to justice is not just a promise—it's our mission.
              </motion.p>
              
              {/* Action buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 1.2 }}
                className="flex flex-wrap gap-4 justify-center"
              >
                <a href="/get-started" className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-lg font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">
                  Get Started <span className="ml-2">→</span>
                </a>
                <a href="/cases" className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-lg font-medium shadow-sm hover:bg-accent hover:text-accent-foreground">
                  Explore Cases <span className="ml-2">📋</span>
                </a>
                <a href="/demo" className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-lg font-medium shadow-sm hover:bg-accent hover:text-accent-foreground">
                  Watch Demo <span className="ml-2">★</span>
                </a>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </section>

      {/* Stats Section */}
      <section id="stats-section" className="py-24 px-6 relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            ref={statsRef}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-10 text-center"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 30 }}
                animate={isStatsInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="relative p-6 rounded-lg bg-card/50 backdrop-blur-sm border border-border/30 overflow-hidden group"
              >
                <div className="absolute -right-10 -top-10 w-20 h-20 bg-primary/5 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                <div className="absolute -left-5 -bottom-5 w-10 h-10 bg-primary/5 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                <motion.p 
                  className="text-4xl font-bold text-primary"
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={isStatsInView ? { opacity: 1, scale: 1 } : {}}
                  transition={{ duration: 0.5, delay: index * 0.1 + 0.2 }}
                >
                  {stat.value}
                </motion.p>
                <p className="text-muted-foreground mt-2">{stat.label}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features-section" className="py-20 px-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-background/0 via-background/50 to-background/0 pointer-events-none"></div>
        
        <div className="max-w-7xl mx-auto mb-16 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Our Powerful Features</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Designed to make legal assistance accessible, affordable, and efficient for everyone. 
              Experience the future of legal technology with our innovative tools.
            </p>
          </motion.div>
        </div>
        
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ y: 50, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="relative group h-full"
            >
              <div className="bg-card/80 backdrop-blur-sm p-8 rounded-lg border border-border/50 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5 h-full flex flex-col">
                <div className="bg-primary/10 rounded-full p-3 w-16 h-16 flex items-center justify-center mb-6">
                  <feature.icon className="w-8 h-8 text-primary" />
                </div>
                
                <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground mb-10">{feature.description}</p>
                
                <div className="mt-auto">
                  <p className="text-sm italic text-primary">{feature.tagline}</p>
                  
                  <div className="mt-4 flex items-center text-primary/80 text-sm font-medium group-hover:text-primary transition-colors">
                    <span>Learn more</span>
                    <ArrowRight className="ml-2 h-3 w-3 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
      
      {/* Testimonials Section */}
      <section id="testimonials-section" ref={testimonialRef} className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-primary/5 pointer-events-none"></div>
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="max-w-5xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isTestimonialInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">What Our Users Say</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Hear from the people who have experienced the power of LAW-DER in their legal journey.
            </p>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isTestimonialInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5 }}
          >
            <TestimonialScroller testimonials={testimonialData} scrollDuration={6000} />
          </motion.div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section id="cta-section" className="py-24 px-6 relative overflow-hidden">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7 }}
          className="max-w-4xl mx-auto text-center bg-card/90 backdrop-blur-lg p-10 rounded-2xl border border-border/50 shadow-xl"
        >
          <Shield className="w-16 h-16 text-primary mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to transform your legal experience?</h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of individuals and businesses who are already benefiting from LAW-DER's innovative legal technology platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-primary text-primary-foreground group" asChild>
              <Link href="/get-started">
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
            <Button size="lg" variant="outline">
              Schedule a Demo
            </Button>
          </div>
        </motion.div>
      </section>
      
      {/* Footer */}
      <footer className="bg-background/90 border-t border-border/40 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
            <div>
              <Link href="/" className="flex items-center space-x-2 mb-4">
                <Scale className="h-6 w-6 text-primary" />
                <span className="text-lg font-bold">LAW-DER</span>
              </Link>
              <p className="text-sm text-muted-foreground">
                Making justice accessible through technology
              </p>
              <div className="mt-4 flex space-x-4">
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951z"/>
                  </svg>
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
                  </svg>
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/>
                  </svg>
                </Button>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-4">Features</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-primary transition-colors">AI Assistant</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Document Manager</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Case Database</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Law Blog</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/about" className="hover:text-primary transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Careers</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium mb-4">Contact</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>123 Legal Avenue</li>
                <li>Justice City, JC 10101</li>
                <li>info@lawder.com</li>
                <li>(555) 123-4567</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-10 pt-6 border-t border-border/20 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-muted-foreground">
              © 2025z LAW-DER. All rights reserved.
            </p>
            <div className="mt-4 md:mt-0">
              <ul className="flex space-x-4 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-primary transition-colors">Privacy</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Terms</Link></li>
                <li><Link href="#" className="hover:text-primary transition-colors">Cookies</Link></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}