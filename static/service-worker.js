const CACHE_NAME = "habit-track-cache-v1";
const urlsToCache = [
  "/",
  "/analytics",
  "/settings",
  "/export",
  "/static/styles.css",
  "/static/manifest.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "https://unpkg.com/htmx.org@1.9.2",
  "https://cdn.jsdelivr.net/npm/alpinejs",
  "https://cdn.jsdelivr.net/npm/chart.js"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
