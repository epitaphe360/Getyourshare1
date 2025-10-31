import React from 'react';
import Sidebar from './Sidebar';
import NotificationBell from './NotificationBell';
import GlobalSearch from '../common/GlobalSearch';
import LanguageSelector from '../common/LanguageSelector';

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto lg:ml-64">
        {/* Header avec recherche et notifications */}
        <div className="bg-white border-b px-8 py-4 flex items-center justify-between">
          <GlobalSearch />
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <NotificationBell />
          </div>
        </div>
        
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
