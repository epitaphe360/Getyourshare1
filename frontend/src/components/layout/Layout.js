import React from 'react';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto lg:ml-64">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
