const CACHE = 'culinary-v4';
const ASSETS = ['/', '/static/css/style.css?v=3', '/static/js/app.js?v=3', '/manifest.json'];

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
  // Network-first for search results and API — always fresh
  if (url.includes('/search') || url.includes('/api/')) {
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return resp;
        })
        .catch(() => caches.match(e.request).then(r => r || new Response('Offline', {status: 503})))
    );
  } else if (url.includes('/static/') || url.endsWith('.css') || url.endsWith('.js')) {
    // Stale-while-revalidate — serve cache instantly, update in background
    e.respondWith(
      caches.match(e.request).then(cached => {
        const fetchPromise = fetch(e.request).then(resp => {
          caches.open(CACHE).then(c => c.put(e.request, resp.clone()));
          return resp;
        }).catch(() => null);
        return cached || fetchPromise;
      })
    );
  } else {
    // Cache-first for HTML and manifest
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
        const clone = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return resp;
      }).catch(() => new Response('Offline', {status: 503})))
    );
  }
});
