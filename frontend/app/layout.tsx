import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from "@/components/theme-provider";
import { Navbar } from "@/components/navbar";
import { SplashScreen } from "@/components/splash-screen";
import { SplashProvider } from "@/components/splash-context";

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'LAW-DER | AI-Powered Legal Assistance',
  description: 'Your 24/7 AI-powered legal companion making justice accessible to all',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <SplashProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
          >
            <SplashScreen />
            <Navbar />
            {children}
          </ThemeProvider>
        </SplashProvider>
      </body>
    </html>
  );
}