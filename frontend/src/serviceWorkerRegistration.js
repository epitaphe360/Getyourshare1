/**
 * Service Worker Registration
 * Enregistre le service worker pour activer la PWA
 */

// Cette variable indique si le navigateur supporte les service workers
const isLocalhost = Boolean(
  window.location.hostname === 'localhost' ||
  window.location.hostname === '[::1]' ||
  window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/)
);

export function register(config) {
  if ('serviceWorker' in navigator) {
    const publicUrl = new URL(process.env.PUBLIC_URL, window.location.href);

    if (publicUrl.origin !== window.location.origin) {
      return;
    }

    window.addEventListener('load', () => {
      const swUrl = `${process.env.PUBLIC_URL}/service-worker.js`;

      if (isLocalhost) {
        checkValidServiceWorker(swUrl, config);

        navigator.serviceWorker.ready.then(() => {
          console.log(
            'Cette application fonctionne en mode PWA avec cache-first sur localhost.'
          );
        });
      } else {
        registerValidSW(swUrl, config);
      }
    });
  }
}

function registerValidSW(swUrl, config) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      console.log('✅ Service Worker enregistré avec succès');

      registration.onupdatefound = () => {
        const installingWorker = registration.installing;

        if (installingWorker == null) {
          return;
        }

        installingWorker.onstatechange = () => {
          if (installingWorker.state === 'installed') {
            if (navigator.serviceWorker.controller) {
              // Nouvelle version disponible
              console.log('🔄 Nouvelle version disponible ! Rechargez pour mettre à jour.');

              if (config && config.onUpdate) {
                config.onUpdate(registration);
              }

              // Afficher une notification à l'utilisateur
              showUpdateNotification();
            } else {
              // Contenu mis en cache pour utilisation offline
              console.log('📦 Contenu mis en cache pour utilisation offline.');

              if (config && config.onSuccess) {
                config.onSuccess(registration);
              }
            }
          }
        };
      };

      // Enregistrer pour les notifications push (si supporté)
      if ('PushManager' in window) {
        registerPushNotifications(registration);
      }

      // Enregistrer pour background sync (si supporté)
      if ('sync' in registration) {
        console.log('✅ Background Sync supporté');
      }

      // Enregistrer pour periodic sync (si supporté)
      if ('periodicSync' in registration) {
        console.log('✅ Periodic Background Sync supporté');
        registerPeriodicSync(registration);
      }
    })
    .catch((error) => {
      console.error('❌ Erreur lors de l\'enregistrement du Service Worker:', error);
    });
}

function checkValidServiceWorker(swUrl, config) {
  fetch(swUrl, {
    headers: { 'Service-Worker': 'script' },
  })
    .then((response) => {
      const contentType = response.headers.get('content-type');

      if (
        response.status === 404 ||
        (contentType != null && contentType.indexOf('javascript') === -1)
      ) {
        navigator.serviceWorker.ready.then((registration) => {
          registration.unregister().then(() => {
            window.location.reload();
          });
        });
      } else {
        registerValidSW(swUrl, config);
      }
    })
    .catch(() => {
      console.log('❌ Pas de connexion Internet. L\'app fonctionne en mode offline.');
    });
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister();
      })
      .catch((error) => {
        console.error(error.message);
      });
  }
}

// Fonction pour afficher une notification de mise à jour
function showUpdateNotification() {
  const shouldUpdate = window.confirm(
    '🆕 Une nouvelle version de ShareYourSales est disponible ! Voulez-vous mettre à jour maintenant ?'
  );

  if (shouldUpdate) {
    window.location.reload();
  }
}

// Enregistrement des Push Notifications
async function registerPushNotifications(registration) {
  try {
    const permission = await Notification.requestPermission();

    if (permission === 'granted') {
      console.log('✅ Notifications Push autorisées');

      // Souscrire aux notifications push
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(
          process.env.REACT_APP_VAPID_PUBLIC_KEY || ''
        )
      });

      console.log('✅ Abonné aux notifications push:', subscription);

      // Envoyer la subscription au serveur
      await sendSubscriptionToServer(subscription);
    } else {
      console.log('❌ Notifications Push refusées');
    }
  } catch (error) {
    console.error('❌ Erreur lors de l\'enregistrement des push notifications:', error);
  }
}

// Enregistrement du Periodic Sync
async function registerPeriodicSync(registration) {
  try {
    await registration.periodicSync.register('update-content', {
      minInterval: 24 * 60 * 60 * 1000 // 24 heures
    });

    console.log('✅ Periodic Sync enregistré');
  } catch (error) {
    console.error('❌ Erreur Periodic Sync:', error);
  }
}

// Helper: Convertir VAPID key
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

// Envoyer la subscription au serveur
async function sendSubscriptionToServer(subscription) {
  try {
    const token = localStorage.getItem('token');

    if (!token) {
      console.log('⚠️ Utilisateur non connecté, subscription non envoyée');
      return;
    }

    await fetch('/api/notifications/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(subscription)
    });

    console.log('✅ Subscription envoyée au serveur');
  } catch (error) {
    console.error('❌ Erreur envoi subscription:', error);
  }
}

// Vérifier si l'app est installée (PWA)
export function checkIfPWA() {
  const isPWA = window.matchMedia('(display-mode: standalone)').matches ||
                window.navigator.standalone ||
                document.referrer.includes('android-app://');

  if (isPWA) {
    console.log('✅ App lancée en mode PWA');
  }

  return isPWA;
}

// Afficher le prompt d'installation PWA
export function showInstallPrompt() {
  let deferredPrompt;

  window.addEventListener('beforeinstallprompt', (e) => {
    // Empêcher le mini-infobar d'apparaître sur mobile
    e.preventDefault();

    // Stocker l'événement pour l'utiliser plus tard
    deferredPrompt = e;

    // Afficher le bouton d'installation personnalisé
    const installButton = document.getElementById('install-button');

    if (installButton) {
      installButton.style.display = 'block';

      installButton.addEventListener('click', () => {
        // Cacher le bouton
        installButton.style.display = 'none';

        // Afficher le prompt
        deferredPrompt.prompt();

        // Attendre la réponse de l'utilisateur
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            console.log('✅ Utilisateur a accepté l\'installation');
          } else {
            console.log('❌ Utilisateur a refusé l\'installation');
          }

          deferredPrompt = null;
        });
      });
    }
  });

  window.addEventListener('appinstalled', () => {
    console.log('✅ PWA installée avec succès !');

    // Analytics ou autre action
  });
}

// Envoyer une notification test
export async function sendTestNotification() {
  if ('serviceWorker' in navigator && 'Notification' in window) {
    const permission = await Notification.requestPermission();

    if (permission === 'granted') {
      const registration = await navigator.serviceWorker.ready;

      registration.showNotification('ShareYourSales', {
        body: '🎉 Les notifications sont activées !',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        tag: 'test',
        actions: [
          {
            action: 'open',
            title: 'Ouvrir l\'app'
          }
        ]
      });
    }
  }
}
