// Layout.jsx
import React from 'react';
import { Sidebar } from '../Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col lg:full">
        <main className="flex-1 p-6 lg:p-8">

            {children}

        </main>
      </div>
    </div>
  );
};