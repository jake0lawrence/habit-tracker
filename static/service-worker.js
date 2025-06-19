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
  "/static/htmx.min.js",
  "/static/alpine.min.js",
  "/static/chart.min.js"
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
