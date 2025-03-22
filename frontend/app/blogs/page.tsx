"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, ArrowRight, Clock, Eye, ExternalLink, ChevronRight, ChevronLeft } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { 
  Carousel, 
  CarouselContent, 
  CarouselItem, 
  CarouselPrevious, 
  CarouselNext,
  type CarouselApi
} from "@/components/ui/carousel";
import { Badge } from "@/components/ui/badge";
import { ParticlesBackground } from "@/components/particles-background";

interface LawResource {
  title: string;
  url: string;
  imageUrl: string;
  description: string;
  category?: string;
  readTime?: string;
  date?: string;
  featured?: boolean;
}

const lawResources: LawResource[] = [
  {
    title: "Understanding Canadian Immigration Law Changes for 2023",
    url: "https://www.canlii.org/",
    imageUrl: "https://images.unsplash.com/photo-1589994965851-a8f479c573a9?q=80&w=800",
    description: "A comprehensive guide to recent changes in Canadian immigration law and how they might affect newcomers and current residents.",
    category: "Immigration",
    readTime: "8 min",
    date: "Apr 15, 2023",
    featured: true
  },
  {
    title: "The Impact of Recent Supreme Court Decisions on Criminal Law",
    url: "https://laws-lois.justice.gc.ca/eng/acts/c-46/",
    imageUrl: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=800",
    description: "Analysis of recent landmark Supreme Court rulings and their implications for criminal proceedings in Canada.",
    category: "Criminal Law",
    readTime: "12 min",
    date: "May 22, 2023",
    featured: true
  },
  {
    title: "Digital Privacy Rights: What Canadians Need to Know",
    url: "https://criminalnotebook.ca/index.php/Main_Page",
    imageUrl: "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=800",
    description: "Exploring the intersection of technology and privacy law in Canada, including recent legislative changes and court decisions.",
    category: "Privacy Law",
    readTime: "10 min",
    date: "Jun 03, 2023",
    featured: true
  },
  {
    title: "Employment Law Updates: What Employers and Employees Should Know",
    url: "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/laws.html",
    imageUrl: "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?q=80&w=800",
    description: "Recent developments in Canadian employment law, covering remote work, health and safety regulations, and employee rights.",
    category: "Employment",
    readTime: "7 min",
    date: "Jul 12, 2023",
    featured: true
  },
  {
    title: "Understanding Family Law Mediation",
    url: "https://www.canlii.org/info/about.html",
    imageUrl: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=800",
    description: "A guide to the mediation process in family law disputes and how it can provide alternatives to litigation.",
    category: "Family Law",
    readTime: "9 min",
    date: "Aug 05, 2023"
  },
  {
    title: "Property Law: Understanding Easements and Rights of Way",
    url: "https://www.fct-cf.gc.ca/en/court-files-and-decisions/court-files",
    imageUrl: "https://images.unsplash.com/photo-1593115057322-e94b77572f20?q=80&w=800",
    description: "Explaining the complex legal concepts of easements and rights of way in Canadian property law.",
    category: "Property Law",
    readTime: "6 min",
    date: "Sep 18, 2023"
  },
  {
    title: "Corporate Governance: Best Practices for Compliance",
    url: "https://guides.law.byu.edu/canada",
    imageUrl: "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?q=80&w=800",
    description: "Corporate governance guidelines and compliance requirements for Canadian businesses.",
    category: "Corporate Law",
    readTime: "11 min",
    date: "Oct 07, 2023"
  },
  {
    title: "Environmental Law: Recent Developments and Case Studies",
    url: "https://guides.library.harvard.edu/law/canada",
    imageUrl: "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?q=80&w=800",
    description: "Analysis of significant environmental law cases and regulatory changes affecting Canadian industries.",
    category: "Environmental",
    readTime: "14 min",
    date: "Nov 22, 2023"
  },
  {
    title: "Legal Ethics in the Digital Age",
    url: "https://flsc.ca/",
    imageUrl: "https://images.unsplash.com/photo-1436450412740-6b988f486c6b?q=80&w=800",
    description: "Exploring ethical considerations for legal professionals in the era of AI, social media, and digital client interactions.",
    category: "Legal Ethics",
    readTime: "8 min",
    date: "Dec 10, 2023"
  },
];

