const CACHE_NAME = "habit-cache-v1";
const urlsToCache = [
  "/",
  "/analytics",
  "/settings",
  "/static/styles.css",
  "/static/manifest.json",
  "https://unpkg.com/htmx.org@1.9.2",
  "https://cdn.jsdelivr.net/npm/alpinejs",
  "https://cdn.jsdelivr.net/npm/chart.js"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
