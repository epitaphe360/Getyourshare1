import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Users,
  Target,
  TrendingUp,
  UserCheck,
  FileText,
  Settings,
  Newspaper,
  ShoppingCart,
  LogOut,
  ChevronDown,
  ChevronRight,
  Menu,
  X,
  Link as LinkIcon,
  Zap,
  MessageSquare,
  Shield
} from 'lucide-react';

const Sidebar = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState({
    advertisers: false,
    performance: false,
    affiliates: false,
    logs: false,
    settings: false,
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleMenu = (menu) => {
    setExpandedMenus(prev => ({ ...prev, [menu]: !prev[menu] }));
  };

  // ============================================
  // MENUS ADAPTÉS PAR RÔLE
  // ============================================

  const getMenuItemsForRole = (role) => {
    // Menu pour INFLUENCER - Simplifié et focalisé
    const influencerMenu = [
      {
        title: 'Getting Started',
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: 'Dashboard',
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: 'Messages',
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: 'Marketplace',
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: 'Mes Campagnes',
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: 'Mes Liens',
        icon: <LinkIcon size={20} />,
        path: '/tracking-links',
      },
      {
        title: 'Performance',
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: 'Conversions', path: '/performance/conversions' },
          { title: 'Rapports', path: '/performance/reports' },
        ],
      },
      {
        title: 'Abonnement',
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: 'Paramètres',
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: 'Personnel', path: '/settings/personal' },
          { title: 'Sécurité', path: '/settings/security' },
        ],
      },
    ];

    // Menu pour MERCHANT - Adapté à la gestion commerciale
    const merchantMenu = [
      {
        title: 'Getting Started',
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: 'Dashboard',
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: 'Messages',
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: 'Mes Produits',
        icon: <ShoppingCart size={20} />,
        path: '/products',
      },
      {
        title: 'Mes Campagnes',
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: 'Mes Affiliés',
        icon: <UserCheck size={20} />,
        submenu: 'affiliates',
        items: [
          { title: 'Liste', path: '/affiliates' },
          { title: 'Demandes', path: '/affiliates/applications' },
          { title: 'Paiements', path: '/affiliates/payouts' },
          { title: 'Coupons', path: '/affiliates/coupons' },
        ],
      },
      {
        title: 'Performance',
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: 'Conversions', path: '/performance/conversions' },
          { title: 'Commissions MLM', path: '/performance/mlm-commissions' },
          { title: 'Rapports', path: '/performance/reports' },
        ],
      },
      {
        title: 'Suivi',
        icon: <FileText size={20} />,
        submenu: 'logs',
        items: [
          { title: 'Clics', path: '/logs/clicks' },
          { title: 'Postback', path: '/logs/postback' },
        ],
      },
      {
        title: 'Marketplace',
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: 'Abonnement',
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: 'Paramètres',
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: 'Personnel', path: '/settings/personal' },
          { title: 'Sécurité', path: '/settings/security' },
          { title: 'Entreprise', path: '/settings/company' },
          { title: 'Affiliés', path: '/settings/affiliates' },
          { title: 'SMTP', path: '/settings/smtp' },
          { title: 'Emails', path: '/settings/emails' },
        ],
      },
    ];

    // Menu pour ADMIN - Complet avec toutes les fonctionnalités
    const adminMenu = [
      {
        title: 'Getting Started',
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: 'Dashboard',
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: 'Messages',
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: 'News & Newsletter',
        icon: <Newspaper size={20} />,
        path: '/news',
      },
      {
        title: 'Annonceurs',
        icon: <Users size={20} />,
        submenu: 'advertisers',
        items: [
          { title: 'Liste', path: '/advertisers' },
          { title: 'Inscriptions', path: '/advertisers/registrations' },
          { title: 'Facturation', path: '/advertisers/billing' },
        ],
      },
      {
        title: 'Campagnes/Offres',
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: 'Produits',
        icon: <ShoppingCart size={20} />,
        path: '/products',
      },
      {
        title: 'Modération IA',
        icon: <Shield size={20} />,
        path: '/admin/moderation',
      },
      {
        title: 'Performance',
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: 'Conversions', path: '/performance/conversions' },
          { title: 'Commissions MLM', path: '/performance/mlm-commissions' },
          { title: 'Leads', path: '/performance/leads' },
          { title: 'Rapports', path: '/performance/reports' },
        ],
      },
      {
        title: 'Affiliés',
        icon: <UserCheck size={20} />,
        submenu: 'affiliates',
        items: [
          { title: 'Liste', path: '/affiliates' },
          { title: 'Demandes', path: '/affiliates/applications' },
          { title: 'Paiements', path: '/affiliates/payouts' },
          { title: 'Coupons', path: '/affiliates/coupons' },
          { title: 'Commandes Perdues', path: '/affiliates/lost-orders' },
          { title: 'Rapport de Solde', path: '/affiliates/balance-report' },
        ],
      },
      {
        title: 'Logs',
        icon: <FileText size={20} />,
        submenu: 'logs',
        items: [
          { title: 'Clics', path: '/logs/clicks' },
          { title: 'Postback', path: '/logs/postback' },
          { title: 'Audit', path: '/logs/audit' },
          { title: 'Webhooks', path: '/logs/webhooks' },
        ],
      },
      {
        title: 'Marketplace',
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: 'Liens de Tracking',
        icon: <LinkIcon size={20} />,
        path: '/tracking-links',
      },
      {
        title: 'Intégrations',
        icon: <Zap size={20} />,
        path: '/integrations',
      },
      {
        title: 'Abonnements Plateforme',
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: 'Paramètres',
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: 'Personnel', path: '/settings/personal' },
          { title: 'Sécurité', path: '/settings/security' },
          { title: 'Entreprise', path: '/settings/company' },
          { title: 'Plateforme', path: '/settings/platform' },
          { title: 'Affiliés', path: '/settings/affiliates' },
          { title: 'Inscription', path: '/settings/registration' },
          { title: 'MLM', path: '/settings/mlm' },
          { title: 'Sources de Trafic', path: '/settings/traffic-sources' },
          { title: 'Permissions', path: '/settings/permissions' },
          { title: 'Utilisateurs', path: '/settings/users' },
          { title: 'SMTP', path: '/settings/smtp' },
          { title: 'Emails', path: '/settings/emails' },
          { title: 'White Label', path: '/settings/white-label' },
        ],
      },
    ];

    // Retourner le menu approprié selon le rôle
    switch (role?.toLowerCase()) {
      case 'influencer':
        return influencerMenu;
      case 'merchant':
        return merchantMenu;
      case 'admin':
      default:
        return adminMenu;
    }
  };

  // Obtenir le menu selon le rôle de l'utilisateur
  const menuItems = getMenuItemsForRole(user?.role);

  const renderMenuItem = (item) => {
    if (item.submenu) {
      return (
        <div key={item.submenu}>
          <button
            onClick={() => toggleMenu(item.submenu)}
            className="w-full flex items-center justify-between px-4 py-3 text-gray-300 hover:bg-blue-800 hover:text-white rounded-lg transition-all"
          >
            <div className="flex items-center space-x-3">
              {item.icon}
              <span>{item.title}</span>
            </div>
            {expandedMenus[item.submenu] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </button>
          {expandedMenus[item.submenu] && (
            <div className="ml-8 mt-1 space-y-1">
              {item.items.map((subItem) => (
                <NavLink
                  key={subItem.path}
                  to={subItem.path}
                  className={({ isActive }) =>
                    `block px-4 py-2 text-sm rounded-lg transition-all ${
                      isActive
                        ? 'bg-blue-800 text-white font-semibold'
                        : 'text-gray-300 hover:bg-blue-800 hover:text-white'
                    }`
                  }
                >
                  {subItem.title}
                </NavLink>
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <NavLink
        key={item.path}
        to={item.path}
        state={item.path === '/marketplace' ? { fromDashboard: true } : undefined}
        className={({ isActive }) =>
          `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            isActive
              ? 'bg-blue-800 text-white font-semibold'
              : 'text-gray-300 hover:bg-blue-800 hover:text-white'
          }`
        }
      >
        {item.icon}
        <span>{item.title}</span>
      </NavLink>
    );
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-blue-600 text-white rounded-lg"
      >
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen bg-gradient-to-b from-blue-700 to-blue-900 text-white overflow-y-auto transition-all duration-300 z-40 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } ${collapsed ? 'w-20' : 'w-64'}`}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-8">
            <h1 className={`text-2xl font-bold ${collapsed ? 'hidden' : 'block'}`}>ShareYourSales</h1>
          </div>

          {/* User Info */}
          <div className={`mb-6 pb-6 border-b border-blue-600 ${collapsed ? 'hidden' : 'block'}`}>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                {user?.first_name?.[0] || 'U'}
              </div>
              <div>
                <p className="font-semibold">{user?.first_name} {user?.last_name}</p>
                <p className="text-xs text-blue-300">{user?.role}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            {menuItems.map(renderMenuItem)}
          </nav>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-3 mt-6 text-gray-300 hover:bg-red-600 hover:text-white rounded-lg transition-all"
          >
            <LogOut size={20} />
            <span className={collapsed ? 'hidden' : 'block'}>Déconnexion</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
