# 📱 ShareYourSales Mobile - iOS & Android

Application mobile React Native pour ShareYourSales - Plateforme d'affiliation entre influenceurs et marchands.

## 🎯 Vue d'ensemble

Cette application mobile offre toutes les fonctionnalités de la plateforme web ShareYourSales sur iOS et Android :

- **Authentification** complète (login, register, forgot password)
- **Dashboards par rôle** (Influenceur, Marchand, Admin)
- **Marketplace** de produits avec recherche et filtres
- **Gestion des liens** d'affiliation (Influenceurs)
- **Gestion des produits** (Marchands)
- **Messagerie** en temps réel
- **Analytics et statistiques**
- **Notifications push**
- **Paramètres** et profil utilisateur

## 🏗️ Architecture

```
mobile/
├── android/                 # Configuration Android
│   ├── app/
│   │   ├── build.gradle    # Build config Android
│   │   └── src/main/
│   │       └── AndroidManifest.xml
│   └── build.gradle        # Root build config
├── ios/                     # Configuration iOS
│   ├── Podfile             # CocoaPods dependencies
│   ├── Info.plist          # iOS app config
│   └── ShareYourSales.xcodeproj/
├── src/                     # Code source
│   ├── components/          # Composants réutilisables
│   │   ├── common/         # Buttons, Cards, Inputs, etc.
│   │   └── charts/         # Charts & graphs
│   ├── contexts/            # React Contexts
│   │   ├── AuthContext.js  # Gestion authentification
│   │   └── ToastContext.js # Notifications toast
│   ├── navigation/          # Navigation
│   │   ├── RootNavigator.js    # Navigation principale
│   │   └── MainNavigator.js    # Tab navigation
│   ├── screens/             # Écrans de l'app
│   │   ├── auth/           # Login, Register, Forgot Password
│   │   ├── dashboard/      # Dashboards par rôle
│   │   ├── marketplace/    # Marketplace & produits
│   │   ├── influencer/     # Écrans influenceur
│   │   ├── merchant/       # Écrans marchand
│   │   ├── messages/       # Messagerie
│   │   ├── profile/        # Profil & paramètres
│   │   └── analytics/      # Analytics & stats
│   ├── services/            # Services API
│   │   └── api.js          # Configuration API (connexion au backend)
│   ├── utils/               # Utilitaires
│   │   ├── theme.js        # Thème de l'app
│   │   ├── constants.js    # Constantes
│   │   └── helpers.js      # Fonctions helpers
│   └── assets/              # Images, icons, fonts
├── App.js                   # Point d'entrée principal
├── index.js                 # Entry point React Native
├── package.json             # Dépendances
└── README.md               # Ce fichier

```

## 🚀 Installation & Démarrage

### Prérequis

#### Pour tous les développeurs :
- **Node.js** 16+ et **npm/yarn**
- **React Native CLI** : `npm install -g react-native-cli`
- **Watchman** (macOS) : `brew install watchman`

#### Pour Android :
- **Android Studio** avec SDK 33
- **Java JDK** 11+
- **Android Emulator** configuré

#### Pour iOS (macOS uniquement) :
- **Xcode** 14+
- **CocoaPods** : `sudo gem install cocoapods`
- **iOS Simulator**

### 📦 Installation des dépendances

```bash
cd mobile
npm install  # ou yarn install

# Pour iOS uniquement
cd ios && pod install && cd ..
```

### ⚙️ Configuration de l'API

Modifiez `src/services/api.js` pour pointer vers votre backend :

```javascript
const API_BASE_URL = __DEV__
  ? 'http://10.0.2.2:8001'  // Android emulator (ou votre IP locale)
  : 'https://your-production-api.com';
```

**Important :**
- Pour Android emulator : `http://10.0.2.2:8001`
- Pour iOS simulator : `http://localhost:8001`
- Pour device réel : `http://YOUR_LOCAL_IP:8001` (ex: `http://192.168.1.10:8001`)

### 🏃 Lancer l'application

#### Android

```bash
# Terminal 1 : Démarrer Metro Bundler
npm start

# Terminal 2 : Lancer sur Android
npm run android

# Ou directement avec un device spécifique
react-native run-android --deviceId=DEVICE_ID
```

#### iOS (macOS uniquement)

