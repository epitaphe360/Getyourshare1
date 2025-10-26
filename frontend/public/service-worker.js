/* eslint-disable no-restricted-globals */

/**
 * Service Worker pour ShareYourSales PWA
 * Permet le fonctionnement offline et les performances optimisées
 */

const CACHE_NAME = 'shareyoursales-v1.0.0';
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/offline.html'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installation en cours...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Mise en cache des fichiers');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] Installé avec succès');
        return self.skipWaiting();
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activation...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Suppression ancien cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Activé');
      return self.clients.claim();
    })
  );
});

// Stratégie de cache: Network First, falling back to Cache
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Ignorer les requêtes non-GET
  if (request.method !== 'GET') {
    return;
  }

  // Ignorer les requêtes vers l'API backend (toujours fetch)
  if (request.url.includes('/api/')) {
    return fetch(request);
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        // Clone la réponse car elle ne peut être consommée qu'une fois
        const responseToCache = response.clone();

        caches.open(CACHE_NAME)
          .then((cache) => {
            cache.put(request, responseToCache);
          });

        return response;
      })
      .catch(() => {
        // Si le réseau échoue, essayer le cache
        return caches.match(request)
          .then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }

            // Si pas dans le cache, retourner la page offline
            if (request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Background Sync pour les requêtes en attente
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background Sync:', event.tag);

  if (event.tag === 'sync-payouts') {
    event.waitUntil(syncPendingPayouts());
  }
});

// Push Notifications
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push reçu:', event);

  let notificationData = {};

  try {
    notificationData = event.data.json();
  } catch (e) {
    notificationData = {
      title: 'ShareYourSales',
      body: event.data.text(),
      icon: '/icons/icon-192x192.png'
    };
  }

  const options = {
    body: notificationData.body,
    icon: notificationData.icon || '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    tag: notificationData.tag || 'default',
    data: notificationData.data || {},
    actions: notificationData.actions || [
      {
        action: 'open',
        title: 'Ouvrir',
        icon: '/icons/icon-72x72.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Gestion des clics sur les notifications
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification cliquée:', event.action);

  event.notification.close();

  const urlToOpen = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then((windowClients) => {
      // Vérifier si une fenêtre est déjà ouverte
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }

      // Sinon, ouvrir une nouvelle fenêtre
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Message Handler (communication avec l'app)
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message reçu:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then((cache) => cache.addAll(event.data.payload))
    );
  }
});

// Helper: Sync pending payouts
async function syncPendingPayouts() {
  try {
    // Récupérer les payouts en attente depuis IndexedDB
    const pendingPayouts = await getPendingPayouts();

    if (pendingPayouts.length > 0) {
      console.log('[Service Worker] Syncing', pendingPayouts.length, 'payouts');

      for (const payout of pendingPayouts) {
        await fetch('/api/mobile-payments/request-payout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${payout.token}`
          },
          body: JSON.stringify(payout.data)
        });

        // Supprimer de IndexedDB après succès
        await removePendingPayout(payout.id);
      }

      console.log('[Service Worker] Sync terminé');
    }
  } catch (error) {
    console.error('[Service Worker] Sync error:', error);
  }
}

// Helper: Get pending payouts from IndexedDB
async function getPendingPayouts() {
  // TODO: Implémenter avec IndexedDB
  return [];
}

// Helper: Remove payout from IndexedDB
async function removePendingPayout(id) {
  // TODO: Implémenter avec IndexedDB
  return Promise.resolve();
}

// Periodic Background Sync (si supporté)
self.addEventListener('periodicsync', (event) => {
  console.log('[Service Worker] Periodic Sync:', event.tag);

  if (event.tag === 'update-content') {
    event.waitUntil(updateCachedContent());
  }
});

async function updateCachedContent() {
  console.log('[Service Worker] Mise à jour du cache...');

  try {
    const cache = await caches.open(CACHE_NAME);

    // Mettre à jour les fichiers critiques
    await cache.addAll(urlsToCache);

    console.log('[Service Worker] Cache mis à jour');
  } catch (error) {
    console.error('[Service Worker] Erreur mise à jour cache:', error);
  }
}

console.log('[Service Worker] Loaded');
