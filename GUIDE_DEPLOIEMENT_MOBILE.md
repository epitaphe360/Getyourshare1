# 📱 Guide Complet de Déploiement Mobile - ShareYourSales

## 🎯 Vue d'ensemble

Ce guide couvre le déploiement complet des applications mobiles ShareYourSales sur **Google Play Store** (Android) et **Apple App Store** (iOS).

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Préparation des Assets](#préparation-des-assets)
3. [Build Android](#build-android)
4. [Déploiement Google Play Store](#déploiement-google-play-store)
5. [Build iOS](#build-ios)
6. [Déploiement Apple App Store](#déploiement-apple-app-store)
7. [Checklist Finale](#checklist-finale)

---

## 1. Prérequis

### Comptes Requis

#### Google Play Store (Android)
- [ ] Compte Google Play Console
- [ ] Paiement unique : **25 USD**
- [ ] Vérification d'identité (peut prendre 48h)
- [ ] URL : https://play.google.com/console

#### Apple App Store (iOS)
- [ ] Compte Apple Developer Program
- [ ] Abonnement annuel : **99 USD/an**
- [ ] Vérification d'identité
- [ ] URL : https://developer.apple.com

### Outils de Développement

#### Pour Android :
```bash
# Android Studio
- SDK Tools 33+
- Android SDK Platform 33
- Android SDK Build-Tools 33.0.0

# Java Development Kit
- JDK 11 ou supérieur

# Variables d'environnement
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

#### Pour iOS (macOS uniquement) :
```bash
# Xcode
- Xcode 14+ depuis App Store
- Command Line Tools
xcode-select --install

# CocoaPods
sudo gem install cocoapods

# Fastlane (optionnel mais recommandé)
sudo gem install fastlane
```

---

## 2. Préparation des Assets

### 📱 Icon de l'Application

#### Android
Générer toutes les tailles d'icônes :

| Résolution | Taille | Chemin |
|------------|--------|--------|
| mdpi | 48x48 | `android/app/src/main/res/mipmap-mdpi/ic_launcher.png` |
| hdpi | 72x72 | `android/app/src/main/res/mipmap-hdpi/ic_launcher.png` |
| xhdpi | 96x96 | `android/app/src/main/res/mipmap-xhdpi/ic_launcher.png` |
| xxhdpi | 144x144 | `android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png` |
| xxxhdpi | 192x192 | `android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` |

**Adaptive Icon (Android 8.0+) :**
- Foreground : 108x108dp (zone safe : 72x72dp)
- Background : 108x108dp

**Outil recommandé :** https://romannurik.github.io/AndroidAssetStudio/icons-launcher.html

#### iOS
- **App Icon** : 1024x1024px (sans transparence, format PNG)
- Placer dans `ios/ShareYourSales/Images.xcassets/AppIcon.appiconset/`

**Xcode génère automatiquement** toutes les tailles nécessaires.

### 🖼️ Splash Screen

#### Android
- Créer un `launch_screen.xml` dans `android/app/src/main/res/layout/`
- Ajouter une image de splash dans `drawable/`

#### iOS
- Utiliser Xcode : Assets > LaunchScreen.storyboard

### 📸 Screenshots pour les Stores

#### Google Play Store (Android)

**Obligatoires :**
- **Phone** : 16:9 ratio
  - Min : 320px
  - Max : 3840px
  - Recommandé : 1080x1920px (portrait) ou 1920x1080px (landscape)
  - Minimum : 2 screenshots
  - Maximum : 8 screenshots

**Optionnels mais recommandés :**
- **7" Tablet** : 1920x1200px - Min 1 screenshot
- **10" Tablet** : 2560x1600px - Min 1 screenshot

**Feature Graphic (obligatoire) :**
- Taille : 1024x500px
- Format : PNG ou JPEG
- Pas de transparence

#### Apple App Store (iOS)

**iPhone obligatoires (choisir 1 taille) :**
- **6.7" display** (iPhone 14 Pro Max, 15 Pro Max) : 1290x2796px
- **6.5" display** (iPhone 11 Pro Max, XS Max) : 1242x2688px
- **5.5" display** (iPhone 8 Plus) : 1242x2208px

**iPad (si support iPad) :**
- **12.9" iPad Pro (3rd gen)** : 2048x2732px
- **11" iPad Pro** : 1668x2388px

**Quantité :**
- Minimum : 3 screenshots
- Maximum : 10 screenshots

### 📝 Descriptions & Métadonnées

Préparer pour **chaque langue** :

#### Textes Requis

**Titre de l'app :**
- Google Play : Max 30 caractères
- App Store : Max 30 caractères
- Exemple : "ShareYourSales"

**Sous-titre (iOS uniquement) :**
- Max 30 caractères
- Exemple : "Affiliation Influenceurs"

**Description courte (Android) :**
- Max 80 caractères
- Exemple : "Plateforme d'affiliation entre influenceurs et marchands au Maroc"

**Description complète :**
- Google Play : Max 4000 caractères
- App Store : Max 4000 caractères

**Exemple de description :**
```
ShareYourSales est la plateforme #1 d'affiliation au Maroc qui connecte les influenceurs avec les marchands.

🎯 Pour les Influenceurs :
✅ Découvrez des milliers de produits à promouvoir
✅ Générez vos liens d'affiliation en 1 clic
✅ Suivez vos statistiques en temps réel
✅ Recevez vos commissions rapidement

🏪 Pour les Marchands :
✅ Proposez vos produits à des milliers d'influenceurs
✅ Gérez les demandes d'affiliation
✅ Analytics détaillés
✅ Paiement sécurisé

📱 Fonctionnalités :
• Marketplace de produits
• Génération de liens trackables
• QR codes pour partage facile
• Messagerie intégrée
• Notifications en temps réel
• Statistiques détaillées
• Dashboard personnalisé par rôle

🔒 Sécurité :
• Connexion sécurisée
• Paiements cryptés
• Données protégées

Rejoignez des milliers d'influenceurs et marchands qui utilisent déjà ShareYourSales !
```

**Mots-clés (iOS uniquement) :**
- Max 100 caractères (séparés par des virgules)
- Exemple : "affiliation,influenceur,marketing,ecommerce,maroc,vente,commission,produits"

**Catégories :**
- **Google Play** : Business / Shopping
- **App Store** : Business / Shopping

---

## 3. Build Android

### Étape 1 : Générer la Clé de Signature

```bash
cd mobile/android/app

# Générer le keystore
keytool -genkeypair -v -storetype PKCS12 \
  -keystore shareyoursales-release-key.keystore \
  -alias shareyoursales-release \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Remplir les informations demandées :
# - Password : [VOTRE_PASSWORD]
# - What is your first and last name? : ShareYourSales
# - What is the name of your organizational unit? : Mobile Development
# - What is the name of your organization? : ShareYourSales
# - What is the name of your City or Locality? : Casablanca
# - What is the name of your State or Province? : Casablanca
# - What is the two-letter country code for this unit? : MA
```

**⚠️ IMPORTANT :** Sauvegarder ce keystore et le password en lieu sûr ! Vous en aurez besoin pour toutes les futures mises à jour.

### Étape 2 : Configurer Gradle

Créer/Éditer `mobile/android/gradle.properties` :

```properties
SHAREYOURSALES_UPLOAD_STORE_FILE=shareyoursales-release-key.keystore
SHAREYOURSALES_UPLOAD_KEY_ALIAS=shareyoursales-release
SHAREYOURSALES_UPLOAD_STORE_PASSWORD=YOUR_KEYSTORE_PASSWORD
SHAREYOURSALES_UPLOAD_KEY_PASSWORD=YOUR_KEY_PASSWORD

# Performance optimizations
org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.configureondemand=true
android.useAndroidX=true
android.enableJetifier=true
```

### Étape 3 : Mettre à Jour android/app/build.gradle

Vérifier les configurations de version :

```gradle
android {
    defaultConfig {
        applicationId "com.shareyoursales"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1         // Incrémenter pour chaque release
        versionName "1.0.0"   // Version visible par users
    }
}
```

### Étape 4 : Build APK (Test)

```bash
cd mobile/android
./gradlew assembleRelease

# APK généré dans :
# android/app/build/outputs/apk/release/app-release.apk

# Installer sur device pour test
adb install app/build/outputs/apk/release/app-release.apk
```

### Étape 5 : Build AAB (Production - Google Play)

```bash
cd mobile/android
./gradlew bundleRelease

# AAB généré dans :
# android/app/build/outputs/bundle/release/app-release.aab
```

**AAB vs APK :**
- **AAB** (Android App Bundle) : Format moderne, requis par Google Play, taille optimisée
- **APK** : Format classique, pour distribution hors store

### Étape 6 : Vérifier l'APK/AAB

```bash
# Obtenir des informations sur l'APK
aapt dump badging app-release.apk

# Vérifier la signature
jarsigner -verify -verbose -certs app-release.apk
```

---

## 4. Déploiement Google Play Store

### Étape 1 : Créer l'Application

1. Aller sur https://play.google.com/console
2. Créer une application
3. Remplir les informations :
   - Nom : ShareYourSales
   - Langue par défaut : Français
   - Type : Application / Jeu
   - Gratuit / Payant : Gratuit

### Étape 2 : Préparer la Fiche du Store

#### Description du Store
- **Titre court** : ShareYourSales
- **Description courte** : (max 80 chars)
- **Description complète** : (voir section Assets)

#### Graphiques
- [ ] Icon : 512x512px (PNG)
- [ ] Feature graphic : 1024x500px (obligatoire)
- [ ] Screenshots phone : Min 2, max 8
- [ ] Screenshots tablet 7" : Min 1 (optionnel)
- [ ] Screenshots tablet 10" : Min 1 (optionnel)

#### Catégorie & Tags
- Catégorie : Business ou Shopping
- Tags : affiliation, ecommerce, maroc, influenceur

### Étape 3 : Classification du Contenu

Remplir le questionnaire Google Play :
- Audience cible : 18+
- Publicité : Oui/Non (selon votre app)
- Contenu : Business app

### Étape 4 : Tarification et Distribution

- [ ] **Gratuit** (ou payant si applicable)
- [ ] **Pays disponibles** : Sélectionner pays (Maroc minimum)
- [ ] **Programme Android for Work** : Oui (recommandé)

### Étape 5 : Upload AAB

1. Aller dans "Release" > "Production"
2. Créer une nouvelle release
3. Upload `app-release.aab`
4. Remplir "Notes de version" (Release notes)

**Notes de version exemple :**
```
Version 1.0.0 - Première release

✨ Nouvelles fonctionnalités :
- Authentification complète
- Marketplace de produits
- Génération de liens d'affiliation
- Messagerie intégrée
- Analytics en temps réel
- Notifications push

🎉 C'est la première version de ShareYourSales mobile !
```

### Étape 6 : Review et Soumission

1. Vérifier toutes les sections (✅ verts requis)
2. Cliquer "Review Release"
3. Soumettre pour review

**Délai de review :**
- Première soumission : 1-7 jours
- Mises à jour ultérieures : 1-3 jours

---

## 5. Build iOS

### Étape 1 : Configuration Xcode

```bash
cd mobile/ios
pod install

# Ouvrir le workspace (PAS le .xcodeproj !)
open ShareYourSales.xcworkspace
```

### Étape 2 : Configurer le Projet dans Xcode

1. **Signing & Capabilities :**
   - Team : Sélectionner votre Apple Developer Team
   - Bundle Identifier : `com.shareyoursales` (doit être unique)
   - Signing Certificate : "iOS Distribution"

2. **General :**
   - Display Name : ShareYourSales
   - Bundle Identifier : com.shareyoursales
   - Version : 1.0.0
   - Build : 1

3. **Build Settings :**
   - Deployment Target : iOS 13.0
   - Build Configuration : Release

### Étape 3 : Créer App ID

1. Aller sur https://developer.apple.com
2. Certificates, IDs & Profiles
3. Identifiers > App IDs
4. Créer un App ID :
   - Description : ShareYourSales
   - Bundle ID : com.shareyoursales (Explicit)
   - Capabilities : Push Notifications, Associated Domains (si besoin)

### Étape 4 : Créer Provisioning Profile

1. Profiles > Distribution > App Store
2. App ID : com.shareyoursales
3. Certificate : Sélectionner votre certificat de distribution
4. Download le profile
5. Double-cliquer pour installer dans Xcode

### Étape 5 : Archive pour Distribution

1. Dans Xcode :
   - Product > Scheme > Edit Scheme
   - Run > Build Configuration : Release
   - Fermer

2. Sélectionner "Any iOS Device (arm64)" ou votre device connecté

3. Product > Archive

4. Attendre la fin du build (peut prendre 5-10 min)

### Étape 6 : Export IPA

1. Window > Organizer
2. Sélectionner votre archive
3. Distribute App
4. **App Store Connect** (pour soumission)
   - OU **Ad Hoc** (pour test sur devices)
   - OU **Development** (pour debug)
5. Next > Upload
6. Signer avec votre certificat
7. Export

**IPA généré dans :** Dossier que vous avez choisi

---

## 6. Déploiement Apple App Store

### Étape 1 : Créer l'App dans App Store Connect

1. Aller sur https://appstoreconnect.apple.com
2. My Apps > + > New App
3. Remplir :
   - Platform : iOS
   - Name : ShareYourSales
   - Primary Language : French
   - Bundle ID : com.shareyoursales
   - SKU : SHAREYOURSALES001 (identifiant unique interne)
   - User Access : Full Access

### Étape 2 : Préparer la Fiche du Store

#### App Information
- [ ] Name : ShareYourSales (30 chars max)
- [ ] Subtitle : Affiliation Influenceurs (30 chars max)
- [ ] Category : Primary = Business, Secondary = Shopping
- [ ] Privacy Policy URL : https://shareyoursales.ma/privacy

#### Pricing and Availability
- [ ] Price : Free
- [ ] Availability : All countries (ou sélectionner)

#### App Privacy
Remplir le questionnaire sur les données collectées :
- Contact Info : Email, Phone
- User Content : Photos (si upload produits)
- Identifiers : User ID
- Usage Data : Product Interaction

### Étape 3 : Version Information

#### Version 1.0.0

**Screenshots :**
- [ ] 6.7" iPhone : 1290x2796px (min 3, max 10)
- [ ] 12.9" iPad (si iPad support) : 2048x2732px

**Description :**
- [ ] Description complète (4000 chars max) - voir section Assets
- [ ] Keywords : affiliation,influenceur,maroc,business,ecommerce (100 chars max)
- [ ] Support URL : https://shareyoursales.ma/support
- [ ] Marketing URL : https://shareyoursales.ma (optionnel)

**What's New (Release Notes) :**
```
Bienvenue sur ShareYourSales !

Cette première version inclut :
✨ Marketplace de produits
📊 Génération de liens d'affiliation
💬 Messagerie intégrée
📈 Analytics en temps réel
🔔 Notifications push
🎯 Dashboards personnalisés

Rejoignez-nous et commencez à générer des revenus !
```

**App Review Information :**
- [ ] Contact : Email + Phone
- [ ] Demo Account (si login requis) :
  ```
  Username: demo@shareyoursales.ma
  Password: Demo123456
  ```
- [ ] Notes : Instructions spéciales pour testeurs

### Étape 4 : Upload Build

#### Via Xcode (Méthode 1)
1. Archive (voir Build iOS)
2. Distribute App > App Store Connect
3. Upload

#### Via Application Loader (Méthode 2 - deprecated)
Utiliser Xcode Organizer maintenant.

#### Via Fastlane (Méthode 3 - Automatisée)
```bash
cd mobile/ios
fastlane deliver
```

**Attendre 10-30 min** pour traitement par Apple.

### Étape 5 : Sélectionner le Build

1. Retourner sur App Store Connect
2. Version 1.0.0
3. Build > Select a build
4. Choisir le build uploadé

### Étape 6 : Export Compliance

Déclarer si l'app utilise du chiffrement :
- Si HTTPS uniquement : "No" à la question d'export compliance
- Si crypto custom : Remplir le formulaire approprié

### Étape 7 : Soumettre pour Review

1. Vérifier que toutes les sections sont complètes (✅)
2. "Submit for Review"
3. Confirmer

**Délai de review :**
- Première soumission : 24h - 7 jours
- Mises à jour : 24h - 48h

---

## 7. Checklist Finale

### ✅ Avant Soumission

#### Documentation
- [ ] Privacy Policy en ligne
- [ ] Terms of Service en ligne
- [ ] Support URL actif
- [ ] Site web fonctionnel

#### Tests
- [ ] Test sur Android (4-5 devices différents)
- [ ] Test sur iOS (iPhone + iPad)
- [ ] Test toutes les fonctionnalités principales
- [ ] Test login/register/forgot password
- [ ] Test paiements (si applicable)
- [ ] Test notifications push
- [ ] Test deep links
- [ ] Vérifier performance (pas de lag)
- [ ] Vérifier crashs (utiliser Crashlytics)

#### Assets
- [ ] Icon 512x512 (Android) et 1024x1024 (iOS)
- [ ] Screenshots pour toutes les tailles requises
- [ ] Feature Graphic 1024x500 (Android)
- [ ] Description traduite en toutes les langues ciblées
- [ ] Video preview (optionnel mais recommandé)

#### Backend
- [ ] API en production stable
- [ ] Base de données backupée
- [ ] Rate limiting configuré
- [ ] Monitoring actif (Sentry, etc.)
- [ ] Certificat SSL valide

#### Sécurité
- [ ] ProGuard activé (Android)
- [ ] Code obfuscation (iOS Bitcode)
- [ ] Pas de clés API en dur dans le code
- [ ] Certificate pinning (recommandé)

### ✅ Après Approval

#### Lancement
- [ ] Annoncer sur réseaux sociaux
- [ ] Email aux early users
- [ ] Communiqué de presse
- [ ] Update site web avec liens stores

#### Monitoring
- [ ] Installer analytics (Firebase, Mixpanel)
- [ ] Configurer crash reporting (Sentry, Crashlytics)
- [ ] Surveiller les reviews/ratings
- [ ] Répondre aux commentaires users

#### Marketing
- [ ] ASO (App Store Optimization)
- [ ] Campagnes pub (Google Ads, Facebook Ads)
- [ ] Influenceurs pour promotion
- [ ] Promo codes pour early adopters

---

## 📊 Métriques de Succès

### KPIs à Suivre

**Installation & Engagement :**
- Downloads (installs)
- Active users (DAU, MAU)
- Retention rate (D1, D7, D30)
- Session duration
- Session frequency

**Conversion :**
- Sign up rate
- Activation rate (premier lien généré, premier produit ajouté)
- Revenue per user
- Conversion rate

**Quality :**
- Crash-free rate (>99%)
- App rating (>4.0)
- Load time (<3s)
- API response time (<500ms)

**Tools recommandés :**
- **Analytics** : Firebase, Mixpanel, Amplitude
- **Crash Reporting** : Sentry, Crashlytics
- **Performance** : Firebase Performance Monitoring

---

## 🚀 Mises à Jour Futures

### Process de Release

1. **Incrémenter version :**
   - Android : `versionCode` et `versionName` dans `build.gradle`
   - iOS : `Version` et `Build` dans Xcode

2. **Build nouvelle version :**
   ```bash
   # Android
   cd android && ./gradlew bundleRelease

   # iOS
   # Xcode > Product > Archive
   ```

3. **Upload sur stores :**
   - Google Play : Upload AAB dans nouvelle release
   - App Store : Upload via Xcode Organizer

4. **Release notes :**
   Rédiger "What's New" clair et engageant

5. **Release progressive (recommandé) :**
   - Google Play : Staged Rollout (10% > 50% > 100%)
   - App Store : Phased Release

---

## 📞 Support & Ressources

### Documentation Officielle
- **React Native** : https://reactnative.dev/docs/getting-started
- **Google Play Console** : https://support.google.com/googleplay/android-developer
- **App Store Connect** : https://developer.apple.com/app-store-connect/

### Outils Utiles
- **App Icon Generator** : https://appicon.co/
- **Screenshot Generator** : https://www.appstorescreenshot.com/
- **ASO Tools** : https://www.apptweak.com/ , https://www.apptopia.com/

### Communautés
- React Native Discord
- Stack Overflow
- Reddit : r/reactnative

---

**Bonne chance pour le lancement ! 🎉📱**

Si vous avez des questions, contactez : support@shareyoursales.ma
