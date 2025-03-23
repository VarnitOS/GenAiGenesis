"use client";

import { useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import { Database, Code, ScanText, LineChart, Brain, ArrowRight, CheckCircle, Scale, BookOpen, Shield, Users, 
  MessageSquare, Server, Network, Search, FileText, CheckSquare, LayoutGrid, Key, Layers, Database as DatabaseIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ParticlesBackground } from "@/components/particles-background";
import Link from "next/link";

export default function HowItWorksPage() {
  const step1Ref = useRef(null);
  const step2Ref = useRef(null);
  const step3Ref = useRef(null);
  const step4Ref = useRef(null);
  const diagramRef = useRef(null);
  
  const isStep1InView = useInView(step1Ref, { once: true, amount: 0.5 });
  const isStep2InView = useInView(step2Ref, { once: true, amount: 0.5 });
  const isStep3InView = useInView(step3Ref, { once: true, amount: 0.5 });
  const isStep4InView = useInView(step4Ref, { once: true, amount: 0.5 });
  const isDiagramInView = useInView(diagramRef, { once: true, amount: 0.1 });
  
  const [activeSection, setActiveSection] = useState(null);
  
  const steps = [
    {
      ref: step1Ref,
      isInView: isStep1InView,
      icon: Users,
      title: "Client Consultation",
      description: "Much like a receptionist and initial attorney consultation at a law firm, our Client Consultation Agent utilizes Cohere Command and Embed models to understand client needs, establish attorney-client relationships, and route matters to appropriate specialists.",
      color: "from-blue-500 to-indigo-600"
    },
    {
      ref: step2Ref,
      isInView: isStep2InView,
      icon: BookOpen,
      title: "Legal Research & Analysis",
      description: "Mirroring the work of paralegals and associate attorneys, our Legal Research Agent employs Cohere Chat and Vector Search technology to conduct thorough legal research across case law, statutes, regulations, and precedents—synthesizing findings into actionable legal insights.",
      color: "from-indigo-500 to-purple-600"
    },
    {
      ref: step3Ref,
      isInView: isStep3InView,
      icon: Shield,
      title: "Verification & Quality Control",
      description: "Functioning like senior partners or compliance officers, our Verification Agent leverages Cohere Command, Rerank, and HuggingFace Factuality models to ensure all legal advice is accurate, properly sourced, and adheres to ethical standards—providing the quality assurance critical to legal practice.",
      color: "from-purple-500 to-pink-600"
    },
    {
      ref: step4Ref,
      isInView: isStep4InView,
      icon: Scale,
      title: "Client Representation",
      description: "Just as attorneys present cases and counsel clients, our orchestrated system integrates the findings from all specialized agents, maintaining conversation memory and knowledge graphs to provide coherent, contextually aware legal guidance through our intuitive client interface.",
      color: "from-pink-500 to-red-600"
    }
  ];
  
  const benefits = [
    "Seamless client intake and case assignment workflow",
    "Comprehensive legal research across multiple jurisdictions",
    "Rigorous fact-checking and citation verification",
    "Knowledge retention across multiple client interactions",
    "Consistent application of legal principles",
    "Ethical compliance and confidentiality safeguards"
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

  const nodeVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.5 } }
  };

  const lineVariants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: { pathLength: 1, opacity: 0.5, transition: { duration: 0.8, ease: "easeInOut" } }
  };

  const sections = [
    { id: "interface", name: "Client Interface", color: "#f9d5e5", hoverColor: "#f7bed7" },
    { id: "orchestration", name: "Agent Orchestration", color: "#e3f9f6", hoverColor: "#c9f5ef" },
    { id: "modelA", name: "Client Consultation Agent", color: "#dbf0ff", hoverColor: "#b6e3ff" },
    { id: "modelB", name: "Legal Research Agent", color: "#d5f5e3", hoverColor: "#b3edc9" },
    { id: "modelC", name: "Verification Agent", color: "#ffe6cc", hoverColor: "#ffd699" },
    { id: "knowledge", name: "Knowledge Infrastructure", color: "#e0e0e0", hoverColor: "#c8c8c8" },
    { id: "memory", name: "Memory Systems", color: "#fdebd0", hoverColor: "#faddaa" }
  ];

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
              Virtual Law Clinic Architecture
            </h1>
            <p className="mt-4 text-xl text-muted-foreground max-w-2xl mx-auto">
              Our agentic AI system simulates the operational structure of a real-world law firm
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

          {/* Improved Architecture Diagram */}
          <motion.div
            ref={diagramRef}
            initial={{ opacity: 0, y: 40 }}
            animate={isDiagramInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7 }}
            className="bg-card/80 backdrop-blur-sm p-6 md:p-10 rounded-xl border border-border/50 mb-20 shadow-lg"
          >
            <h2 className="text-3xl font-semibold mb-8 text-center">System Architecture</h2>
            <p className="text-muted-foreground text-center mb-10 max-w-2xl mx-auto">
              Our multi-agent architecture mirrors a real law firm's structure, with specialized components working in concert to deliver legal services.
            </p>
            
            <div className="mb-6 flex flex-wrap justify-center gap-3">
              {sections.map((section) => (
                <motion.button
                  key={section.id}
                  onClick={() => setActiveSection(activeSection === section.id ? null : section.id)}
                  className="px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-300"
                  style={{ 
                    backgroundColor: activeSection === section.id ? section.hoverColor : section.color,
                    opacity: activeSection && activeSection !== section.id ? 0.7 : 1
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {section.name}
                </motion.button>
              ))}
            </div>
            
            <div className="relative w-full overflow-x-auto pb-6">
              <div className="min-w-[1000px] lg:max-w-[1200px] mx-auto">
                {/* Top Layer - Client Interface */}
                <motion.div 
                  className={`transition-opacity duration-300 mb-16 ${activeSection && activeSection !== 'interface' ? 'opacity-40' : 'opacity-100'}`}
                  initial="hidden"
                  animate={isDiagramInView ? "visible" : "hidden"}
                  variants={staggerVariants}
                >
                  <SectionLabel label="Client Interface" bgColor="#f9d5e5" variants={nodeVariants} />
                  <div className="flex justify-center gap-8 mt-3">
                    <ComponentBox icon={<MessageSquare />} label="Web Chat Portal" bgColor="#f9d5e5" variants={nodeVariants} />
                    <ComponentBox icon={<Server />} label="API Gateway" bgColor="#f9d5e5" variants={nodeVariants} />
                  </div>
                  <ArrowDown />
                </motion.div>

                {/* Middle Layer - Agent Orchestration */}
                <motion.div 
                  className={`transition-opacity duration-300 mb-16 ${activeSection && activeSection !== 'orchestration' ? 'opacity-40' : 'opacity-100'}`}
                  initial="hidden"
                  animate={isDiagramInView ? "visible" : "hidden"}
                  variants={staggerVariants}
                >
                  <SectionLabel label="Agent Orchestration" bgColor="#e3f9f6" variants={nodeVariants} />
                  <div className="flex justify-center mt-3">
                    <ComponentBox icon={<Network />} label="LangChain Agent Orchestrator" bgColor="#e3f9f6" variants={nodeVariants} wide />
                  </div>
                  <div className="relative h-10 mt-3">
                    <div className="absolute left-1/2 h-full w-0.5 bg-gradient-to-b from-[#e3f9f6] to-transparent transform -translate-x-1/2"></div>
                    <div className="absolute left-1/4 top-1/2 w-[25%] h-0.5 bg-gradient-to-r from-transparent to-[#e3f9f6]"></div>
                    <div className="absolute left-1/2 top-1/2 w-[25%] h-0.5 bg-gradient-to-r from-[#e3f9f6] to-transparent"></div>
                  </div>
                </motion.div>

                {/* Main 3-column agent section */}
                <div className="grid grid-cols-3 gap-6 mb-16">
                  {/* Left Column - Client Consultation Agent */}
                  <motion.div 
                    className={`transition-opacity duration-300 ${activeSection && activeSection !== 'modelA' ? 'opacity-40' : 'opacity-100'}`}
                    initial="hidden"
                    animate={isDiagramInView ? "visible" : "hidden"}
                    variants={staggerVariants}
                  >
                    <SectionLabel label="Client Consultation Agent" bgColor="#dbf0ff" variants={nodeVariants} />
                    <div className="flex flex-col gap-4 mt-3">
                      <ComponentBox icon={<Code />} label="Cohere Command" bgColor="#dbf0ff" variants={nodeVariants} />
                      <ComponentBox icon={<Search />} label="Cohere Embed" bgColor="#dbf0ff" variants={nodeVariants} />
                      <ComponentBox icon={<Users />} label="Client Understanding Chain" bgColor="#dbf0ff" variants={nodeVariants} />
                    </div>
                  </motion.div>

                  {/* Middle Column - Legal Research Agent */}
                  <motion.div 
                    className={`transition-opacity duration-300 ${activeSection && activeSection !== 'modelB' ? 'opacity-40' : 'opacity-100'}`}
                    initial="hidden"
                    animate={isDiagramInView ? "visible" : "hidden"}
                    variants={staggerVariants}
                  >
                    <SectionLabel label="Legal Research Agent" bgColor="#d5f5e3" variants={nodeVariants} />
                    <div className="flex flex-col gap-4 mt-3">
                      <ComponentBox icon={<MessageSquare />} label="Cohere Chat" bgColor="#d5f5e3" variants={nodeVariants} />
                      <ComponentBox icon={<DatabaseIcon />} label="Vector Search Engine" bgColor="#d5f5e3" variants={nodeVariants} />
                      <ComponentBox icon={<FileText />} label="Research Synthesis Chain" bgColor="#d5f5e3" variants={nodeVariants} />
                    </div>
                  </motion.div>

                  {/* Right Column - Verification Agent */}
                  <motion.div 
                    className={`transition-opacity duration-300 ${activeSection && activeSection !== 'modelC' ? 'opacity-40' : 'opacity-100'}`}
                    initial="hidden"
                    animate={isDiagramInView ? "visible" : "hidden"}
                    variants={staggerVariants}
                  >
                    <SectionLabel label="Verification Agent" bgColor="#ffe6cc" variants={nodeVariants} />
                    <div className="flex flex-col gap-4 mt-3">
                      <ComponentBox icon={<Code />} label="Cohere Command" bgColor="#ffe6cc" variants={nodeVariants} />
                      <ComponentBox icon={<LayoutGrid />} label="Cohere Rerank" bgColor="#ffe6cc" variants={nodeVariants} />
                      <ComponentBox icon={<CheckSquare />} label="Verification Chain" bgColor="#ffe6cc" variants={nodeVariants} />
                      <ComponentBox icon={<Shield />} label="HuggingFace Factuality Model" bgColor="#ffe6cc" variants={nodeVariants} />
                    </div>
                  </motion.div>
                </div>

                {/* Knowledge Infrastructure */}
                <motion.div 
                  className={`transition-opacity duration-300 mb-16 ${activeSection && activeSection !== 'knowledge' ? 'opacity-40' : 'opacity-100'}`}
                  initial="hidden"
                  animate={isDiagramInView ? "visible" : "hidden"}
                  variants={staggerVariants}
                >
                  <SectionLabel label="Knowledge Infrastructure" bgColor="#e0e0e0" variants={nodeVariants} />
                  <div className="grid grid-cols-5 gap-4 mt-3">
                    <ComponentBox icon={<BookOpen size={18} />} label="Case Law Vector DB" bgColor="#e0e0e0" variants={nodeVariants} small />
                    <ComponentBox icon={<BookOpen size={18} />} label="Statutes Vector DB" bgColor="#e0e0e0" variants={nodeVariants} small />
                    <ComponentBox icon={<BookOpen size={18} />} label="Regulations Vector DB" bgColor="#e0e0e0" variants={nodeVariants} small />
                    <ComponentBox icon={<BookOpen size={18} />} label="Precedents Vector DB" bgColor="#e0e0e0" variants={nodeVariants} small />
                    <ComponentBox icon={<Key size={18} />} label="Authorized Sources List" bgColor="#e0e0e0" variants={nodeVariants} small />
                  </div>
                  <ArrowDown />
                </motion.div>

                {/* Memory Systems */}
                <motion.div 
                  className={`transition-opacity duration-300 ${activeSection && activeSection !== 'memory' ? 'opacity-40' : 'opacity-100'}`}
                  initial="hidden"
                  animate={isDiagramInView ? "visible" : "hidden"}
                  variants={staggerVariants}
                >
                  <SectionLabel label="Memory Systems" bgColor="#fdebd0" variants={nodeVariants} />
                  <div className="flex justify-center gap-8 mt-3">
                    <ComponentBox icon={<MessageSquare />} label="Conversation Memory" bgColor="#fdebd0" variants={nodeVariants} />
                    <ComponentBox icon={<Layers />} label="Knowledge Graph" bgColor="#fdebd0" variants={nodeVariants} />
                  </div>
                </motion.div>
              </div>
            </div>

            <motion.div 
              className="text-sm text-center text-muted-foreground mt-6"
              initial={{ opacity: 0 }}
              animate={isDiagramInView ? { opacity: 1 } : {}}
              transition={{ delay: 1 }}
            >
              Click on any section title to highlight its components in the architecture
            </motion.div>
          </motion.div>

          {/* Law Firm Architecture Simulation Section */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7 }}
            className="bg-card/80 backdrop-blur-sm p-10 rounded-xl border border-border/50 mb-20 shadow-lg"
          >
            <h2 className="text-3xl font-semibold mb-8 text-center">Law Firm Architecture Simulation</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.5 }}
                className="bg-background/50 p-6 rounded-lg border border-border/30"
              >
                <h3 className="text-xl font-semibold mb-4 text-primary">Front Office Operations</h3>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">Web Chat Portal functions as the firm's reception area, greeting clients and initiating intake</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">API Gateway serves as the administrative coordinator, routing client matters to appropriate departments</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">LangChain Agent Orchestrator mirrors a managing partner, overseeing case workflow and resource allocation</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">Client Understanding Chain emulates initial attorney consultations to identify legal issues</span>
                  </li>
                </ul>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.5 }}
                className="bg-background/50 p-6 rounded-lg border border-border/30"
              >
                <h3 className="text-xl font-semibold mb-4 text-primary">Back Office Legal Work</h3>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">Vector Search Engine replicates the law library and research database access</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">Research Synthesis Chain functions like associate attorneys drafting legal memoranda</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">Verification Chain operates as the firm's quality control and ethics committee</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-muted-foreground">HuggingFace Factuality Model serves as the meticulous fact-checker in document preparation</span>
                  </li>
                </ul>
              </motion.div>
            </div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-background/50 p-6 rounded-lg border border-border/30"
            >
              <h3 className="text-xl font-semibold mb-4 text-primary">Knowledge Management Infrastructure</h3>
              <ol className="space-y-2 list-decimal pl-5">
                <li className="text-muted-foreground">
                  <span className="font-medium text-foreground">Legal Knowledge Base:</span> Our Vector Databases for Case Law, Statutes, Regulations, and Precedents parallel a firm's specialized practice libraries
                </li>
                <li className="text-muted-foreground">
                  <span className="font-medium text-foreground">Institutional Memory:</span> Conversation Memory functions like detailed client file management and history
                </li>
                <li className="text-muted-foreground">
                  <span className="font-medium text-foreground">Connected Intelligence:</span> Knowledge Graph mimics senior attorneys' ability to connect seemingly disparate legal concepts
                </li>
                <li className="text-muted-foreground">
                  <span className="font-medium text-foreground">Ethical Safeguards:</span> Authorized Sources List implements ethical rules regarding legal research integrity
                </li>
                <li className="text-muted-foreground">
                  <span className="font-medium text-foreground">Multi-agent Collaboration:</span> The interconnected system of agents replicates law firm departments collaborating on complex matters
                </li>
                <li className="text-muted-foreground">
                  <span className="font-medium text-foreground">Client Communication:</span> The full system synthesizes information into clear legal guidance, similar to client-facing documents
                </li>
              </ol>
            </motion.div>
          </motion.div>

          {/* Benefits Section */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7 }}
            className="bg-card/80 backdrop-blur-sm p-10 rounded-xl border border-border/50 mb-20 shadow-lg"
          >
            <h2 className="text-3xl font-semibold mb-8 text-center">Legal Practice Benefits</h2>
            
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
            <h2 className="text-3xl font-semibold mb-6">Experience AI-powered legal assistance</h2>
            <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
              Our virtual law clinic architecture provides professional-grade legal support through an innovative multi-agent system.
            </p>
            <Button size="lg" className="bg-primary text-primary-foreground group shadow-lg shadow-primary/20">
              <Link href="/contact/form">
                Consult With Our System
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
          </motion.div>
        </div>
      </div>
    </main>
  );
}

// Component for section labels
function SectionLabel({ label, bgColor, variants }) {
  return (
    <motion.div 
      className="text-center font-medium py-2 px-6 rounded-full max-w-xs mx-auto"
      style={{ backgroundColor: `${bgColor}60` }}
      variants={variants}
    >
      {label}
    </motion.div>
  );
}

// Component for architecture components
function ComponentBox({ icon, label, bgColor, variants, wide = false, small = false }) {
  return (
    <motion.div
      className={`${wide ? 'min-w-80' : small ? 'min-w-0' : 'min-w-52'} bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-md p-4 flex flex-col items-center justify-center gap-2 h-full`}
      style={{ backgroundColor: `${bgColor}20` }}
      variants={variants}
      whileHover={{ scale: 1.02, boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)" }}
    >
      <div className="text-gray-800 dark:text-gray-200">
        {icon}
      </div>
      <div className={`text-center font-medium ${small ? 'text-xs' : 'text-sm'}`}>
        {label}
      </div>
    </motion.div>
  );
}

// Component for downward arrows
function ArrowDown() {
  return (
    <div className="flex justify-center my-4">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-400">
        <path d="M12 5L12 19M12 19L19 12M12 19L5 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </div>
  );
} 