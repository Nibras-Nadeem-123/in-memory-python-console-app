import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Phase 2 Todo App',
  description: 'Spec-Driven Todo System - Phase 2',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="min-h-screen">
          <header className="py-4 text-white bg-blue-600 shadow-md">
            <div className="max-w-4xl px-4 mx-auto">
              <h1 className="text-2xl font-bold">Phase 2 Todo App</h1>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
