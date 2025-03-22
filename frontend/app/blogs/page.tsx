"use client";

import { motion } from "framer-motion";
import { BookOpen } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

interface LawResource {
  title: string;
  url: string;
  imageUrl: string;
  description: string;
}

const lawResources: LawResource[] = [
  {
    title: "CanLII",
    url: "https://www.canlii.org/",
    imageUrl: "https://images.unsplash.com/photo-1589994965851-a8f479c573a9?q=80&w=800",
    description: "Canadian Legal Information Institute Database"
  },
  {
    title: "Criminal Code of Canada",
    url: "https://laws-lois.justice.gc.ca/eng/acts/c-46/",
    imageUrl: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800",
    description: "Official Criminal Code of Canada"
  },
  {
    title: "Criminal Law Notebook",
    url: "https://criminalnotebook.ca/index.php/Main_Page",
    imageUrl: "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=800",
    description: "Comprehensive Criminal Law Resource"
  },
  {
    title: "Canadian Immigration Laws",
    url: "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/laws.html",
    imageUrl: "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?q=80&w=800",
    description: "Immigration and Settlement Laws"
  },
  {
    title: "CanLII About",
    url: "https://www.canlii.org/info/about.html",
    imageUrl: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=800",
    description: "About the CanLII Platform"
  },
  {
    title: "Federal Court Decisions",
    url: "https://www.fct-cf.gc.ca/en/court-files-and-decisions/court-files",
    imageUrl: "https://images.unsplash.com/photo-1593115057322-e94b77572f20?q=80&w=800",
    description: "Federal Court Case Files"
  },
  {
    title: "BYU Law Guide",
    url: "https://guides.law.byu.edu/canada",
    imageUrl: "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?q=80&w=800",
    description: "BYU Guide to Canadian Law"
  },
  {
    title: "Harvard Law Guide",
    url: "https://guides.library.harvard.edu/law/canada",
    imageUrl: "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?q=80&w=800",
    description: "Harvard Guide to Canadian Law"
  },
  {
    title: "Federation of Law Societies",
    url: "https://flsc.ca/",
    imageUrl: "https://images.unsplash.com/photo-1436450412740-6b988f486c6b?q=80&w=800",
    description: "Federation of Law Societies of Canada"
  },
  {
    title: "Supreme Court of Canada",
    url: "https://www.scc-csc.ca/home-accueil/",
    imageUrl: "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?q=80&w=800",
    description: "Supreme Court of Canada Portal"
  }
];

export default function BlogsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <BookOpen className="h-12 w-12 mx-auto mb-4 text-primary" />
          <h1 className="text-4xl font-bold tracking-tight">Weekly Law Blogs</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Essential Canadian Legal Resources and Updates
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lawResources.map((resource, index) => (
            <motion.div
              key={resource.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Link
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block group"
              >
                <div className="bg-card/80 backdrop-blur-sm rounded-lg border border-border/50 overflow-hidden transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
                  <div className="relative h-48 w-full">
                    <Image
                      src={resource.imageUrl}
                      alt={resource.title}
                      fill
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                      {resource.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {resource.description}
                    </p>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </main>
  );
}