```bash
# Terminal 1 : Démarrer Metro Bundler
npm start

# Terminal 2 : Lancer sur iOS
npm run ios

# Ou avec un simulateur spécifique
react-native run-ios --simulator="iPhone 14 Pro"
```

## 📲 Fonctionnalités Implémentées

### ✅ Authentification
- [x] Écran de connexion avec validation
- [x] Écran d'inscription (Influenceur/Marchand)
- [x] Mot de passe oublié
- [x] Stockage sécurisé du token (AsyncStorage)
- [x] Auto-login au démarrage

### ✅ Navigation
- [x] Navigation par tabs (Bottom tabs)
- [x] Navigation par stack
- [x] Navigation adaptée par rôle
- [x] Back navigation gérée

### ✅ API Service
- [x] Configuration axios
- [x] Intercepteurs (auth token, errors)
- [x] APIs d'authentification
- [x] APIs dashboard
- [x] APIs marketplace
- [x] APIs affiliation
- [x] APIs produits
- [x] APIs analytics
- [x] APIs messagerie
- [x] APIs notifications
- [x] APIs paramètres
- [x] APIs abonnements

### 📋 Écrans à Compléter

Les écrans suivants sont à implémenter (templates fournis dans la structure) :

#### Dashboard Screens
- `src/screens/dashboard/DashboardScreen.js` - Dashboard générique
- `src/screens/dashboard/InfluencerDashboard.js` - Dashboard influenceur
- `src/screens/dashboard/MerchantDashboard.js` - Dashboard marchand
- `src/screens/dashboard/AdminDashboard.js` - Dashboard admin

#### Marketplace Screens
- `src/screens/marketplace/MarketplaceScreen.js` - Liste des produits
- `src/screens/marketplace/ProductDetailScreen.js` - Détails produit

#### Influencer Screens
- `src/screens/influencer/MyLinksScreen.js` - Liste des liens d'affiliation
- `src/screens/influencer/LinkStatsScreen.js` - Statistiques d'un lien

#### Merchant Screens
- `src/screens/merchant/ProductsListScreen.js` - Liste des produits
- `src/screens/merchant/CreateProductScreen.js` - Créer/Éditer un produit
- `src/screens/merchant/AffiliationRequestsScreen.js` - Demandes d'affiliation

#### Messages Screens
- `src/screens/messages/MessagesScreen.js` - Liste des conversations
- `src/screens/messages/ChatScreen.js` - Conversation

#### Profile Screens
- `src/screens/profile/ProfileScreen.js` - Profil utilisateur
- `src/screens/profile/SettingsScreen.js` - Paramètres
- `src/screens/profile/EditProfileScreen.js` - Éditer le profil

#### Analytics Screens
- `src/screens/analytics/AnalyticsScreen.js` - Analytics dashboard
- `src/screens/analytics/ConversionsScreen.js` - Conversions détaillées

### 🎨 Composants UI à Créer

Composants réutilisables à implémenter :

```
src/components/
├── common/
│   ├── Button.js           # Bouton personnalisé
│   ├── Card.js             # Card UI
│   ├── Input.js            # Input personnalisé
│   ├── Badge.js            # Badge (status, etc.)
│   ├── Avatar.js           # Avatar utilisateur
│   ├── EmptyState.js       # État vide
│   └── LoadingSpinner.js   # Loading indicator
└── charts/
    ├── LineChart.js        # Graphique ligne
    ├── BarChart.js         # Graphique barres
    └── PieChart.js         # Graphique circulaire
```

## 🎨 Thème & Design

Le thème est configuré dans `src/utils/theme.js` :

```javascript
// Couleurs principales
primary: '#6366f1',      // Indigo
secondary: '#8b5cf6',    // Purple
accent: '#f59e0b',       // Amber
success: '#10b981',      // Green
error: '#ef4444',        // Red
warning: '#f59e0b',      // Amber
```

## 📱 Build Production

### Android (.apk / .aab)

1. **Générer une clé de signature :**

```bash
cd android/app
keytool -genkeypair -v -storetype PKCS12 -keystore shareyoursales-release-key.keystore -alias shareyoursales-release -keyalg RSA -keysize 2048 -validity 10000
```

2. **Configurer gradle.properties :**

