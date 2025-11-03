import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { I18nProvider } from './i18n/i18n';
import Layout from './components/layout/Layout';
import PublicLayout from './components/layout/PublicLayout';
import ChatbotWidget from './components/bot/ChatbotWidget';
import WhatsAppFloatingButton from './components/social/WhatsAppFloatingButton';
import HomepageV2 from './pages/HomepageV2';
import Login from './pages/Login';
import Register from './pages/Register';
import Pricing from './pages/Pricing';
import Dashboard from './pages/Dashboard';
import GettingStarted from './pages/GettingStarted';
import News from './pages/News';
import Marketplace from './pages/Marketplace';
import TrackingLinks from './pages/TrackingLinks';
import Integrations from './pages/Integrations';
import LandingPage from './pages/LandingPage';
import AIMarketing from './pages/AIMarketing';
import MerchantsList from './pages/merchants/MerchantsList';
import InfluencersList from './pages/influencers/InfluencersList';
import InfluencerSearchPage from './pages/influencers/InfluencerSearchPage';
import InfluencerProfilePage from './pages/influencers/InfluencerProfilePage';

// Messaging
import MessagingPage from './pages/MessagingPage';

// New Pages V2
import MarketplaceV2 from './pages/MarketplaceV2';
import ProductDetail from './pages/ProductDetail';
import MyLinks from './pages/influencer/MyLinks';
import Contact from './pages/Contact';
import AdminSocialDashboard from './pages/admin/AdminSocialDashboard';
import UserManagement from './pages/admin/UserManagement';
import ModerationDashboard from './pages/admin/ModerationDashboard';

// Legal Pages
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';
import About from './pages/About';

// New Pages V3 - Subscription System
import PricingV3 from './pages/PricingV3';
import MarketplaceFourTabs from './pages/MarketplaceFourTabs';
import MarketplaceGroupon from './pages/MarketplaceGroupon';
import SubscriptionDashboard from './pages/company/SubscriptionDashboard';
import SubscriptionManagement from './pages/subscription/SubscriptionManagement';
import TeamManagement from './pages/company/TeamManagement';
import CompanyLinksDashboard from './pages/company/CompanyLinksDashboard';

// Products
import ProductsListPage from './pages/products/ProductsListPage';
import CreateProductPage from './pages/products/CreateProductPage';

// Advertisers
import AdvertisersList from './pages/advertisers/AdvertisersList';
import AdvertiserRegistrations from './pages/advertisers/AdvertiserRegistrations';
import AdvertiserBilling from './pages/advertisers/AdvertiserBilling';

// Campaigns
import CampaignsList from './pages/campaigns/CampaignsList';
import CreateCampaignPage from './pages/campaigns/CreateCampaignPage';

// Affiliates
import AffiliatesList from './pages/affiliates/AffiliatesList';
import AffiliateApplications from './pages/affiliates/AffiliateApplications';
import AffiliatePayouts from './pages/affiliates/AffiliatePayouts';
import AffiliateCoupons from './pages/affiliates/AffiliateCoupons';
import LostOrders from './pages/affiliates/LostOrders';
import BalanceReport from './pages/affiliates/BalanceReport';

// Performance
import Conversions from './pages/performance/Conversions';
import MLMCommissions from './pages/performance/MLMCommissions';
import Leads from './pages/performance/Leads';
import Reports from './pages/performance/Reports';

// Logs
import Clicks from './pages/logs/Clicks';
import Postback from './pages/logs/Postback';
import Audit from './pages/logs/Audit';
import Webhooks from './pages/logs/Webhooks';

// Settings
import PersonalSettings from './pages/settings/PersonalSettings';
import SecuritySettings from './pages/settings/SecuritySettings';
import CompanySettings from './pages/settings/CompanySettings';
import AffiliateSettings from './pages/settings/AffiliateSettings';
import RegistrationSettings from './pages/settings/RegistrationSettings';
import MLMSettings from './pages/settings/MLMSettings';
import TrafficSources from './pages/settings/TrafficSources';
import Permissions from './pages/settings/Permissions';
import Users from './pages/settings/Users';
import SMTP from './pages/settings/SMTP';
import Emails from './pages/settings/Emails';
import WhiteLabel from './pages/settings/WhiteLabel';
import PlatformSettings from './pages/settings/PlatformSettings';

import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
};

