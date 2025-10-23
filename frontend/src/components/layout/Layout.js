import React from 'react';
import Sidebar from './Sidebar';
import NotificationBell from './NotificationBell';
import GlobalSearch from '../common/GlobalSearch';

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto lg:ml-64">
        {/* Header avec recherche et notifications */}
        <div className="bg-white border-b px-8 py-4 flex items-center justify-between">
          <GlobalSearch />
          <NotificationBell />
        </div>
        
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
