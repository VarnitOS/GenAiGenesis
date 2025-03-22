"use client";

import { useRef, useState } from "react";
import { motion, useInView, useScroll, useTransform } from "framer-motion";
import { Users, Scale, Gavel, Target, Award, Clock, ArrowRight, ChevronDown, Star, Shield, BookOpen } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ParticlesBackground } from "@/components/particles-background";

export default function AboutPage() {
  const [activeTab, setActiveTab] = useState(0);
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
  
  const objectives = [
    { icon: Award, text: "Enhance legal literacy by providing accessible educational resources." },
    { icon: Clock, text: "Leverage AI to offer real-time, affordable legal assistance." },
    { icon: Target, text: "Break socioeconomic barriers by prioritizing underserved communities." },
    { icon: Scale, text: "Continuously expand and refine our legal database for better accessibility." },
    { icon: Gavel, text: "Advocate for diversity, equity, and inclusion within the legal landscape." }
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-20" ref={missionRef}>

            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: missionInView ? 1 : 0, x: missionInView ? 0 : -50 }}
              transition={{ duration: 0.7 }}
              className="bg-card/80 backdrop-blur-sm p-8 rounded-lg border border-border/50 hover:border-primary/30 transition-all duration-300 shadow-lg"
            >
              <motion.div 
                initial={{ width: "0%" }}
                animate={{ width: missionInView ? "100%" : "0%" }}
                transition={{ duration: 1.2, ease: "easeOut" }}
                className="h-1 bg-primary/30 mb-6 rounded-full"
              />
              <motion.h2 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: missionInView ? 1 : 0, x: missionInView ? 0 : -20 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="text-3xl font-semibold mb-5 border-l-4 border-primary pl-4"
              >
                Mission
              </motion.h2>
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: missionInView ? 1 : 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="text-muted-foreground mb-6 leading-relaxed"
              >
                LAW-DER is committed to democratizing legal assistance through cutting-edge AI technology while advancing legal literacy, diversity, equity, and inclusion. We believe that everyone—regardless of their financial situation or background—deserves access to quality legal guidance. Legal knowledge should not be a privilege but a right, empowering individuals to navigate the complexities of the legal system with confidence.
              </motion.p>
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: missionInView ? 1 : 0 }}
                transition={{ duration: 0.5, delay: 0.6 }}
                className="text-muted-foreground mb-6 leading-relaxed"
              >
                Our platform prioritizes those from less favorable socioeconomic backgrounds, ensuring they have the tools and information necessary to protect their rights. By leveraging AI, we break down barriers to legal education, promote fairness, and foster a more just and inclusive society where legal literacy is accessible to all.
              </motion.p>
            </motion.div>
          </div>
          </motion.div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-card/80 backdrop-blur-sm p-8 rounded-lg border border-border/50 max-w-3xl mx-auto"
        >
          <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
          <p className="text-muted-foreground mb-6">
            LAW-DER is dedicated to democratizing legal assistance through cutting-edge AI technology. 
            We believe everyone deserves access to quality legal guidance, regardless of their financial situation.
          </p>

          <h2 className="text-2xl font-semibold mb-4">What We Do</h2>
          <ul className="space-y-4 text-muted-foreground">
            <li>• Provide 24/7 AI-powered legal assistance</li>
            <li>• Connect clients with pro bono lawyers</li>
            <li>• Simplify legal document management</li>
            <li>• Offer comprehensive case law database</li>
            <li>• Share expert legal insights through our blog</li>
          </ul>
        </motion.div>
      </div>
    </main>
  );
}
