"use client";

import { motion } from "framer-motion";
import { Scale } from "lucide-react";

export default function CasesPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <Scale className="h-12 w-12 mx-auto mb-4 text-primary" />
          <h1 className="text-4xl font-bold tracking-tight">Case Archives</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Explore our comprehensive database of legal precedents and judgments
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Placeholder for case archive content */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-card/80 backdrop-blur-sm p-6 rounded-lg border border-border/50"
          >
            <p className="text-lg font-medium">Coming Soon</p>
            <p className="text-muted-foreground mt-2">
              Our case archive is being populated with the latest legal precedents and judgments.
            </p>
          </motion.div>
        </div>
      </div>
    </main>
  );
}