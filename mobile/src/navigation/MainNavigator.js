/**
 * Main Navigator
 * Bottom Tab Navigation with role-based screens
 */

import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {useAuth} from '../contexts/AuthContext';

// Dashboard Screens
import DashboardScreen from '../screens/dashboard/DashboardScreen';
import InfluencerDashboard from '../screens/dashboard/InfluencerDashboard';
import MerchantDashboard from '../screens/dashboard/MerchantDashboard';
import AdminDashboard from '../screens/dashboard/AdminDashboard';

// Marketplace Screens
import MarketplaceScreen from '../screens/marketplace/MarketplaceScreen';
import ProductDetailScreen from '../screens/marketplace/ProductDetailScreen';

// Links Screens (Influencer)
import MyLinksScreen from '../screens/influencer/MyLinksScreen';
import LinkStatsScreen from '../screens/influencer/LinkStatsScreen';

// Products Screens (Merchant)
import ProductsListScreen from '../screens/merchant/ProductsListScreen';
import CreateProductScreen from '../screens/merchant/CreateProductScreen';
import AffiliationRequestsScreen from '../screens/merchant/AffiliationRequestsScreen';

// Messages Screen
import MessagesScreen from '../screens/messages/MessagesScreen';
import ChatScreen from '../screens/messages/ChatScreen';

// Profile/Settings Screens
import ProfileScreen from '../screens/profile/ProfileScreen';
import SettingsScreen from '../screens/profile/SettingsScreen';
import EditProfileScreen from '../screens/profile/EditProfileScreen';

// Analytics Screens
import AnalyticsScreen from '../screens/analytics/AnalyticsScreen';
import ConversionsScreen from '../screens/analytics/ConversionsScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Dashboard Stack
const DashboardStack = () => {
  const {userRole} = useAuth();

  const getDashboardComponent = () => {
    switch (userRole) {
      case 'influencer':
        return InfluencerDashboard;
      case 'merchant':
        return MerchantDashboard;
      case 'admin':
        return AdminDashboard;
      default:
        return DashboardScreen;
    }
  };

  return (
    <Stack.Navigator>
      <Stack.Screen
        name="DashboardHome"
        component={getDashboardComponent()}
        options={{title: 'Tableau de Bord'}}
      />
    </Stack.Navigator>
  );
};

// Marketplace Stack
const MarketplaceStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="MarketplaceHome"
      component={MarketplaceScreen}
      options={{title: 'Marketplace'}}
    />
    <Stack.Screen
      name="ProductDetail"
      component={ProductDetailScreen}
      options={{title: 'Détails du Produit'}}
    />
  </Stack.Navigator>
);

// Links Stack (for Influencers)
const LinksStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="MyLinksHome"
      component={MyLinksScreen}
      options={{title: 'Mes Liens'}}
    />
    <Stack.Screen
      name="LinkStats"
      component={LinkStatsScreen}
      options={{title: 'Statistiques'}}
    />
  </Stack.Navigator>
);

// Products Stack (for Merchants)
const ProductsStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="ProductsHome"
      component={ProductsListScreen}
      options={{title: 'Mes Produits'}}
    />
    <Stack.Screen
      name="CreateProduct"
      component={CreateProductScreen}
      options={{title: 'Nouveau Produit'}}
    />
    <Stack.Screen
      name="AffiliationRequests"
      component={AffiliationRequestsScreen}
      options={{title: 'Demandes d\'Affiliation'}}
    />
  </Stack.Navigator>
);

// Messages Stack
const MessagesStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="MessagesList"
      component={MessagesScreen}
      options={{title: 'Messages'}}
    />
    <Stack.Screen
      name="Chat"
      component={ChatScreen}
      options={{title: 'Conversation'}}
    />
  </Stack.Navigator>
);

// Profile Stack
const ProfileStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="ProfileHome"
      component={ProfileScreen}
      options={{title: 'Profil'}}
    />
    <Stack.Screen
      name="Settings"
      component={SettingsScreen}
      options={{title: 'Paramètres'}}
    />
    <Stack.Screen
      name="EditProfile"
      component={EditProfileScreen}
      options={{title: 'Modifier le Profil'}}
    />
  </Stack.Navigator>
);

// Analytics Stack
const AnalyticsStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="AnalyticsHome"
      component={AnalyticsScreen}
      options={{title: 'Analytics'}}
    />
    <Stack.Screen
      name="Conversions"
      component={ConversionsScreen}
      options={{title: 'Conversions'}}
    />
  </Stack.Navigator>
);

const MainNavigator = () => {
  const {userRole} = useAuth();

  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
          } else if (route.name === 'Marketplace') {
            iconName = focused ? 'storefront' : 'storefront-outline';
          } else if (route.name === 'MyLinks') {
            iconName = focused ? 'link-variant' : 'link-variant';
          } else if (route.name === 'Products') {
            iconName = focused ? 'package-variant' : 'package-variant-closed';
          } else if (route.name === 'Analytics') {
            iconName = focused ? 'chart-line' : 'chart-line-variant';
          } else if (route.name === 'Messages') {
            iconName = focused ? 'message' : 'message-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'account' : 'account-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6366f1',
        tabBarInactiveTintColor: '#94a3b8',
        headerShown: false,
      })}>
      {/* Dashboard - Available for all roles */}
      <Tab.Screen
        name="Dashboard"
        component={DashboardStack}
        options={{title: 'Accueil'}}
      />

      {/* Marketplace - Available for all roles */}
      <Tab.Screen
        name="Marketplace"
        component={MarketplaceStack}
        options={{title: 'Marketplace'}}
      />

      {/* Influencer-specific tabs */}
      {userRole === 'influencer' && (
        <Tab.Screen
          name="MyLinks"
          component={LinksStack}
          options={{title: 'Mes Liens'}}
        />
      )}

      {/* Merchant-specific tabs */}
      {userRole === 'merchant' && (
        <>
          <Tab.Screen
            name="Products"
            component={ProductsStack}
            options={{title: 'Produits'}}
          />
          <Tab.Screen
            name="Analytics"
            component={AnalyticsStack}
            options={{title: 'Analytics'}}
          />
        </>
      )}

      {/* Messages - Available for all roles */}
      <Tab.Screen
        name="Messages"
        component={MessagesStack}
        options={{title: 'Messages'}}
      />

      {/* Profile - Available for all roles */}
      <Tab.Screen
        name="Profile"
        component={ProfileStack}
        options={{title: 'Profil'}}
      />
    </Tab.Navigator>
  );
};

export default MainNavigator;
