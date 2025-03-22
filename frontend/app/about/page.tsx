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