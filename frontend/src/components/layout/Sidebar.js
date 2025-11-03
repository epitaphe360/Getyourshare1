import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useI18n } from '../../i18n/i18n';
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
  Shield,
  Languages
} from 'lucide-react';

const Sidebar = () => {
  const { logout, user } = useAuth();
  const { t, changeLanguage, language, languageNames, languageFlags, languages } = useI18n();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
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
        title: t('nav_getting_started'),
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: t('nav_dashboard'),
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: t('nav_messages'),
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: t('nav_marketplace'),
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: t('nav_my_campaigns'),
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: t('nav_links'),
        icon: <LinkIcon size={20} />,
        path: '/tracking-links',
      },
      {
        title: t('nav_performance'),
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: t('nav_conversions'), path: '/performance/conversions' },
          { title: t('nav_reports'), path: '/performance/reports' },
        ],
      },
      {
        title: t('nav_subscription'),
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: t('nav_settings'),
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: t('nav_personal'), path: '/settings/personal' },
          { title: t('nav_security'), path: '/settings/security' },
        ],
      },
    ];

    // Menu pour MERCHANT - Adapté à la gestion commerciale
    const merchantMenu = [
      {
        title: t('nav_getting_started'),
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: t('nav_dashboard'),
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: t('nav_messages'),
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: t('nav_my_products'),
        icon: <ShoppingCart size={20} />,
        path: '/products',
      },
      {
        title: t('nav_my_campaigns'),
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: t('nav_my_affiliates'),
        icon: <UserCheck size={20} />,
        submenu: 'affiliates',
        items: [
          { title: t('nav_list'), path: '/affiliates' },
          { title: t('nav_applications'), path: '/affiliates/applications' },
          { title: t('nav_payouts'), path: '/affiliates/payouts' },
          { title: t('nav_coupons'), path: '/affiliates/coupons' },
        ],
      },
      {
        title: t('nav_performance'),
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: t('nav_conversions'), path: '/performance/conversions' },
          { title: t('nav_mlm_commissions'), path: '/performance/mlm-commissions' },
          { title: t('nav_reports'), path: '/performance/reports' },
        ],
      },
      {
        title: t('nav_tracking'),
        icon: <FileText size={20} />,
        submenu: 'logs',
        items: [
          { title: t('nav_clicks'), path: '/logs/clicks' },
          { title: t('nav_postback'), path: '/logs/postback' },
        ],
      },
      {
        title: t('nav_marketplace'),
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: t('nav_subscription'),
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: t('nav_settings'),
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: t('nav_personal'), path: '/settings/personal' },
          { title: t('nav_security'), path: '/settings/security' },
          { title: t('nav_company'), path: '/settings/company' },
          { title: t('nav_affiliates'), path: '/settings/affiliates' },
          { title: t('nav_smtp'), path: '/settings/smtp' },
          { title: t('nav_emails'), path: '/settings/emails' },
        ],
      },
    ];

    // Menu pour ADMIN - Complet avec toutes les fonctionnalités
    const adminMenu = [
      {
        title: t('nav_getting_started'),
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: t('nav_dashboard'),
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: t('nav_messages'),
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: t('nav_news'),
        icon: <Newspaper size={20} />,
        path: '/news',
      },
      {
        title: t('nav_advertisers'),
        icon: <Users size={20} />,
        submenu: 'advertisers',
        items: [
          { title: t('nav_list'), path: '/advertisers' },
          { title: t('nav_registrations'), path: '/advertisers/registrations' },
          { title: t('nav_billing'), path: '/advertisers/billing' },
        ],
      },
      {
        title: t('nav_campaigns'),
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: t('nav_products'),
        icon: <ShoppingCart size={20} />,
        path: '/products',
      },
      {
        title: t('nav_moderation'),
        icon: <Shield size={20} />,
        path: '/admin/moderation',
      },
      {
        title: t('nav_performance'),
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: t('nav_conversions'), path: '/performance/conversions' },
          { title: t('nav_mlm_commissions'), path: '/performance/mlm-commissions' },
          { title: t('nav_leads'), path: '/performance/leads' },
          { title: t('nav_reports'), path: '/performance/reports' },
        ],
      },
      {
        title: t('nav_affiliates'),
        icon: <UserCheck size={20} />,
        submenu: 'affiliates',
        items: [
          { title: t('nav_list'), path: '/affiliates' },
          { title: t('nav_applications'), path: '/affiliates/applications' },
          { title: t('nav_payouts'), path: '/affiliates/payouts' },
          { title: t('nav_coupons'), path: '/affiliates/coupons' },
          { title: t('nav_lost_orders'), path: '/affiliates/lost-orders' },
          { title: t('nav_balance_report'), path: '/affiliates/balance-report' },
        ],
      },
      {
        title: t('nav_logs'),
        icon: <FileText size={20} />,
        submenu: 'logs',
        items: [
          { title: t('nav_clicks'), path: '/logs/clicks' },
          { title: t('nav_postback'), path: '/logs/postback' },
          { title: t('nav_audit'), path: '/logs/audit' },
          { title: t('nav_webhooks'), path: '/logs/webhooks' },
        ],
      },
      {
        title: t('nav_marketplace'),
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: t('nav_tracking_links'),
        icon: <LinkIcon size={20} />,
        path: '/tracking-links',
      },
      {
        title: t('nav_integrations'),
        icon: <Zap size={20} />,
        path: '/integrations',
      },
      {
        title: t('nav_platform_subscriptions'),
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: t('nav_settings'),
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: t('nav_personal'), path: '/settings/personal' },
          { title: t('nav_security'), path: '/settings/security' },
          { title: t('nav_company'), path: '/settings/company' },
          { title: t('nav_platform'), path: '/settings/platform' },
          { title: t('nav_affiliates'), path: '/settings/affiliates' },
          { title: t('nav_registration'), path: '/settings/registration' },
          { title: t('nav_mlm'), path: '/settings/mlm' },
          { title: t('nav_traffic_sources'), path: '/settings/traffic-sources' },
          { title: t('nav_permissions'), path: '/settings/permissions' },
          { title: t('nav_users'), path: '/settings/users' },
          { title: t('nav_smtp'), path: '/settings/smtp' },
          { title: t('nav_emails'), path: '/settings/emails' },
          { title: t('nav_white_label'), path: '/settings/white-label' },
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

          {/* Language Selector */}
          <div className="mt-6 border-t border-gray-700 pt-4">
            <div className="relative">
              <button
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="w-full flex items-center justify-between px-4 py-3 text-gray-300 hover:bg-blue-600 hover:text-white rounded-lg transition-all"
              >
                <div className="flex items-center space-x-3">
                  <Languages size={20} />
                  {!collapsed && (
                    <span>
                      {languageFlags[language]} {languageNames[language]}
                    </span>
                  )}
                </div>
                {!collapsed && (
                  <ChevronDown 
                    size={16} 
                    className={`transition-transform ${showLanguageMenu ? 'rotate-180' : ''}`}
                  />
                )}
              </button>

              {/* Language dropdown */}
              {showLanguageMenu && !collapsed && (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
                  {Object.entries(languages).map(([key, value]) => (
                    <button
                      key={value}
                      onClick={() => {
                        changeLanguage(value);
                        setShowLanguageMenu(false);
                      }}
                      className={`w-full px-4 py-2 text-left hover:bg-blue-600 transition-colors flex items-center space-x-2 ${
                        language === value ? 'bg-blue-700 text-white' : 'text-gray-300'
                      }`}
                    >
                      <span>{languageFlags[value]}</span>
                      <span>{languageNames[value]}</span>
                      {language === value && (
                        <span className="ml-auto text-green-400">✓</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-3 mt-4 text-gray-300 hover:bg-red-600 hover:text-white rounded-lg transition-all"
          >
            <LogOut size={20} />
            <span className={collapsed ? 'hidden' : 'block'}>{t('logout')}</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
