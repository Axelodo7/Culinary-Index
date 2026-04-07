const CACHE = 'culinary-v3';
const ASSETS = ['/', '/static/css/style.css', '/static/js/app.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = e.request.url;
  // Network-first for CSS/JS — always try server, fall back to cache
  if (url.includes('/static/') || url.endsWith('.css') || url.endsWith('.js')) {
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return resp;
        })
        .catch(() => caches.match(e.request))
    );
  } else {
    // Cache-first for everything else
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).catch(() => new Response('Offline', {status: 503})))
    );
  }
});
