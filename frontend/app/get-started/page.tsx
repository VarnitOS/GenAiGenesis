"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { ParticlesBackground } from "@/components/particles-background";
import { CheckIcon, ChevronRightIcon, Scale, Shield, Gavel } from "lucide-react";
import { FormEvent } from "react";

export default function GetStartedPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    caseType: "",
    urgency: "",
    description: "",
    documents: [] as File[]
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulating form submission
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
    }, 1500);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData({
        ...formData,
        documents: Array.from(e.target.files)
      });
    }
  };

  const updateFormData = (field: string, value: string) => {
    setFormData({
      ...formData,
      [field]: value
    });
  };

  const nextStep = () => {
    setStep(step + 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const prevStep = () => {
    setStep(step - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const caseTypes = [
    "Corporate Law",
    "Family Law",
    "Criminal Defense",
    "Intellectual Property",
    "Real Estate Law",
    "Employment Law",
    "Immigration Law",
    "Personal Injury",
    "Tax Law",
    "Other"
  ];

  const urgencyLevels = [
    "Immediate (24-48 hours)",
    "Urgent (3-5 days)",
    "Standard (1-2 weeks)",
    "Not time-sensitive"
  ];

  const steps = [
    { 
      title: "Personal Information", 
      description: "Tell us who you are so we can contact you",
      icon: <Shield className="h-8 w-8" />
    },
    { 
      title: "Case Details", 
      description: "Help us understand your legal needs",
      icon: <Gavel className="h-8 w-8" />
    },
    { 
      title: "Additional Information", 
      description: "Provide any other relevant details",
      icon: <Scale className="h-8 w-8" />
    }
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background/80 to-accent/20 pt-20 pb-20">
      <div className="relative">
        <div className="absolute inset-0 -z-10 opacity-5">
          <ParticlesBackground />
        </div>
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {success ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="bg-card/80 backdrop-blur-sm p-10 rounded-2xl border border-green-500/50 text-center shadow-xl"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
                className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 text-green-600"
              >
                <CheckIcon className="h-10 w-10" />
              </motion.div>
              <h2 className="text-3xl font-bold mb-4">Application Submitted!</h2>
              <p className="text-lg text-muted-foreground mb-8">
                Thank you for reaching out to LAW-DER. Our team will review your information and contact you within 24 hours to discuss the next steps.
              </p>
              <p className="text-sm text-muted-foreground mb-6">
                A confirmation email has been sent to {formData.email}
              </p>
              <Button 
                onClick={() => window.location.href = "/"}
                className="bg-primary hover:bg-primary/90"
              >
                Return to Home
              </Button>
            </motion.div>
          ) : (
            <>
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-center mb-10"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
                  className="bg-primary/10 rounded-full p-4 w-24 h-24 flex items-center justify-center mx-auto mb-6"
                >
                  <Scale className="h-12 w-12 text-primary" />
                </motion.div>
                <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80">
                  Get Started with LAW-DER
                </h1>
                <p className="mt-4 text-lg text-muted-foreground">
                  Complete the form below to begin your legal journey
                </p>
              </motion.div>
  
              {/* Progress Steps */}
              <div className="mb-10">
                <div className="flex items-center justify-between mx-auto max-w-3xl">
                  {steps.map((s, i) => (
                    <div key={i} className="flex flex-col items-center relative">
                      <motion.div 
                        initial={{ opacity: 0.3 }}
                        animate={{ opacity: step > i ? 1 : step === i+1 ? 1 : 0.3 }}
                        className={`w-16 h-16 rounded-full flex items-center justify-center ${
                          step > i+1 ? 'bg-primary text-white' : 
                          step === i+1 ? 'bg-primary/20 border-2 border-primary text-primary' : 
                          'bg-card border border-border text-muted-foreground'
                        } mb-2 z-10`}
                      >
                        {step > i+1 ? (
                          <CheckIcon className="h-6 w-6" />
                        ) : (
                          s.icon
                        )}
                      </motion.div>
                      <motion.p 
                        initial={{ opacity: 0.5 }}
                        animate={{ opacity: step === i+1 || step > i+1 ? 1 : 0.5 }}
                        className={`text-xs font-medium ${step === i+1 ? 'text-primary' : ''}`}
                      >
                        {s.title}
                      </motion.p>
                      {i < steps.length - 1 && (
                        <div className="absolute left-[calc(50%+2rem)] top-8 w-[calc(100%-4rem)] h-0.5 bg-border">
                          <motion.div 
                            initial={{ width: "0%" }}
                            animate={{ width: step > i+1 ? "100%" : "0%" }}
                            transition={{ duration: 0.5 }}
                            className="h-full bg-primary"
                          ></motion.div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
  
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-card/80 backdrop-blur-sm p-8 rounded-xl border border-border/50 shadow-lg"
              >
                <form onSubmit={handleSubmit} className="space-y-6">
                  {step === 1 && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-semibold mb-6">Personal Information</h2>
                      <div className="space-y-4">
                        <div>
                          <label htmlFor="name" className="block text-sm font-medium mb-2">
                            Full Name*
                          </label>
                          <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => updateFormData("name", e.target.value)}
                            placeholder="John Doe"
                            required
                          />
                        </div>
                        <div>
                          <label htmlFor="email" className="block text-sm font-medium mb-2">
                            Email Address*
                          </label>
                          <Input
                            id="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => updateFormData("email", e.target.value)}
                            placeholder="john@example.com"
                            required
                          />
                        </div>
                        <div>
                          <label htmlFor="phone" className="block text-sm font-medium mb-2">
                            Phone Number
                          </label>
                          <Input
                            id="phone"
                            value={formData.phone}
                            onChange={(e) => updateFormData("phone", e.target.value)}
                            placeholder="(123) 456-7890"
                          />
                        </div>
                      </div>
                    </motion.div>
                  )}
  
                  {step === 2 && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-semibold mb-6">Case Details</h2>
                      <div className="space-y-4">
                        <div>
                          <label htmlFor="caseType" className="block text-sm font-medium mb-2">
                            Type of Legal Assistance*
                          </label>
                          <Select 
                            value={formData.caseType} 
                            onValueChange={(value) => updateFormData("caseType", value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select case type" />
                            </SelectTrigger>
                            <SelectContent>
                              {caseTypes.map((type) => (
                                <SelectItem key={type} value={type}>
                                  {type}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <label htmlFor="urgency" className="block text-sm font-medium mb-2">
                            Urgency Level*
                          </label>
                          <Select 
                            value={formData.urgency} 
                            onValueChange={(value) => updateFormData("urgency", value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select urgency level" />
                            </SelectTrigger>
                            <SelectContent>
                              {urgencyLevels.map((level) => (
                                <SelectItem key={level} value={level}>
                                  {level}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <label htmlFor="description" className="block text-sm font-medium mb-2">
                            Brief Description of Your Case*
                          </label>
                          <Textarea
                            id="description"
                            value={formData.description}
                            onChange={(e) => updateFormData("description", e.target.value)}
                            placeholder="Please describe your legal situation in a few sentences..."
                            rows={4}
                            required
                          />
                        </div>
                      </div>
                    </motion.div>
                  )}
  
                  {step === 3 && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-semibold mb-6">Additional Information</h2>
                      <div className="space-y-4">
                        <div>
                          <label htmlFor="documents" className="block text-sm font-medium mb-2">
                            Upload Relevant Documents (Optional)
                          </label>
                          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed border-border rounded-md">
                            <div className="space-y-1 text-center">
                              <svg className="mx-auto h-12 w-12 text-muted-foreground" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                              </svg>
                              <div className="flex text-sm text-muted-foreground">
                                <label htmlFor="file-upload" className="relative cursor-pointer bg-background rounded-md font-medium text-primary hover:text-primary/80 focus-within:outline-none">
                                  <span>Upload files</span>
                                  <input
                                    id="file-upload"
                                    name="file-upload"
                                    type="file"
                                    multiple
                                    className="sr-only"
                                    onChange={handleFileChange}
                                  />
                                </label>
                                <p className="pl-1">or drag and drop</p>
                              </div>
                              <p className="text-xs text-muted-foreground">
                                PDF, DOC, DOCX, JPG, PNG up to 10MB each
                              </p>
                            </div>
                          </div>
                          {formData.documents.length > 0 && (
                            <div className="mt-2">
                              <p className="text-sm font-medium">Uploaded files:</p>
                              <ul className="mt-1 text-sm text-muted-foreground">
                                {formData.documents.map((file, index) => (
                                  <li key={index}>{file.name}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        <div className="border-t border-border pt-4 mt-6">
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              className="h-4 w-4 text-primary border-border rounded focus:ring-primary"
                              required
                            />
                            <span className="ml-2 text-sm text-muted-foreground">
                              I agree to the{" "}
                              <a href="#" className="text-primary hover:underline">
                                Terms of Service
                              </a>{" "}
                              and{" "}
                              <a href="#" className="text-primary hover:underline">
                                Privacy Policy
                              </a>
                            </span>
                          </label>
                        </div>
                      </div>
                    </motion.div>
                  )}
  
                  <div className="flex justify-between mt-8 pt-6 border-t border-border">
                    {step > 1 ? (
                      <Button 
                        type="button" 
                        onClick={prevStep}
                        variant="outline"
                      >
                        Back
                      </Button>
                    ) : (
                      <div></div>
                    )}
                    
                    {step < 3 ? (
                      <Button 
                        type="button" 
                        onClick={nextStep}
                        className="bg-primary text-primary-foreground"
                      >
                        Continue <ChevronRightIcon className="ml-2 h-4 w-4" />
                      </Button>
                    ) : (
                      <Button 
                        type="submit"
                        className="bg-primary text-primary-foreground"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Processing...
                          </>
                        ) : (
                          "Submit Application"
                        )}
                      </Button>
                    )}
                  </div>
                </form>
              </motion.div>
            </>
          )}
        </div>
      </div>
    </main>
  );
} 