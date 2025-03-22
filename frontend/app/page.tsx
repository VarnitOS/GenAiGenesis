"use client";

import { motion } from "framer-motion";
import { Scale, Gavel, BookOpen, FileText, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/navbar";
import { ParticlesBackground } from "@/components/particles-background";

export default function Home() {
  const features = [
    {
      icon: Scale,
      title: "AI Assistant",
      description: "Your 24/7 legal companion powered by advanced AI",
      tagline: "Justice never sleeps, neither does our AI"
    },
    {
      icon: FileText,
      title: "Document Manager",
      description: "Smart document analysis and management system",
      tagline: "The paper chase ends here"
    },
    {
      icon: BookOpen,
      title: "Law Case Database",
      description: "Comprehensive repository of legal precedents",
      tagline: "Order in the digital court"
    },
    {
      icon: Gavel,
      title: "Law Blog",
      description: "Latest insights from legal experts",
      tagline: "Where law meets clarity"
    }
  ];

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20">
        {/* Hero Section */}
        <section className="relative h-screen flex items-center justify-center overflow-hidden">
          <ParticlesBackground />
          <div className="absolute inset-0 z-0">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.1 }}
              transition={{ duration: 1 }}
              className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1589994965851-a8f479c573a9?q=80&w=2000')] bg-cover bg-center"
            />
          </div>
          
          <div className="relative z-10 text-center space-y-8 max-w-4xl mx-auto px-4">
            <motion.h1
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80"
            >
              LAW-DER
            </motion.h1>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl font-light text-muted-foreground"
            >
              LAW AND ORDER JUST GOT LOUDER
            </motion.p>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Button size="lg" className="bg-primary text-primary-foreground group">
                Get Started
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button size="lg" variant="outline">
                Explore Cases
              </Button>
              <Button size="lg" variant="ghost">
                Watch Demo
              </Button>
            </motion.div>
          </div>

          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="absolute bottom-10 text-center w-full text-muted-foreground px-4"
          >
            <p className="text-lg italic">"In the court of technology, justice is served 24/7"</p>
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-6 relative">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ y: 50, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="relative group"
              >
                <div className="bg-card/80 backdrop-blur-sm p-8 rounded-lg border border-border/50 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
                  <feature.icon className="w-12 h-12 mb-4 text-primary" />
                  <h3 className="text-2xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground mb-4">{feature.description}</p>
                  <p className="text-sm italic text-primary">{feature.tagline}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}