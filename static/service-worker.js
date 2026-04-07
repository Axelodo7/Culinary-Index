const CACHE = 'culinary-v1';
const ASSETS = ['/', '/static/css/style.css', '/static/js/app.js'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener('activate', e => e.waitUntil(clients.claim()));
self.addEventListener('fetch', e => { e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).catch(() => new Response('Offline', {status: 503})))); });