export default function BlogsPage() {
  const [api, setApi] = useState<CarouselApi>();
  const [current, setCurrent] = useState(0);
  const [count, setCount] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  const featuredBlogs = lawResources.filter(blog => blog.featured);
  
  useEffect(() => {
    if (!api) {
      return;
    }
    
    setCount(api.scrollSnapList().length);
    setCurrent(api.selectedScrollSnap() + 1);

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap() + 1);
    });
    
    // Setup autoplay
    const setupAutoplay = () => {
      timerRef.current = setInterval(() => {
        api.scrollNext();
      }, 5000); // Change slide every 5 seconds
    };
    
    setupAutoplay();
    
    // Clear interval when component unmounts
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [api]);

  // Pause autoplay on hover
  const pauseAutoplay = () => {
    if (timerRef.current) clearInterval(timerRef.current);
  };

  // Resume autoplay when mouse leaves
  const resumeAutoplay = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      api?.scrollNext();
    }, 5000);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-16 pb-20 overflow-hidden">
      <div className="relative">
        <div className="absolute inset-0 -z-10 opacity-5">
          <ParticlesBackground />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
              className="bg-primary/10 rounded-full p-4 w-24 h-24 flex items-center justify-center mx-auto mb-6"
            >
              <BookOpen className="h-12 w-12 text-primary" />
            </motion.div>
            <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80">Law Insights</h1>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Stay informed with expert analysis and updates on Canadian legal matters
            </p>
          </motion.div>

          {/* Featured Carousel */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mb-20 relative"
            onMouseEnter={pauseAutoplay}
            onMouseLeave={resumeAutoplay}
          >
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold border-l-4 border-primary pl-4">Featured Articles</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {current} / {count}
                </span>
              </div>
            </div>
            
            <Carousel
              opts={{
                align: "start",
                loop: true,
              }}
              setApi={setApi}
              className="w-full"
            >
              <CarouselContent>
                {featuredBlogs.map((blog, index) => (
                  <CarouselItem key={index} className="md:basis-2/3 lg:basis-1/2">
                    <div className="group relative overflow-hidden rounded-xl border border-border/50 bg-card/80 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 h-[400px]">
                      <div className="absolute inset-0 z-0">
                        <Image
                          src={blog.imageUrl}
                          alt={blog.title}
                          fill
                          className="object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent"></div>
                      </div>
                      
                      <div className="absolute top-4 left-4 z-10">
                        <Badge className="bg-primary/90 hover:bg-primary text-white">{blog.category}</Badge>
                      </div>
                      
                      <div className="absolute bottom-0 left-0 right-0 p-6 z-10">
                        <div className="flex items-center space-x-2 text-white/80 text-sm mb-3">
                          <Clock className="w-4 h-4" />
                          <span>{blog.readTime}</span>
                          <span>•</span>
                          <span>{blog.date}</span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-primary transition-colors">
                          {blog.title}
                        </h3>
                        <p className="text-white/70 mb-5 line-clamp-2">
                          {blog.description}
                        </p>
                        <Link
                          href={blog.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-primary hover:text-primary/80 font-medium transition-colors"
                        >
                          Read Article
                          <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                        </Link>
                      </div>
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              
              <div className="absolute -right-4 top-1/2 -translate-y-1/2 flex justify-end gap-2">
                <CarouselPrevious 
                  className="relative -left-4 h-10 w-10 rounded-full bg-background/90 backdrop-blur-sm border-primary/20 shadow-md"
                  variant="outline"
                />
                <CarouselNext 
                  className="relative -right-4 h-10 w-10 rounded-full bg-background/90 backdrop-blur-sm border-primary/20 shadow-md"
                  variant="outline"
                />
              </div>
            </Carousel>
          </motion.div>

          {/* All Blogs Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4 }}
          >
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold border-l-4 border-primary pl-4">All Articles</h2>
              <Button variant="ghost" className="text-muted-foreground hover:text-primary group">
                View all
                <ChevronRight className="ml-1 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {lawResources.map((resource, index) => (
                <motion.div
                  key={resource.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.05 }}
                  whileHover={{ y: -5 }}
                  className="h-full"
                >
                  <Link
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block h-full group"
                  >
                    <div className="bg-card/80 backdrop-blur-sm rounded-lg border border-border/50 overflow-hidden transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 h-full flex flex-col">
                      <div className="relative h-48 w-full overflow-hidden">
                        <Image
                          src={resource.imageUrl}
                          alt={resource.title}
                          fill
                          className="object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                        {resource.category && (
                          <div className="absolute top-3 left-3">
                            <Badge variant="secondary" className="bg-background/80 backdrop-blur-sm">
                              {resource.category}
                            </Badge>
                          </div>
                        )}
                      </div>
                      <div className="p-5 flex flex-col flex-grow">
                        {(resource.readTime || resource.date) && (
                          <div className="flex items-center space-x-2 text-muted-foreground text-xs mb-3">
                            {resource.readTime && (
                              <>
                                <Clock className="w-3 h-3" />
                                <span>{resource.readTime}</span>
                              </>
                            )}
                            {resource.readTime && resource.date && <span>•</span>}
                            {resource.date && <span>{resource.date}</span>}
                          </div>
                        )}
                        <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors line-clamp-2">
                          {resource.title}
                        </h3>
                        <p className="text-sm text-muted-foreground mb-4 line-clamp-3 flex-grow">
                          {resource.description}
                        </p>
                        <div className="flex items-center text-primary text-sm font-medium mt-auto">
                          <span>Read more</span>
                          <ExternalLink className="ml-2 h-3 w-3 group-hover:translate-x-1 transition-transform" />
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="mt-12 text-center"
            >
              <Button 
                size="lg" 
                className="bg-primary text-primary-foreground group shadow-lg shadow-primary/20"
                onClick={() => window.location.href = "https://www.canlii.org/"}
              >
                Explore More Articles
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}