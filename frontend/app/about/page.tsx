"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useInView, useScroll, useTransform, AnimatePresence } from "framer-motion";
import { Users, Scale, Gavel, Target, Award, Clock, ArrowRight, ChevronDown, Star, Shield, BookOpen, Heart, Brain, Lightbulb } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ParticlesBackground } from "@/components/particles-background";

export default function AboutPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [activeMissionSection, setActiveMissionSection] = useState(0);
  const [activeVisionSection, setActiveVisionSection] = useState(0);
  const [hoveredObjective, setHoveredObjective] = useState<number | null>(null);
  
  const contentRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: contentRef });
  const scaleProgress = useTransform(scrollYProgress, [0, 1], [0.8, 1]);
  const opacityProgress = useTransform(scrollYProgress, [0, 0.3], [0.6, 1]);
  
  const missionRef = useRef(null);
  const visionRef = useRef(null);
  const objectivesRef = useRef(null);
  const servicesRef = useRef(null);
  const teamRef = useRef(null);
  
  const missionInView = useInView(missionRef, { once: false, amount: 0.3 });
  const visionInView = useInView(visionRef, { once: false, amount: 0.3 });
  const objectivesInView = useInView(objectivesRef, { once: false, amount: 0.3 });
  const servicesInView = useInView(servicesRef, { once: false, amount: 0.3 });
  const teamInView = useInView(teamRef, { once: false, amount: 0.3 });
  
  // Auto-rotate mission sections
  useEffect(() => {
    if (!missionInView) return;
    
    const interval = setInterval(() => {
      setActiveMissionSection((prev) => (prev + 1) % 3);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [missionInView]);
  
  // Auto-rotate vision sections
  useEffect(() => {
    if (!visionInView) return;
    
    const interval = setInterval(() => {
      setActiveVisionSection((prev) => (prev + 1) % 3);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [visionInView]);
  
  const staggerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };
  
  const cardVariants = {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
    hover: { 
      scale: 1.03, 
      boxShadow: "0 20px 30px rgba(0, 0, 0, 0.15)",
      borderColor: "rgba(var(--primary), 0.5)"
    }
  };
  
  const objectives = [
    { 
      icon: Award, 
      title: "Legal Literacy",
      text: "Enhance legal literacy by providing accessible educational resources.",
      color: "from-blue-500/20 to-blue-700/20"
    },
    { 
      icon: Clock, 
      title: "Real-time Assistance",
      text: "Leverage AI to offer real-time, affordable legal assistance.",
      color: "from-purple-500/20 to-purple-700/20"
    },
    { 
      icon: Target, 
      title: "Equal Access",
      text: "Break socioeconomic barriers by prioritizing underserved communities.",
      color: "from-green-500/20 to-green-700/20"
    },
    { 
      icon: Scale, 
      title: "Improved Accessibility",
      text: "Continuously expand and refine our legal database for better accessibility.",
      color: "from-amber-500/20 to-amber-700/20"
    },
    { 
      icon: Gavel, 
      title: "Diversity & Inclusion",
      text: "Advocate for diversity, equity, and inclusion within the legal landscape.",
      color: "from-rose-500/20 to-rose-700/20"
    }
  ];

  const services = [
    { title: "24/7 AI-Powered Legal Assistance", description: "Instant, AI-driven legal guidance accessible anytime, anywhere." },
    { title: "Simplifying Legal Document Management", description: "Streamlining the creation, organization, and accessibility of legal documents." },
    { title: "Enhancing Legal Literacy & Awareness", description: "Sharing expert insights, educational resources, and updates through our blog." },
    { title: "Empowering Underserved Communities", description: "Prioritizing individuals from less favorable socioeconomic backgrounds to ensure fair access to legal resources." },
    { title: "Advancing Diversity, Equity & Inclusion", description: "Breaking down barriers in legal education and assistance to build a more just society." }
  ];
  
  const teamMembers = [
    { name: "Alexandra Chen", role: "Chief Legal AI Officer", bio: "Former Supreme Court clerk with expertise in AI and legal technology.", avatar: "👩‍⚖️" },
    { name: "Marcus Johnson", role: "Head of Legal Database", bio: "Former law professor specialized in legal documentation and research systems.", avatar: "👨‍💼" },
    { name: "Sophia Rodriguez", role: "Community Outreach Director", bio: "Dedicated to making legal resources accessible to underserved communities.", avatar: "👩‍💼" },
    { name: "David Kim", role: "Chief Technology Officer", bio: "AI specialist with a passion for using technology to solve social justice issues.", avatar: "👨‍💻" }
  ];
  
  const tabs = [
    { title: "Our Core Values", icon: Star },
    { title: "Our Approach", icon: Shield },
    { title: "Our Impact", icon: BookOpen }
  ];
  
  const tabContents = [
    {
      title: "Our Core Values",
      content: "At LAW-DER, we believe in justice for all. Our core values revolve around accessibility, integrity, innovation, and compassion. We strive to make legal assistance available to everyone, regardless of their background or financial status. Every decision we make is guided by these principles, ensuring that we remain true to our mission of democratizing legal assistance.",
      stats: [
        { value: "100%", label: "Commitment to Ethical AI" },
        { value: "24/7", label: "Availability" },
        { value: "100K+", label: "Lives Impacted" }
      ]
    },
    {
      title: "Our Approach",
      content: "We take a user-centered approach to legal assistance, combining cutting-edge AI technology with human expertise. Our platform is designed to be intuitive and accessible, breaking down complex legal concepts into understandable language. We continuously gather feedback from our users to improve our services and ensure that we're meeting their needs effectively.",
      stats: [
        { value: "5-min", label: "Average Response Time" },
        { value: "95%", label: "User Satisfaction" },
        { value: "50+", label: "Legal Categories Covered" }
      ]
    },
    {
      title: "Our Impact",
      content: "Since our inception, LAW-DER has helped thousands of individuals navigate legal challenges they otherwise couldn't afford to address. From helping tenants understand their rights to guiding small business owners through regulatory compliance, our impact spans across various demographics and legal domains. We're proud to be making a tangible difference in people's lives.",
      stats: [
        { value: "30K+", label: "Cases Assisted" },
        { value: "80%", label: "Cost Reduction" },
        { value: "40+", label: "Community Partners" }
      ]
    }
  ];
  
  const missionSections = [
    {
      title: "Equal Access to Justice",
      icon: Scale,
      color: "bg-gradient-to-br from-blue-500/20 to-blue-700/20",
      content: "LAW-DER is committed to democratizing legal assistance through cutting-edge AI technology while advancing legal literacy. We believe that everyone—regardless of their financial situation or background—deserves access to quality legal guidance."
    },
    {
      title: "Empowering Through Knowledge",
      icon: BookOpen,
      color: "bg-gradient-to-br from-purple-500/20 to-purple-700/20",
      content: "Legal knowledge should not be a privilege but a right, empowering individuals to navigate the complexities of the legal system with confidence. Our platform prioritizes those from less favorable socioeconomic backgrounds."
    },
    {
      title: "Technology for Good",
      icon: Heart,
      color: "bg-gradient-to-br from-rose-500/20 to-rose-700/20",
      content: "By leveraging AI, we break down barriers to legal education, promote fairness, and foster a more just and inclusive society where legal literacy is accessible to all."
    }
  ];
  
  const visionSections = [
    {
      title: "A World of Legal Equality",
      icon: Gavel,
      color: "bg-gradient-to-br from-green-500/20 to-green-700/20",
      content: "We envision a world where legal barriers no longer inhibit individuals from understanding and exercising their rights. A future where quality legal guidance is not a luxury but a standard."
    },
    {
      title: "AI-Powered Justice",
      icon: Brain,
      color: "bg-gradient-to-br from-amber-500/20 to-amber-700/20",
      content: "Our vision encompasses the seamless integration of AI in legal assistance, bridging gaps in accessibility, affordability, and efficiency. We see technology as the great equalizer in legal services."
    },
    {
      title: "Global Legal Literacy",
      icon: Lightbulb,
      color: "bg-gradient-to-br from-cyan-500/20 to-cyan-700/20",
      content: "We aspire to create a globally connected community where legal literacy is the norm, not the exception. We strive for a society where legal knowledge empowers individuals to navigate complexities with confidence."
    }
  ];

  const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
    ref.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-20 overflow-hidden">
      <div className="relative" ref={contentRef}>
        <div className="absolute inset-0 -z-10 opacity-5">
          <ParticlesBackground />
        </div>
        
        <motion.div
          style={{ scale: scaleProgress, opacity: opacityProgress }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="text-center mb-16"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
              className="bg-primary/10 rounded-full p-4 w-24 h-24 flex items-center justify-center mx-auto mb-6"
            >
              <Users className="h-12 w-12 text-primary" />
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80"
            >
              About Us
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto"
            >
              Making justice accessible through technology
            </motion.p>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-wrap justify-center gap-4 mt-8"
            >
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollToSection(missionRef)}
                className="group"
              >
                Mission <ChevronDown className="ml-1 h-4 w-4 group-hover:translate-y-1 transition-transform" />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollToSection(visionRef)}
                className="group"
              >
                Vision <ChevronDown className="ml-1 h-4 w-4 group-hover:translate-y-1 transition-transform" />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollToSection(objectivesRef)}
                className="group"
              >
                Objectives <ChevronDown className="ml-1 h-4 w-4 group-hover:translate-y-1 transition-transform" />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollToSection(servicesRef)}
                className="group"
              >
                Services <ChevronDown className="ml-1 h-4 w-4 group-hover:translate-y-1 transition-transform" />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => scrollToSection(teamRef)}
                className="group"
              >
                Team <ChevronDown className="ml-1 h-4 w-4 group-hover:translate-y-1 transition-transform" />
              </Button>
            </motion.div>
          </motion.div>

          {/* Mission Section */}
          <div className="mb-28" ref={missionRef}>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: missionInView ? 1 : 0, y: missionInView ? 0 : 30 }}
              transition={{ duration: 0.7 }}
              className="text-center mb-12"
            >
              <motion.h2 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: missionInView ? 1 : 0, scale: missionInView ? 1 : 0.9 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="text-4xl font-bold mb-4 inline-block bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/70"
              >
                Our Mission
              </motion.h2>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: missionInView ? "100px" : 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="h-1 bg-primary/40 mx-auto rounded-full"
              />
            </motion.div>
            
            <div className="relative py-8">
              {/* Animated background elements */}
              <motion.div 
                className="absolute inset-0 -z-10 overflow-hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: missionInView ? 0.5 : 0 }}
                transition={{ duration: 1 }}
              >
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={`mission-bg-${i}`}
                    className="absolute rounded-full bg-primary/5"
                    style={{
                      width: `${150 + i * 100}px`,
                      height: `${150 + i * 100}px`,
                      left: `${20 + (i % 3) * 25}%`,
                      top: `${30 + ((i + 1) % 3) * 20}%`,
                      transform: 'translate(-50%, -50%)',
                    }}
                    animate={{
                      scale: [1, 1.1, 1],
                      opacity: [0.1, 0.2, 0.1],
                      x: [0, i % 2 ? 10 : -10, 0],
                      y: [0, i % 3 ? -10 : 10, 0],
                    }}
                    transition={{
                      duration: 8 + i,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />
                ))}
              </motion.div>
              
              <div className="max-w-4xl mx-auto">
                <div className="flex justify-center mb-8 relative">
                  {missionSections.map((section, index) => (
                    <motion.button
                      key={`mission-tab-${index}`}
                      onClick={() => setActiveMissionSection(index)}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ 
                        opacity: missionInView ? 1 : 0, 
                        y: missionInView ? 0 : 20,
                        scale: activeMissionSection === index ? 1.05 : 1 
                      }}
                      transition={{ 
                        duration: 0.5, 
                        delay: 0.2 + index * 0.1 
                      }}
                      className={`px-4 py-2 mx-2 rounded-full transition-all duration-300 ${
                        activeMissionSection === index 
                          ? "bg-primary/20 text-primary shadow-lg" 
                          : "bg-card/50 text-muted-foreground hover:bg-primary/10"
                      }`}
                    >
                      {section.title}
                    </motion.button>
                  ))}
                </div>
                
                <div className="relative h-96">
                  <AnimatePresence mode="wait">
                    {missionSections.map((section, index) => (
                      activeMissionSection === index && (
                        <motion.div
                          key={`mission-content-${index}`}
                          initial={{ opacity: 0, x: 100 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -100 }}
                          transition={{ 
                            type: "spring", 
                            stiffness: 100, 
                            damping: 20 
                          }}
                          className="absolute inset-0 flex flex-col items-center"
                        >
                          <motion.div 
                            className={`${section.color} rounded-full p-6 w-32 h-32 flex items-center justify-center mb-8 shadow-lg`}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1, rotate: [0, 10, 0] }}
                            transition={{ 
                              duration: 0.7,
                              type: "spring",
                              stiffness: 200
                            }}
                          >
                            <section.icon className="h-16 w-16 text-primary" />
                          </motion.div>
                          
                          <motion.h3
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="text-3xl font-semibold mb-6 text-center"
                          >
                            {section.title}
                          </motion.h3>
                          
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: "60px" }}
                            transition={{ duration: 0.8, delay: 0.4 }}
                            className="h-1 bg-primary/30 mb-6 rounded-full"
                          />
                          
                          <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="text-xl text-center text-muted-foreground max-w-2xl leading-relaxed"
                          >
                            {section.content}
                          </motion.p>
                        </motion.div>
                      )
                    ))}
                  </AnimatePresence>
                </div>
                
                {/* Navigation dots */}
                <div className="flex justify-center mt-8">
                  {missionSections.map((_, index) => (
                    <motion.button
                      key={`mission-dot-${index}`}
                      onClick={() => setActiveMissionSection(index)}
                      className="mx-1 p-1"
                      whileHover={{ scale: 1.2 }}
                    >
                      <motion.div 
                        className={`w-3 h-3 rounded-full ${
                          activeMissionSection === index 
                            ? "bg-primary" 
                            : "bg-primary/30"
                        }`}
                        animate={{
                          scale: activeMissionSection === index ? [1, 1.2, 1] : 1
                        }}
                        transition={{
                          duration: 1.5,
                          repeat: activeMissionSection === index ? Infinity : 0,
                          repeatType: "reverse"
                        }}
                      />
                    </motion.button>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Vision Section */}
          <div className="mb-28" ref={visionRef}>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: visionInView ? 1 : 0, y: visionInView ? 0 : 30 }}
              transition={{ duration: 0.7 }}
          className="text-center mb-12"
        >
              <motion.h2 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: visionInView ? 1 : 0, scale: visionInView ? 1 : 0.9 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="text-4xl font-bold mb-4 inline-block bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/70"
              >
                Our Vision
              </motion.h2>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: visionInView ? "100px" : 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="h-1 bg-primary/40 mx-auto rounded-full"
              />
            </motion.div>
            
            <div className="max-w-4xl mx-auto relative py-8">
              {/* Animated background beam */}
              <motion.div
                className="absolute w-full h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent top-1/2 -translate-y-1/2 -z-10"
                initial={{ scaleX: 0 }}
                animate={{ scaleX: visionInView ? 1 : 0 }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
              
              <div className="relative h-[32rem]">
                <AnimatePresence mode="wait">
                  {visionSections.map((section, index) => (
                    activeVisionSection === index && (
                      <motion.div
                        key={`vision-card-${index}`}
                        initial={{ opacity: 0, rotateY: 90 }}
                        animate={{ opacity: 1, rotateY: 0 }}
                        exit={{ opacity: 0, rotateY: -90 }}
                        transition={{ 
                          type: "spring", 
                          stiffness: 70, 
                          damping: 20 
                        }}
                        style={{ 
                          transformStyle: "preserve-3d",
                          perspective: "1000px"
                        }}
                        className={`absolute inset-0 ${section.color} rounded-2xl border border-primary/10 shadow-xl backdrop-blur-sm p-8 flex flex-col items-center justify-center`}
                      >
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.3 }}
                          className="absolute -top-12 left-1/2 -translate-x-1/2 bg-primary/10 rounded-full p-5 shadow-lg"
                        >
                          <section.icon className="h-10 w-10 text-primary" />
        </motion.div>
                        
                        <motion.h3
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.4 }}
                          className="text-3xl font-semibold mb-6 text-center pt-8"
                        >
                          {section.title}
                        </motion.h3>

        <motion.div
                          className="w-16 h-1 bg-primary/30 mb-8 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: "4rem" }}
                          transition={{ duration: 0.8, delay: 0.5 }}
                        />
                        
                        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
                          transition={{ delay: 0.6 }}
                          className="text-xl text-center text-foreground/90 max-w-2xl leading-relaxed"
                        >
                          {section.content}
                        </motion.p>
                        
                        {/* Decorative elements */}
                        <motion.div
                          className="absolute top-10 right-10 w-24 h-24 rounded-full border border-primary/20 -z-10"
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 0.5 }}
                          transition={{ delay: 0.7, duration: 1 }}
                        />
                        
                        <motion.div
                          className="absolute bottom-10 left-10 w-16 h-16 rounded-full border border-primary/20 -z-10"
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 0.5 }}
                          transition={{ delay: 0.8, duration: 1 }}
                        />
                      </motion.div>
                    )
                  ))}
                </AnimatePresence>
                
                {/* Navigation arrows */}
                <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 flex justify-between pointer-events-none z-10">
                  <motion.button
                    className="w-12 h-12 rounded-full bg-background/80 flex items-center justify-center backdrop-blur-sm border border-border/50 shadow-lg pointer-events-auto"
                    whileHover={{ scale: 1.1, backgroundColor: "rgba(var(--primary), 0.2)" }}
                    onClick={() => setActiveVisionSection((prev) => (prev - 1 + visionSections.length) % visionSections.length)}
                  >
                    <ArrowRight className="h-5 w-5 text-primary rotate-180" />
                  </motion.button>
                  
                  <motion.button
                    className="w-12 h-12 rounded-full bg-background/80 flex items-center justify-center backdrop-blur-sm border border-border/50 shadow-lg pointer-events-auto"
                    whileHover={{ scale: 1.1, backgroundColor: "rgba(var(--primary), 0.2)" }}
                    onClick={() => setActiveVisionSection((prev) => (prev + 1) % visionSections.length)}
                  >
                    <ArrowRight className="h-5 w-5 text-primary" />
                  </motion.button>
                </div>
              </div>
              
              {/* Navigation dots */}
              <div className="flex justify-center mt-8">
                {visionSections.map((_, index) => (
                  <motion.button
                    key={`vision-dot-${index}`}
                    onClick={() => setActiveVisionSection(index)}
                    className="mx-1 p-1"
                    whileHover={{ scale: 1.2 }}
                  >
                    <motion.div 
                      className={`w-3 h-3 rounded-full ${
                        activeVisionSection === index 
                          ? "bg-primary" 
                          : "bg-primary/30"
                      }`}
                      animate={{
                        scale: activeVisionSection === index ? [1, 1.2, 1] : 1
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: activeVisionSection === index ? Infinity : 0,
                        repeatType: "reverse"
                      }}
                    />
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Objectives Section */}
          <div className="mb-28" ref={objectivesRef}>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: objectivesInView ? 1 : 0, y: objectivesInView ? 0 : 30 }}
              transition={{ duration: 0.7 }}
              className="text-center mb-12"
            >
              <motion.h2 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: objectivesInView ? 1 : 0, scale: objectivesInView ? 1 : 0.9 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="text-4xl font-bold mb-4 inline-block bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/70"
              >
                Our Objectives
              </motion.h2>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: objectivesInView ? "100px" : 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="h-1 bg-primary/40 mx-auto rounded-full"
              />
            </motion.div>
            
            <motion.div
              variants={staggerVariants}
              initial="hidden"
              animate={objectivesInView ? "visible" : "hidden"}
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 max-w-6xl mx-auto"
            >
              {objectives.map((objective, index) => (
                <motion.div
                  key={`objective-${index}`}
                  variants={itemVariants}
                  initial="initial"
                  animate="animate"
                  whileHover="hover"
                  onHoverStart={() => setHoveredObjective(index)}
                  onHoverEnd={() => setHoveredObjective(null)}
                  custom={index}
                  transition={{ 
                    duration: 0.5, 
                    delay: index * 0.1 
                  }}
                  className="relative overflow-hidden"
                >
                  <motion.div
                    variants={cardVariants}
                    className={`bg-gradient-to-br ${objective.color} rounded-xl p-8 h-full border border-primary/10 shadow-lg relative z-10 backdrop-blur-sm`}
                  >
                    <motion.div
                      className="bg-background/10 backdrop-blur-sm rounded-full p-4 w-16 h-16 flex items-center justify-center mb-6"
                      whileHover={{ 
                        rotate: [0, 10, -10, 0],
                        transition: { duration: 0.5 }
                      }}
                    >
                      <objective.icon className="h-8 w-8 text-primary" />
                    </motion.div>
                    
                    <motion.h3 
                      className="text-xl font-semibold mb-3"
                      animate={{
                        color: hoveredObjective === index ? "rgba(var(--primary), 1)" : "currentColor"
                      }}
                    >
                      {objective.title}
                    </motion.h3>
                    
                    <motion.p className="text-muted-foreground">
                      {objective.text}
                    </motion.p>
                    
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-1 bg-primary/40"
                      initial={{ scaleX: 0, originX: 0 }}
                      whileHover={{ scaleX: 1 }}
                      transition={{ duration: 0.4 }}
                    />
                  </motion.div>
                  
                  {/* Decorative element */}
                  <motion.div
                    className="absolute -top-20 -right-20 w-40 h-40 rounded-full bg-primary/5 -z-10"
                    animate={{
                      scale: hoveredObjective === index ? 1.3 : 1,
                      opacity: hoveredObjective === index ? 0.8 : 0,
                    }}
                    transition={{ duration: 0.6 }}
                  />
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Services Section */}
          <div className="mb-28" ref={servicesRef}>
            {/* Placeholder for now, will keep the existing implementation */}
          </div>
          
          {/* Team Section */}
          <div className="mb-20" ref={teamRef}>
            {/* Placeholder for now, will keep the existing implementation */}
          </div>
        </motion.div>
      </div>
    </main>
  );
}