// Role-based Protected Route Component
const RoleProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Vérifier si le rôle de l'utilisateur est autorisé
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Accès refusé</h2>
            <p className="text-gray-600 mb-4">
              Vous n'avez pas les permissions nécessaires pour accéder à cette page.
            </p>
            <p className="text-sm text-gray-500">
              Cette fonctionnalité est réservée aux {allowedRoles.join(', ')}.
            </p>
            <button
              onClick={() => window.history.back()}
              className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Retour
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return <Layout>{children}</Layout>;
};

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <I18nProvider>
          <BrowserRouter
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true
            }}
          >
          <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomepageV2 />} />
          <Route path="/home" element={<HomepageV2 />} />
          <Route path="/landing-old" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/pricing-v3" element={<PricingV3 />} />
          <Route path="/marketplace-4tabs" element={<MarketplaceFourTabs />} />
          <Route path="/marketplace" element={<PublicLayout><MarketplaceGroupon /></PublicLayout>} />
          
          {/* Product Detail - Public (accessible sans connexion) */}
          <Route path="/marketplace/product/:productId" element={<PublicLayout><ProductDetail /></PublicLayout>} />
          
          {/* Contact Page (Public avec menu homepage) */}
          <Route path="/contact" element={<PublicLayout><Contact /></PublicLayout>} />

          {/* Legal Pages (Public avec menu homepage) */}
          <Route path="/privacy" element={<PublicLayout><Privacy /></PublicLayout>} />
          <Route path="/terms" element={<PublicLayout><Terms /></PublicLayout>} />
          <Route path="/about" element={<PublicLayout><About /></PublicLayout>} />

          {/* Protected Routes */}
          <Route
            path="/getting-started"
            element={
              <ProtectedRoute>
                <GettingStarted />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/news"
            element={
              <ProtectedRoute>
                <News />
              </ProtectedRoute>
            }
          />

          {/* Advertisers Routes */}
          <Route
            path="/advertisers"
            element={
              <ProtectedRoute>
                <AdvertisersList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/advertisers/registrations"
            element={
              <ProtectedRoute>
                <AdvertiserRegistrations />
              </ProtectedRoute>
            }
          />
          <Route
            path="/advertisers/billing"
            element={
              <ProtectedRoute>
                <AdvertiserBilling />
              </ProtectedRoute>
            }
          />

          {/* Campaigns Routes */}
          <Route
            path="/campaigns"
            element={
              <ProtectedRoute>
                <CampaignsList />
              </ProtectedRoute>
            }
          />
          {/* CRÉATION DE CAMPAGNE - MERCHANTS/ADMIN UNIQUEMENT */}
          <Route
            path="/campaigns/create"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <CreateCampaignPage />
              </RoleProtectedRoute>
            }
          />

          {/* Merchants Routes */}
          <Route
            path="/merchants"
            element={
              <ProtectedRoute>
                <MerchantsList />
              </ProtectedRoute>
            }
          />

          {/* Influencers Routes */}
          <Route
            path="/influencers"
            element={
              <ProtectedRoute>
                <InfluencersList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/influencers/search"
            element={
              <ProtectedRoute>
                <InfluencerSearchPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/influencers/:influencerId"
            element={
              <ProtectedRoute>
                <InfluencerProfilePage />
              </ProtectedRoute>
            }
          />

          {/* Messages Routes */}
          <Route
            path="/messages"
            element={
              <ProtectedRoute>
                <MessagingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/messages/:conversationId"
            element={
              <ProtectedRoute>
                <MessagingPage />
              </ProtectedRoute>
            }
          />

          {/* Products Routes */}
          <Route
            path="/products"
            element={
              <ProtectedRoute>
                <ProductsListPage />
              </ProtectedRoute>
            }
          />
          {/* CRÉATION/ÉDITION DE PRODUIT - MERCHANTS/ADMIN UNIQUEMENT */}
          <Route
            path="/products/create"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <CreateProductPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/products/:productId/edit"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <CreateProductPage />
              </RoleProtectedRoute>
            }
          />

          {/* Affiliates Routes */}
          <Route
            path="/affiliates"
            element={
              <ProtectedRoute>
                <AffiliatesList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/applications"
            element={
              <ProtectedRoute>
                <AffiliateApplications />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/payouts"
            element={
              <ProtectedRoute>
                <AffiliatePayouts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/coupons"
            element={
              <ProtectedRoute>
                <AffiliateCoupons />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/lost-orders"
            element={
              <ProtectedRoute>
                <LostOrders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/balance-report"
            element={
              <ProtectedRoute>
                <BalanceReport />
              </ProtectedRoute>
            }
          />

          {/* Performance Routes */}
          <Route
            path="/performance/conversions"
            element={
              <ProtectedRoute>
                <Conversions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/performance/mlm-commissions"
            element={
              <ProtectedRoute>
                <MLMCommissions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/performance/leads"
            element={
              <ProtectedRoute>
                <Leads />
              </ProtectedRoute>
            }
          />
          <Route
            path="/performance/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />

          {/* Logs Routes */}
          <Route
            path="/logs/clicks"
            element={
              <ProtectedRoute>
                <Clicks />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs/postback"
            element={
              <ProtectedRoute>
                <Postback />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs/audit"
            element={
              <ProtectedRoute>
                <Audit />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs/webhooks"
            element={
              <ProtectedRoute>
                <Webhooks />
              </ProtectedRoute>
            }
          />

          {/* Marketplace - Version Groupon (utilisée partout) */}
          {/* Route déjà définie en haut du fichier avec MarketplaceGroupon */}

          {/* Anciennes versions marketplace (pour référence) */}
          <Route
            path="/marketplace-old"
            element={
              <ProtectedRoute>
                <Marketplace />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/marketplace-v2"
            element={
              <ProtectedRoute>
                <MarketplaceV2 />
              </ProtectedRoute>
            }
          />

          {/* Influencer Routes */}
          <Route
            path="/my-links"
            element={
              <ProtectedRoute>
                <MyLinks />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin/social-dashboard"
            element={
              <ProtectedRoute>
                <AdminSocialDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <UserManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/moderation"
            element={
              <ProtectedRoute>
                <ModerationDashboard />
              </ProtectedRoute>
            }
          />

          {/* Company/Subscription Routes */}
          <Route
            path="/subscription"
            element={
              <ProtectedRoute>
                <SubscriptionDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/manage"
            element={
              <ProtectedRoute>
                <SubscriptionManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/team"
            element={
              <ProtectedRoute>
                <TeamManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/company-links"
            element={
              <ProtectedRoute>
                <CompanyLinksDashboard />
              </ProtectedRoute>
            }
          />

          {/* AI Marketing */}
          <Route
            path="/ai-marketing"
            element={
              <ProtectedRoute>
                <AIMarketing />
              </ProtectedRoute>
            }
          />

          {/* Tracking Links */}
          <Route
            path="/tracking-links"
            element={
              <ProtectedRoute>
                <TrackingLinks />
              </ProtectedRoute>
            }
          />

          {/* Integrations */}
          <Route
            path="/integrations"
            element={
              <ProtectedRoute>
                <Integrations />
              </ProtectedRoute>
            }
          />

          {/* Settings Routes */}
          <Route
            path="/settings/personal"
            element={
              <ProtectedRoute>
                <PersonalSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/security"
            element={
              <ProtectedRoute>
                <SecuritySettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/company"
            element={
              <ProtectedRoute>
                <CompanySettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/affiliates"
            element={
              <ProtectedRoute>
                <AffiliateSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/registration"
            element={
              <ProtectedRoute>
                <RegistrationSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/mlm"
            element={
              <ProtectedRoute>
                <MLMSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/traffic-sources"
            element={
              <ProtectedRoute>
                <TrafficSources />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/permissions"
            element={
              <ProtectedRoute>
                <Permissions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/users"
            element={
              <ProtectedRoute>
                <Users />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/smtp"
            element={
              <ProtectedRoute>
                <SMTP />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/emails"
            element={
              <ProtectedRoute>
                <Emails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/white-label"
            element={
              <ProtectedRoute>
                <WhiteLabel />
              </ProtectedRoute>
            }
          />
          {/* PARAMÈTRES PLATEFORME - ADMIN UNIQUEMENT */}
          <Route
            path="/settings/platform"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <PlatformSettings />
              </RoleProtectedRoute>
            }
          />

          {/* Default Route */}
          <Route path="/app" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
        {/* Chatbot Widget flottant (en bas à droite) */}
        <ChatbotWidget />
        
        {/* Bouton WhatsApp flottant (en bas à gauche) */}
        <WhatsAppFloatingButton 
          phoneNumber="+212600000000"
          message="Bonjour! Je suis intéressé par la plateforme ShareYourSales."
          position="left"
        />
        
        </BrowserRouter>
        </I18nProvider>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
