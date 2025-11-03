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
  // MENUS ADAPTÉS PAR RÔLE - Avec traductions memoïzées
  // ============================================

  const getMenuItemsForRole = (role) => {
    // Traductions statiques (calculées une seule fois)
    const translations = {
      getting_started: t('nav_getting_started') || 'Getting Started',
      dashboard: t('nav_dashboard') || 'Dashboard',
      messages: t('nav_messages') || 'Messages',
      marketplace: t('nav_marketplace') || 'Marketplace',
      my_campaigns: t('nav_my_campaigns') || 'Mes Campagnes',
      my_links: t('nav_links') || 'Mes Liens',
      performance: t('nav_performance') || 'Performance',
      conversions: t('nav_conversions') || 'Conversions',
      reports: t('nav_reports') || 'Rapports',
      subscription: t('nav_subscription') || 'Abonnement',
      settings: t('nav_settings') || 'Paramètres',
      personal: t('nav_personal') || 'Personnel',
      security: t('nav_security') || 'Sécurité',
      my_products: t('nav_my_products') || 'Mes Produits',
      my_affiliates: t('nav_my_affiliates') || 'Mes Affiliés',
      list: t('nav_list') || 'Liste',
      applications: t('nav_applications') || 'Demandes',
      payouts: t('nav_payouts') || 'Paiements',
      coupons: t('nav_coupons') || 'Coupons',
      mlm_commissions: t('nav_mlm_commissions') || 'Commissions MLM',
      tracking: t('nav_tracking') || 'Suivi',
      clicks: t('nav_clicks') || 'Clics',
      postback: t('nav_postback') || 'Postback',
      company: t('nav_company') || 'Entreprise',
      affiliates: t('nav_affiliates') || 'Affiliés',
      smtp: t('nav_smtp') || 'SMTP',
      emails: t('nav_emails') || 'Emails',
      news: t('nav_news') || 'News & Newsletter',
      advertisers: t('nav_advertisers') || 'Annonceurs',
      campaigns: t('nav_campaigns') || 'Campagnes/Offres',
      products: t('nav_products') || 'Produits',
      moderation: t('nav_moderation') || 'Modération IA',
      leads: t('nav_leads') || 'Leads',
      lost_orders: t('nav_lost_orders') || 'Commandes Perdues',
      balance_report: t('nav_balance_report') || 'Rapport de Solde',
      audit: t('nav_audit') || 'Audit',
      webhooks: t('nav_webhooks') || 'Webhooks',
      tracking_links: t('nav_tracking_links') || 'Liens de Tracking',
      integrations: t('nav_integrations') || 'Intégrations',
      platform_subscriptions: t('nav_platform_subscriptions') || 'Abonnements Plateforme',
      registrations: t('nav_registrations') || 'Inscriptions',
      billing: t('nav_billing') || 'Facturation',
      logs: t('nav_logs') || 'Logs',
      platform: t('nav_platform') || 'Plateforme',
      registration: t('nav_registration') || 'Inscription',
      mlm: t('nav_mlm') || 'MLM',
      traffic_sources: t('nav_traffic_sources') || 'Sources de Trafic',
      permissions: t('nav_permissions') || 'Permissions',
      users: t('nav_users') || 'Utilisateurs',
      white_label: t('nav_white_label') || 'White Label',
    };
    // Menu pour INFLUENCER - Simplifié et focalisé
    const influencerMenu = [
      {
        title: translations.getting_started,
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: translations.dashboard,
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: translations.messages,
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: translations.marketplace,
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: translations.my_campaigns,
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: translations.my_links,
        icon: <LinkIcon size={20} />,
        path: '/tracking-links',
      },
      {
        title: translations.performance,
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: translations.conversions, path: '/performance/conversions' },
          { title: translations.reports, path: '/performance/reports' },
        ],
      },
      {
        title: translations.subscription,
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: translations.settings,
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: translations.personal, path: '/settings/personal' },
          { title: translations.security, path: '/settings/security' },
        ],
      },
    ];

    // Menu pour MERCHANT - Adapté à la gestion commerciale
    const merchantMenu = [
      {
        title: translations.getting_started,
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: translations.dashboard,
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: translations.messages,
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: translations.my_products,
        icon: <ShoppingCart size={20} />,
        path: '/products',
      },
      {
        title: translations.my_campaigns,
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: translations.my_affiliates,
        icon: <UserCheck size={20} />,
        submenu: 'affiliates',
        items: [
          { title: translations.list, path: '/affiliates' },
          { title: translations.applications, path: '/affiliates/applications' },
          { title: translations.payouts, path: '/affiliates/payouts' },
          { title: translations.coupons, path: '/affiliates/coupons' },
        ],
      },
      {
        title: translations.performance,
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: translations.conversions, path: '/performance/conversions' },
          { title: translations.mlm_commissions, path: '/performance/mlm-commissions' },
          { title: translations.reports, path: '/performance/reports' },
        ],
      },
      {
        title: translations.tracking,
        icon: <FileText size={20} />,
        submenu: 'logs',
        items: [
          { title: translations.clicks, path: '/logs/clicks' },
          { title: translations.postback, path: '/logs/postback' },
        ],
      },
      {
        title: translations.marketplace,
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: translations.subscription,
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: translations.settings,
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: translations.personal, path: '/settings/personal' },
          { title: translations.security, path: '/settings/security' },
          { title: translations.company, path: '/settings/company' },
          { title: translations.affiliates, path: '/settings/affiliates' },
          { title: translations.smtp, path: '/settings/smtp' },
          { title: translations.emails, path: '/settings/emails' },
        ],
      },
    ];

    // Menu pour ADMIN - Complet avec toutes les fonctionnalités
    const adminMenu = [
      {
        title: translations.getting_started,
        icon: <Newspaper size={20} />,
        path: '/getting-started',
      },
      {
        title: translations.dashboard,
        icon: <LayoutDashboard size={20} />,
        path: '/dashboard',
      },
      {
        title: translations.messages,
        icon: <MessageSquare size={20} />,
        path: '/messages',
      },
      {
        title: translations.news,
        icon: <Newspaper size={20} />,
        path: '/news',
      },
      {
        title: translations.advertisers,
        icon: <Users size={20} />,
        submenu: 'advertisers',
        items: [
          { title: translations.list, path: '/advertisers' },
          { title: translations.registrations, path: '/advertisers/registrations' },
          { title: translations.billing, path: '/advertisers/billing' },
        ],
      },
      {
        title: translations.campaigns,
        icon: <Target size={20} />,
        path: '/campaigns',
      },
      {
        title: translations.products,
        icon: <ShoppingCart size={20} />,
        path: '/products',
      },
      {
        title: translations.moderation,
        icon: <Shield size={20} />,
        path: '/admin/moderation',
      },
      {
        title: translations.performance,
        icon: <TrendingUp size={20} />,
        submenu: 'performance',
        items: [
          { title: translations.conversions, path: '/performance/conversions' },
          { title: translations.mlm_commissions, path: '/performance/mlm-commissions' },
          { title: translations.leads, path: '/performance/leads' },
          { title: translations.reports, path: '/performance/reports' },
        ],
      },
      {
        title: translations.affiliates,
        icon: <UserCheck size={20} />,
        submenu: 'affiliates',
        items: [
          { title: translations.list, path: '/affiliates' },
          { title: translations.applications, path: '/affiliates/applications' },
          { title: translations.payouts, path: '/affiliates/payouts' },
          { title: translations.coupons, path: '/affiliates/coupons' },
          { title: translations.lost_orders, path: '/affiliates/lost-orders' },
          { title: translations.balance_report, path: '/affiliates/balance-report' },
        ],
      },
      {
        title: translations.logs,
        icon: <FileText size={20} />,
        submenu: 'logs',
        items: [
          { title: translations.clicks, path: '/logs/clicks' },
          { title: translations.postback, path: '/logs/postback' },
          { title: translations.audit, path: '/logs/audit' },
          { title: translations.webhooks, path: '/logs/webhooks' },
        ],
      },
      {
        title: translations.marketplace,
        icon: <ShoppingCart size={20} />,
        path: '/marketplace',
      },
      {
        title: translations.tracking_links,
        icon: <LinkIcon size={20} />,
        path: '/tracking-links',
      },
      {
        title: translations.integrations,
        icon: <Zap size={20} />,
        path: '/integrations',
      },
      {
        title: translations.platform_subscriptions,
        icon: <Zap size={20} />,
        path: '/subscription',
      },
      {
        title: translations.settings,
        icon: <Settings size={20} />,
        submenu: 'settings',
        items: [
          { title: translations.personal, path: '/settings/personal' },
          { title: translations.security, path: '/settings/security' },
          { title: translations.company, path: '/settings/company' },
          { title: translations.platform, path: '/settings/platform' },
          { title: translations.affiliates, path: '/settings/affiliates' },
          { title: translations.registration, path: '/settings/registration' },
          { title: translations.mlm, path: '/settings/mlm' },
          { title: translations.traffic_sources, path: '/settings/traffic-sources' },
          { title: translations.permissions, path: '/settings/permissions' },
          { title: translations.users, path: '/settings/users' },
          { title: translations.smtp, path: '/settings/smtp' },
          { title: translations.emails, path: '/settings/emails' },
          { title: translations.white_label, path: '/settings/white-label' },
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
