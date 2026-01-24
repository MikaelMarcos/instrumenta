const CACHE_NAME = 'caern-app-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/bootstrap.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/htmx.min.js',
  '/static/css/all.min.css',
  '/static/webfonts/fa-solid-900.woff2',
  '/corte_vazao',
  '/calculadora_k',
  '/biblioteca_equipamentos'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Network first, fall back to cache strategy for HTML
  // Cache first for static assets
  
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match(event.request);
      })
    );
  } else {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  }
});