```properties
SHAREYOURSALES_UPLOAD_STORE_FILE=shareyoursales-release-key.keystore
SHAREYOURSALES_UPLOAD_KEY_ALIAS=shareyoursales-release
SHAREYOURSALES_UPLOAD_STORE_PASSWORD=your_keystore_password
SHAREYOURSALES_UPLOAD_KEY_PASSWORD=your_key_password
```

3. **Build APK :**

```bash
cd android
./gradlew assembleRelease

# APK disponible dans :
# android/app/build/outputs/apk/release/app-release.apk
```

4. **Build AAB (Google Play) :**

```bash
cd android
./gradlew bundleRelease

# AAB disponible dans :
# android/app/build/outputs/bundle/release/app-release.aab
```

### iOS (.ipa)

1. **Ouvrir Xcode :**

```bash
open ios/ShareYourSales.xcworkspace
```

2. **Dans Xcode :**
   - Sélectionner "Generic iOS Device" ou votre device
   - Product > Archive
   - Distribute App > App Store Connect / Ad Hoc

3. **Ou via CLI (avec fastlane) :**

```bash
cd ios
fastlane build
```

## 🚀 Déploiement

### 📱 Google Play Store (Android)

1. Créer un compte développeur Google Play (25$ one-time)
2. Créer une nouvelle application
3. Remplir les informations (description, screenshots, etc.)
4. Upload l'AAB : `android/app/build/outputs/bundle/release/app-release.aab`
5. Soumettre pour review

**Screenshots requis :**
- Phone : 16:9 (1920x1080) - min 2 screenshots
- 7" Tablet : 16:9 (1920x1080) - min 1 screenshot
- 10" Tablet : 16:9 (1920x1080) - min 1 screenshot

### 🍎 App Store (iOS)

1. Créer un compte Apple Developer (99$/an)
2. Créer une App ID dans Apple Developer Portal
3. Créer l'app dans App Store Connect
4. Préparer les assets :
   - Icon 1024x1024
   - Screenshots iPhone (6.7", 6.5", 5.5")
   - Screenshots iPad (12.9", 10.5")
5. Upload via Xcode Archive ou Application Loader
6. Soumettre pour review

## 🔧 Configuration Avancée

### Push Notifications

1. **Firebase Cloud Messaging (Android & iOS) :**

```bash
npm install @react-native-firebase/app @react-native-firebase/messaging
```

2. Ajouter `google-services.json` (Android) et `GoogleService-Info.plist` (iOS)

3. Configuration dans `App.js`

### Deep Linking

Configuration dans `AndroidManifest.xml` et `Info.plist` pour ouvrir l'app via liens :

```
shareyoursales://marketplace/product/123
```

### Analytics

Intégrer Firebase Analytics, Mixpanel, ou Amplitude pour tracking.

## 🐛 Debug

### Activer le mode debug

```bash
# Android
adb shell input keyevent 82  # Ouvre dev menu

# iOS
Cmd + D dans le simulateur
```

### Logs

```bash
# Android
react-native log-android

# iOS
react-native log-ios
```

### React Native Debugger

```bash
npm install -g react-native-debugger
react-native-debugger
```

## 📦 Dépendances Principales

- **react-native** : Framework mobile
- **@react-navigation** : Navigation
- **react-native-paper** : UI components (Material Design)
- **axios** : HTTP client
- **@react-native-async-storage** : Local storage
- **react-native-vector-icons** : Icons
- **react-native-chart-kit** : Charts
- **react-native-svg** : SVG support

## 🔒 Sécurité

- **Token JWT** stocké dans AsyncStorage (encrypted)
- **HTTPS** obligatoire en production
- **Code obfuscation** avec ProGuard (Android) et bitcode (iOS)
- **Certificate pinning** recommandé pour API calls

## 📄 Licence

Proprietary - ShareYourSales © 2025

## 🤝 Support

Pour toute question :
- Email : support@shareyoursales.ma
- Documentation complète : https://docs.shareyoursales.ma

---

## ✅ Next Steps

1. **Compléter les écrans** listés dans la section "Écrans à Compléter"
2. **Créer les composants UI** réutilisables
3. **Tester sur devices réels** (Android & iOS)
4. **Optimiser les performances** (images, lazy loading, etc.)
5. **Ajouter les tests** (Jest, Detox)
6. **Préparer les assets** (icon, splash screen, screenshots)
7. **Build & deploy** sur les stores

**Temps estimé pour complétion : 2-3 semaines**

Bon développement ! 🚀
