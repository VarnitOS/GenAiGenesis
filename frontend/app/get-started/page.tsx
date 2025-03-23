"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ParticlesBackground } from "@/components/particles-background";
import { Send, BrainCircuit, Loader2, Scale, BookOpen, RotateCw, AlertTriangle, XCircle, ExternalLink, Clock, FileText, Link2, ChevronDown, ChevronUp } from "lucide-react";
import axios from "axios";
import ReactMarkdown from 'react-markdown';

// Define API endpoint and configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
const API_TIMEOUT = 550000; // 2 minutes, more reasonable than the extremely large number

type Message = {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp?: Date;
  error?: boolean;
  metadata?: {
    executionTime?: number;
    sources?: {
      title: string;
      url: string;
      snippet: string;
      source: string;
    }[];
    researchSynthesis?: string;
    rawAnalysis?: string;
  };
};

export default function GetStartedPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [expandedMessage, setExpandedMessage] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [isServerAvailable, setIsServerAvailable] = useState(true);
  const connectionCheckRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to the bottom of the chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input field when component loads
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Reset API error after 5 seconds
  useEffect(() => {
    if (apiError) {
      const timer = setTimeout(() => {
        setApiError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [apiError]);

  const toggleMessageExpansion = (id: string) => {
    if (expandedMessage === id) {
      setExpandedMessage(null);
      setExpandedSection(null);
    } else {
      setExpandedMessage(id);
      setExpandedSection('synthesis');
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)} seconds`;
    } else {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes} min ${remainingSeconds.toFixed(0)} sec`;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Clear any previous API errors
    setApiError(null);

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Improved error handling and connection logic
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

      // Check server availability first with a health check
      try {
        await axios.get(`${API_URL}/health`, { 
          timeout: 5000 // Quick timeout just for the health check
        });
      } catch (healthError) {
        // If health check fails, we know the server is not reachable
        throw new Error('CONNECT_ERROR');
      }

      // If health check passes, proceed with the main request
      const response = await axios.post(
        `${API_URL}/api/query`, 
        { query: input },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          signal: controller.signal,
          timeout: API_TIMEOUT,
        }
      );

      clearTimeout(timeoutId);

      // Improved data validation
      const data = response.data;
      if (!data) {
        throw new Error('Empty response received');
      }

      if (data.final_response) {
        // Add assistant response to chat
        const assistantMessage: Message = {
          id: data.query_id || Date.now().toString() + '-response',
          content: data.final_response.response || 'Sorry, I couldn\'t process your request',
          role: 'assistant',
          timestamp: new Date(),
          metadata: {
            executionTime: data.execution_time,
            sources: data.research?.internet_results || [],
            researchSynthesis: data.research?.synthesis || '',
            rawAnalysis: data.research?.research_focus?.raw_analysis || '',
          }
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else if (data.error) {
        // Handle explicit error response from backend
        throw new Error(data.error);
      } else {
        throw new Error('Invalid response format from API');
      }
    } catch (error: any) {
      console.error('API Error:', error);
      
      // More specific error handling with better messages
      let errorMessage = 'Sorry, there was an error processing your request. Please try again.';
      let errorType = 'UNKNOWN';
      
      if (error.message === 'CONNECT_ERROR' || !navigator.onLine) {
        errorMessage = 'Could not connect to the legal research service. Please check your internet connection and ensure the backend is running.';
        errorType = 'CONNECTION';
      } else if (error.name === 'AbortError' || error.code === 'ECONNABORTED') {
        errorMessage = 'The request took too long to complete. Please try again or refine your question.';
        errorType = 'TIMEOUT';
      } else if (error.response) {
        // Server responded with a non-2xx status
        if (error.response.status === 429) {
          errorMessage = 'Too many requests. Please wait a moment before trying again.';
          errorType = 'RATE_LIMIT';
        } else if (error.response.status === 404) {
          errorMessage = 'API endpoint not found. Please check the backend configuration.';
          errorType = 'NOT_FOUND';
        } else {
          errorMessage = `Server error (${error.response.status}): ${error.response.data?.error || 'Unknown error'}`;
          errorType = 'SERVER';
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response received from the server. The request may still be processing.';
        errorType = 'NO_RESPONSE';
      }
      
      setApiError(`Error: ${errorMessage}`);
      
      // Add error message as a system message
      const errorResponseMessage: Message = {
        id: Date.now().toString() + '-error',
        content: errorMessage,
        role: 'assistant',
        timestamp: new Date(),
        error: true,
      };
      setMessages((prev) => [...prev, errorResponseMessage]);
      
      // For connection errors, keep checking connection periodically
      if (errorType === 'CONNECTION') {
        startConnectionCheck();
      }
    } finally {
      setIsLoading(false);
      // Focus back on input field after response
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  const checkServerConnection = async () => {
    try {
      await axios.get(`${API_URL}/health`, { timeout: 3000 });
      setIsServerAvailable(true);
      if (connectionCheckRef.current) {
        clearInterval(connectionCheckRef.current);
        connectionCheckRef.current = null;
      }
    } catch (error) {
      setIsServerAvailable(false);
    }
  };

  const startConnectionCheck = () => {
    if (!connectionCheckRef.current) {
      // Check immediately
      checkServerConnection();
      // Then set up interval
      connectionCheckRef.current = setInterval(checkServerConnection, 5000);
    }
  };

  // Check connection when component mounts
  useEffect(() => {
    checkServerConnection();
    return () => {
      if (connectionCheckRef.current) {
        clearInterval(connectionCheckRef.current);
      }
    };
  }, []);

  const suggestionTopics = [
    "What are my rights as a tenant?",
    "How do I start a small business LLC?",
    "What happens during a divorce proceeding?",
    "Explain copyright infringement"
  ];

  const renderMessage = (message: Message) => {
    if (message.role === 'assistant') {
      return (
        <div className="message assistant-message p-4 rounded-lg bg-gray-800/80 backdrop-blur-sm max-w-[85%]">
          <div className="prose prose-invert prose-sm max-w-none text-gray-100">
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          </div>
          
          {message.metadata?.executionTime && (
            <div className="text-xs text-gray-400 mt-2">
              Processed in {formatTime(message.metadata.executionTime)}
            </div>
          )}
        </div>
      );
    }
    
    return (
      <div className="message user-message p-4 rounded-lg bg-blue-600/80 backdrop-blur-sm max-w-[85%] self-end">
        <p className="text-white">{message.content}</p>
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-slate-900 to-gray-950 pt-20 pb-20 text-white">
      {/* Subtle law-themed pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff15_1px,transparent_1px),linear-gradient(to_bottom,#ffffff15_1px,transparent_1px)] bg-[size:40px_40px] opacity-5"></div>
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-blue-600/5"></div>
      
      <div className="relative">
        <div className="absolute inset-0 -z-10 opacity-10">
          <ParticlesBackground />
        </div>
        
        {/* Decorative glow elements */}
        <div className="fixed top-1/4 -left-20 w-80 h-80 bg-blue-600/20 blur-[120px] rounded-full pointer-events-none"></div>
        <div className="fixed bottom-1/4 -right-20 w-80 h-80 bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none"></div>
        
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
            <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="text-center mb-12"
          >
            <div className="flex justify-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ 
                  type: "spring", 
                  stiffness: 200, 
                  damping: 20, 
                  delay: 0.2 
                }}
                className="relative"
              >
                <div className="absolute inset-0 rounded-full blur-2xl opacity-60 bg-gradient-to-r from-blue-600/40 to-indigo-600/40 -z-10"></div>
                <div className="relative flex items-center justify-center w-32 h-32">
                  {/* Animated rings */}
                  <div className="absolute inset-0 rounded-full border-2 border-indigo-400/20 animate-[ping_4s_cubic-bezier(0,0,0.2,1)_infinite]"></div>
                  <div className="absolute inset-[5px] rounded-full border-2 border-indigo-400/30 animate-[ping_4s_cubic-bezier(0,0,0.2,1)_infinite_1s]"></div>
                  
                  {/* Main icon container */}
                  <div className="relative z-10 bg-gradient-to-br from-blue-500 to-indigo-700 rounded-full p-6 shadow-[0_0_30px_rgba(79,70,229,0.4)]">
                    <BrainCircuit className="h-16 w-16 text-white drop-shadow-lg" />
                  </div>
                </div>
              </motion.div>
            </div>
            
            <motion.h1 
              className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-indigo-200 to-blue-300 mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.7 }}
            >
              LAW-DER Assistant
            </motion.h1>
            
            <motion.p 
              className="mt-4 text-xl text-blue-100/90 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.7 }}
            >
              Ask any legal question and receive professional, research-backed answers
            </motion.p>
          </motion.div>

          {/* API Error Banner */}
          {apiError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-4 bg-red-900/50 border border-red-700 text-red-200 px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <AlertTriangle className="h-5 w-5 text-red-300" />
              <span className="text-sm">{apiError}</span>
            </motion.div>
          )}

          {/* Chat container */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="relative rounded-2xl overflow-hidden"
          >
            {/* Glass border glow effect */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-600/30 via-indigo-600/20 to-blue-600/30 blur-xl"></div>
            
            {/* Glass card */}
            <div className="relative backdrop-blur-lg border border-white/10 shadow-2xl rounded-2xl flex flex-col h-[600px] overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-slate-900/90 to-gray-950/95"></div>
              
              {/* Chat header */}
              <div className="relative bg-gradient-to-r from-slate-800 to-slate-900 py-4 px-6 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-lg mr-3 shadow-lg">
                    <Scale className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">LAW-DER Legal Research</h3>
                    <p className="text-xs text-slate-400">Powered by advanced AI legal analysis</p>
                        </div>
                    </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs font-medium text-green-400">Connected to {new URL(API_URL).host}</span>
                </div>
              </div>
  
              {/* Messages area */}
              <div className="relative flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-center">
                    <div className="max-w-md space-y-6">
                      <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl p-8 backdrop-blur-sm border border-white/10 shadow-2xl">
                        <div className="relative flex items-center justify-center mx-auto mb-6">
                          <div className="absolute inset-0 rounded-full blur-md bg-blue-600/20"></div>
                          <div className="bg-gradient-to-br from-blue-500/20 to-indigo-600/20 rounded-full p-3 w-18 h-18 flex items-center justify-center border border-white/10">
                            <Scale className="h-8 w-8 text-blue-200" />
                          </div>
                        </div>
                        <h3 className="text-xl font-medium text-white mb-3">How can I assist you today?</h3>
                        <p className="text-slate-300 mb-6">
                          I can provide information and insights on a wide range of legal topics, drawing from extensive research.
                        </p>
                        
                        <div className="space-y-3">
                          <p className="text-sm text-blue-200 font-medium">Popular questions:</p>
                          <div className="flex flex-wrap gap-2 justify-center">
                            {suggestionTopics.map((topic, index) => (
                              <button
                                key={index}
                                onClick={() => setInput(topic)}
                                className="text-xs bg-gradient-to-r from-slate-800 to-slate-900 hover:from-blue-900/30 hover:to-indigo-900/30 text-slate-300 hover:text-white px-3 py-2 rounded-lg border border-slate-700/80 hover:border-blue-500/30 transition-all duration-200 shadow-md"
                              >
                                {topic}
                              </button>
                            ))}
                        </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.role === 'assistant' && (
                        <div className="flex-shrink-0 mr-3">
                          <div className={`p-2 rounded-lg shadow-lg ${
                            message.error 
                              ? 'bg-gradient-to-br from-red-600 to-red-800 shadow-red-900/20' 
                              : 'bg-gradient-to-br from-blue-600 to-indigo-700 shadow-indigo-900/20'
                          }`}>
                            {message.error ? (
                              <XCircle className="h-5 w-5 text-white" />
                            ) : (
                              <Scale className="h-5 w-5 text-white" />
                            )}
                          </div>
                        </div>
                      )}
                      
                      <div 
                        className={`max-w-[75%] rounded-xl px-5 py-4 shadow-lg ${
                          message.role === 'user' 
                            ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-tr-none shadow-blue-900/30' 
                            : message.error
                              ? 'bg-gradient-to-r from-red-950/70 to-red-900/70 text-red-100 rounded-tl-none border border-red-700/50'
                              : 'bg-gradient-to-r from-slate-800 to-slate-900 text-slate-100 rounded-tl-none border border-slate-700'
                        }`}
                      >
                        {renderMessage(message)}
                        
                        {/* Show metadata for assistant messages */}
                        {message.role === 'assistant' && message.metadata && !message.error && (
                          <div className="mt-4">
                            {/* Processing time tag */}
                            {message.metadata.executionTime && (
                              <div className="flex items-center gap-1 mt-2 mb-4">
                                <div className="inline-flex items-center gap-1 bg-slate-700/50 rounded-full px-2 py-0.5 text-xs text-slate-300">
                                  <Clock className="h-3 w-3" />
                                  <span>Processed in {formatTime(message.metadata.executionTime)}</span>
                        </div>
                      </div>
                            )}
                            
                            {/* Expandable details button */}
                            <div className="border-t border-slate-700/50 pt-3 mt-3">
                              <button
                                onClick={() => toggleMessageExpansion(message.id)}
                                className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                              >
                                {expandedMessage === message.id ? (
                                  <>
                                    <ChevronUp className="h-3 w-3" />
                                    <span>Hide research details</span>
                                  </>
                                ) : (
                                  <>
                                    <ChevronDown className="h-3 w-3" />
                                    <span>Show research details</span>
                                  </>
                                )}
                              </button>
                            </div>
                            
                            {/* Expanded research details */}
                            {expandedMessage === message.id && (
                              <div className="mt-4 pt-3 border-t border-slate-700/30 space-y-4">
                                {/* Section tabs */}
                                <div className="flex space-x-2 border-b border-slate-700/30">
                                  <button 
                                    className={`px-3 py-1 text-xs rounded-t-lg ${expandedSection === 'synthesis' ? 'bg-indigo-900/40 text-indigo-200 border-b-2 border-indigo-500' : 'bg-slate-800/30 text-slate-400 hover:text-slate-300'}`}
                                    onClick={() => toggleSection('synthesis')}
                                  >
                                    Full Analysis
                                  </button>
                                  <button 
                                    className={`px-3 py-1 text-xs rounded-t-lg ${expandedSection === 'sources' ? 'bg-indigo-900/40 text-indigo-200 border-b-2 border-indigo-500' : 'bg-slate-800/30 text-slate-400 hover:text-slate-300'}`}
                                    onClick={() => toggleSection('sources')}
                                  >
                                    Sources ({message.metadata.sources?.length || 0})
                                  </button>
                                  <button 
                                    className={`px-3 py-1 text-xs rounded-t-lg ${expandedSection === 'raw' ? 'bg-indigo-900/40 text-indigo-200 border-b-2 border-indigo-500' : 'bg-slate-800/30 text-slate-400 hover:text-slate-300'}`}
                                    onClick={() => toggleSection('raw')}
                                  >
                                    Raw Analysis
                                  </button>
                                </div>
                                
                                {/* Research synthesis */}
                                {expandedSection === 'synthesis' && message.metadata.researchSynthesis && (
                                  <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700/50 text-sm text-slate-300 max-h-60 overflow-y-auto whitespace-pre-wrap">
                                    <div className="flex items-center gap-1 mb-2 text-indigo-200">
                                      <FileText className="h-4 w-4" />
                                      <span className="font-medium">Complete Legal Analysis</span>
                                    </div>
                                    {message.metadata.researchSynthesis}
                                  </div>
                                )}
                                
                                {/* Sources */}
                                {expandedSection === 'sources' && message.metadata.sources && (
                                  <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700/50 text-sm text-slate-300 max-h-60 overflow-y-auto">
                                    <div className="flex items-center gap-1 mb-3 text-indigo-200">
                                      <Link2 className="h-4 w-4" />
                                      <span className="font-medium">Reference Sources</span>
                              </div>
                                    
                                    <div className="space-y-3">
                                      {message.metadata.sources.map((source, index) => (
                                        <div key={index} className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/30">
                                          <div className="font-medium text-blue-300 mb-1">{source.title}</div>
                                          <p className="text-xs text-slate-400 mb-2">{source.snippet}</p>
                                          <div className="flex justify-between items-center">
                                            <span className="text-xs text-slate-500">{source.source}</span>
                                            <a 
                                              href={source.url} 
                                              target="_blank" 
                                              rel="noopener noreferrer"
                                              className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                                            >
                                              <span>Visit</span>
                                              <ExternalLink className="h-3 w-3" />
                                            </a>
                            </div>
                          </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Raw analysis */}
                                {expandedSection === 'raw' && message.metadata.rawAnalysis && (
                                  <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700/50 text-sm text-slate-300 max-h-60 overflow-y-auto whitespace-pre-wrap font-mono text-xs">
                                    <div className="flex items-center gap-1 mb-2 text-indigo-200 font-sans text-sm">
                                      <FileText className="h-4 w-4" />
                                      <span className="font-medium">Raw Analysis Data</span>
                                    </div>
                                    {message.metadata.rawAnalysis}
                                  </div>
                                )}
                            </div>
                          )}
                        </div>
                        )}
                        
                        {message.timestamp && (
                          <div className="mt-2 text-right">
                            <span className={`text-xs ${message.error ? 'text-red-400/70' : message.role === 'user' ? 'text-blue-200/70' : 'text-slate-400/70'}`}>
                              {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </span>
                        </div>
                        )}
                      </div>
                      
                      {message.role === 'user' && (
                        <div className="flex-shrink-0 ml-3">
                          <div className="bg-gradient-to-br from-slate-700 to-slate-800 p-2 rounded-lg shadow-lg">
                            <div className="h-5 w-5 rounded-full bg-gradient-to-br from-blue-200 to-blue-400 flex items-center justify-center text-slate-800 text-xs font-bold">
                              Y
                            </div>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))
                )}
                
                {isLoading && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="flex-shrink-0 mr-3">
                      <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2 rounded-lg shadow-lg shadow-indigo-900/20">
                        <Scale className="h-5 w-5 text-white" />
                      </div>
                    </div>
                    <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl rounded-tl-none px-5 py-4 border border-slate-700 shadow-lg">
                      <div className="flex flex-col">
                        <div className="flex items-center gap-3">
                          <RotateCw className="h-4 w-4 text-blue-400 animate-spin" />
                          <span className="text-sm text-slate-300">Researching legal information...</span>
                        </div>
                        <p className="text-xs text-slate-400 mt-2">
                          Processing complex legal queries may take 60-90 seconds
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>
              
              {/* Input area */}
              <div className="relative border-t border-slate-800 bg-gradient-to-r from-slate-900 to-slate-950 p-4">
                <form onSubmit={handleSubmit} className="relative">
                  <Input
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your legal question here..."
                    disabled={isLoading}
                    className="pr-24 py-6 bg-slate-800/50 text-white border-slate-700 focus:border-blue-500/60 placeholder:text-slate-500 rounded-xl shadow-inner shadow-black/20"
                  />
                  <div className="absolute right-1.5 top-1.5 bottom-1.5 flex">
                    {input.trim() && (
                      <Button 
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-lg px-4 text-white flex items-center gap-2 shadow-lg shadow-blue-900/20 transition-all duration-200"
                      >
                        <span>{isLoading ? 'Sending...' : 'Send'}</span>
                        {isLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </Button>
                    )}
                  </div>
                </form>
              </div>
            </div>
              </motion.div>
          
          {/* Connection Status */}
          <div className="mt-4 flex justify-center">
            <div className="flex items-center gap-2 bg-slate-900/70 backdrop-blur-sm px-3 py-1 rounded-full border border-slate-700/30">
              <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
              <span className="text-xs text-slate-400">
                {isLoading 
                  ? 'Processing request...' 
                  : `Connected to ${new URL(API_URL).hostname}`
                }
              </span>
            </div>
          </div>
          
          {/* Footer */}
          <div className="mt-4 text-center">
            <div className="inline-flex items-center justify-center gap-1 mb-2 bg-slate-900/50 backdrop-blur-sm px-4 py-1 rounded-full border border-slate-700/50">
              <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
              <p className="text-xs text-slate-400">Secure & confidential</p>
            </div>
            <p className="text-sm text-slate-500 mb-2">
              Responses are for informational purposes only and do not constitute legal advice.
            </p>
            <p className="text-xs text-slate-600">
              LAW-DER Legal Technologies | © {new Date().getFullYear()}
            </p>
          </div>
        </div>
      </div>
    </main>
  );
} 