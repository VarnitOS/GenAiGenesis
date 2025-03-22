"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Lightbulb, FileText, UserCheck, Scale, ArrowRight, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ParticlesBackground } from "@/components/particles-background";
import Link from "next/link";

export default function HowItWorksPage() {
  const step1Ref = useRef(null);
  const step2Ref = useRef(null);
  const step3Ref = useRef(null);
  const step4Ref = useRef(null);
  
  const isStep1InView = useInView(step1Ref, { once: true, amount: 0.5 });
  const isStep2InView = useInView(step2Ref, { once: true, amount: 0.5 });
  const isStep3InView = useInView(step3Ref, { once: true, amount: 0.5 });
  const isStep4InView = useInView(step4Ref, { once: true, amount: 0.5 });
  
  const steps = [
    {
      ref: step1Ref,
      isInView: isStep1InView,
      icon: Lightbulb,
      title: "Initial Consultation",
      description: "Our AI analyzes your legal situation. Simply describe your case, and our system will identify the key legal issues and suggest the best path forward.",
      color: "from-blue-500 to-indigo-600"
    },
    {
      ref: step2Ref,
      isInView: isStep2InView,
      icon: FileText,
      title: "Document Assessment",
      description: "Upload any relevant documents. Our AI will review contracts, legal notices, and other documents to extract important information and identify potential risks or opportunities.",
      color: "from-indigo-500 to-purple-600"
    },
    {
      ref: step3Ref,
      isInView: isStep3InView,
      icon: UserCheck,
      title: "Expert Matching",
      description: "Based on your needs, we'll connect you with the most suitable legal resources or professionals who specialize in your specific legal matters.",
      color: "from-purple-500 to-pink-600"
    },
    {
      ref: step4Ref,
      isInView: isStep4InView,
      icon: Scale,
      title: "Personalized Action Plan",
      description: "Receive a comprehensive action plan tailored to your situation. This includes recommended steps, timeline, and resources to help you navigate your legal journey.",
      color: "from-pink-500 to-red-600"
    }
  ];
  
  const benefits = [
    "Access to legal expertise 24/7",
    "Significant cost savings compared to traditional legal services",
    "Personalized advice tailored to your specific situation",
    "Secure and confidential handling of all your information",
    "Easy-to-understand explanations of complex legal concepts",
    "Faster resolution of your legal matters"
  ];

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

  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-20 pb-20 overflow-hidden">
      <div className="relative">
        <div className="absolute inset-0 -z-10 opacity-5">
          <ParticlesBackground />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-16"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
              className="bg-primary/10 rounded-full p-4 w-24 h-24 flex items-center justify-center mx-auto mb-6"
            >
              <Scale className="h-12 w-12 text-primary" />
            </motion.div>
            <h1 className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80">
              How It Works
            </h1>
            <p className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto">
              Simple, efficient, and powerful legal assistance at your fingertips
            </p>
          </motion.div>

          {/* Process Steps */}
          <div className="mb-24 space-y-24">
            {steps.map((step, index) => (
              <div 
                key={index}
                ref={step.ref} 
                className={`relative ${index % 2 === 0 ? 'lg:mr-[50%]' : 'lg:ml-[50%]'}`}
              >
                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="absolute h-24 w-px bg-gradient-to-b from-primary/50 to-transparent left-[39px] top-full z-0 hidden md:block"></div>
                )}
                
                <motion.div
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  animate={step.isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.7, delay: 0.2 }}
                  className="flex flex-col md:flex-row items-start gap-6 relative z-10"
                >
                  <div className="flex-shrink-0">
                    <div className="relative">
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={step.isInView ? { scale: 1 } : {}}
                        transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.4 }}
                        className={`w-20 h-20 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center shadow-lg`}
                      >
                        <step.icon className="h-10 w-10 text-white" />
                      </motion.div>
                      <motion.div 
                        initial={{ opacity: 0, scale: 0 }}
                        animate={step.isInView ? { opacity: 1, scale: 1 } : {}}
                        transition={{ duration: 0.4, delay: 0.5 }}
                        className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-background flex items-center justify-center shadow-md border-2 border-primary"
                      >
                        <span className="text-primary font-bold">{index + 1}</span>
                      </motion.div>
                    </div>
                  </div>
                  
                  <div className="bg-card/80 backdrop-blur-sm p-6 md:p-8 rounded-xl border border-border/50 flex-grow hover:border-primary/30 transition-all duration-300 shadow-lg">
                    <motion.h3 
                      initial={{ opacity: 0, y: -10 }}
                      animate={step.isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ duration: 0.5, delay: 0.3 }}
                      className="text-2xl font-bold mb-4"
                    >
                      {step.title}
                    </motion.h3>
                    <motion.p 
                      initial={{ opacity: 0 }}
                      animate={step.isInView ? { opacity: 1 } : {}}
                      transition={{ duration: 0.5, delay: 0.4 }}
                      className="text-muted-foreground"
                    >
                      {step.description}
                    </motion.p>
                  </div>
                </motion.div>
              </div>
            ))}
          </div>

          {/* Benefits Section */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7 }}
            className="bg-card/80 backdrop-blur-sm p-10 rounded-xl border border-border/50 mb-20 shadow-lg"
          >
            <h2 className="text-3xl font-semibold mb-8 text-center">The Benefits of LAW-DER</h2>
            
            <motion.ul 
              variants={staggerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {benefits.map((benefit, index) => (
                <motion.li 
                  key={index} 
                  variants={itemVariants}
                  whileHover={{ x: 5 }}
                  className="flex items-start space-x-3 bg-background/50 p-5 rounded-lg border border-border/30 hover:border-primary/30 transition-all duration-300"
                >
                  <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">{benefit}</span>
                </motion.li>
              ))}
            </motion.ul>
          </motion.div>

          {/* CTA Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7 }}
            className="bg-primary/10 rounded-xl p-10 text-center mb-10 max-w-4xl mx-auto"
          >
            <h2 className="text-3xl font-semibold mb-6">Ready to experience LAW-DER?</h2>
            <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of users who are already leveraging our platform for accessible legal assistance.
            </p>
            <Button size="lg" className="bg-primary text-primary-foreground group shadow-lg shadow-primary/20">
              <Link href="/get-started">
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </motion.div>
        </div>
      </div>
    </main>
  );
}