"use client";

import { motion } from "framer-motion";
import { Users } from "lucide-react";

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <Users className="h-12 w-12 mx-auto mb-4 text-primary" />
          <h1 className="text-4xl font-bold tracking-tight">About Us</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Making justice accessible through technology
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-card/80 backdrop-blur-sm p-8 rounded-lg border border-border/50 max-w-3xl mx-auto"
        >
          <h2 className="text-2xl font-semibold mb-4">Mission</h2>
          <p className="text-muted-foreground mb-6">
            LAW-DER is committed to democratizing legal assistance through cutting-edge AI technology while advancing legal literacy, diversity, equity, and inclusion. We believe that everyone—regardless of their financial situation or background—deserves access to quality legal guidance. Legal knowledge should not be a privilege but a right, empowering individuals to navigate the complexities of the legal system with confidence. Our platform prioritizes those from less favorable socioeconomic backgrounds, ensuring they have the tools and information necessary to protect their rights. By leveraging AI, we break down barriers to legal education, promote fairness, and foster a more just and inclusive society where legal literacy is accessible to all.
          </p>

          <h2 className="text-2xl font-semibold mb-4"> Vision</h2>
          <p className="text-muted-foreground mb-6">
            To create a world where legal assistance is universally accessible, empowering individuals with the knowledge and resources to defend their rights. Through AI-driven solutions, we aim to foster a legal system that is fair, inclusive, and equitable for all, regardless of socioeconomic status.
          </p>

          <h2 className="text-2xl font-semibold mb-4">Our Objectives</h2>
          <ul className="list-disc list-inside text-muted-foreground mb-6">
            <li>Enhance legal literacy by providing accessible educational resources.</li>
            <li>Leverage AI to offer real-time, affordable legal assistance.</li>
            <li>Break socioeconomic barriers by prioritizing underserved communities.</li>
            <li>Continuously expand and refine our legal database for better accessibility.</li>
            <li>Advocate for diversity, equity, and inclusion within the legal landscape.</li>
          </ul>

          <h2 className="text-2xl font-semibold mb-4">What We Do</h2>
          <p className="text-muted-foreground mb-4"><strong className="text-primary">24/7 AI-Powered Legal Assistance:</strong> Instant, AI-driven legal guidance accessible anytime, anywhere.</p>
          <p className="text-muted-foreground mb-4"><strong className="text-primary">Simplifying Legal Document Management:</strong> Streamlining the creation, organization, and accessibility of legal documents.</p>
          <p className="text-muted-foreground mb-4"><strong className="text-primary">Providing a Comprehensive Case Law Database:</strong> Ensuring easy access to essential legal precedents and rulings.</p>
          <p className="text-muted-foreground mb-4"><strong className="text-primary">Enhancing Legal Literacy & Awareness:</strong> Sharing expert insights, educational resources, and updates through our blog.</p>
          <p className="text-muted-foreground mb-4"><strong className="text-primary">Empowering Underserved Communities:</strong> Prioritizing individuals from less favorable socioeconomic backgrounds to ensure fair access to legal resources.</p>
          <p className="text-muted-foreground mb-4"><strong className="text-primary">Advancing Diversity, Equity & Inclusion:</strong> Breaking down barriers in legal education and assistance to build a more just society.</p>
        </motion.div>
      </div>
    </main>
  );
}
