// Service Worker for OUrLove PWA
const CACHE_NAME = 'ourlove-cache-v1';

// List of files to cache for offline use
const STATIC_CACHE = 'ourlove-static-v1';
const DYNAMIC_CACHE = 'ourlove-dynamic-v1';

// List of critical static assets to cache immediately
const CRITICAL_ASSETS = [
    '/',
    '/offline/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/images/icons/icon-192x192.svg',
    '/static/images/icons/icon-512x512.svg',
    '/favicon.ico'
];

// Third-party assets to cache with lower priority
const THIRD_PARTY_ASSETS = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    'https://unpkg.com/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css',
    'https://unpkg.com/persian-date@1.1.0/dist/persian-date.min.js',
    'https://unpkg.com/persian-datepicker@1.2.0/dist/js/persian-datepicker.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

// Maximum age for dynamic cache items (1 week)
const MAX_DYNAMIC_CACHE_AGE = 7 * 24 * 60 * 60 * 1000; // 1 week in milliseconds

// Install event - cache essential files
self.addEventListener('install', event => {
    console.log('[Service Worker] Installing...');
    
    // Skip waiting to ensure the new service worker activates immediately
    self.skipWaiting();
    
    event.waitUntil(
        Promise.all([
            // Cache critical assets first (high priority)
            caches.open(STATIC_CACHE)
                .then(cache => {
                    console.log('[Service Worker] Caching critical assets');
                    return cache.addAll(CRITICAL_ASSETS);
                }),
            // Cache third-party assets separately (lower priority)
            caches.open(STATIC_CACHE)
                .then(cache => {
                    console.log('[Service Worker] Caching third-party assets');
                    // We use individual promises to prevent one failed resource from failing the entire cache
                    return Promise.allSettled(
                        THIRD_PARTY_ASSETS.map(url => 
                            cache.add(url).catch(error => 
                                console.log(`Failed to cache ${url}: ${error}`)
                            )
                        )
                    );
                })
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activating...');
    
    // Take control of all clients immediately
    self.clients.claim();
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (![STATIC_CACHE, DYNAMIC_CACHE].includes(cacheName)) {
                        console.log('[Service Worker] Removing old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Helper function to limit the size of dynamic cache
const limitCacheSize = (cacheName, maxItems) => {
    caches.open(cacheName).then(cache => {
        cache.keys().then(keys => {
            if (keys.length > maxItems) {
                cache.delete(keys[0]).then(
                    limitCacheSize(cacheName, maxItems)
                );
            }
        });
    });
};

// Clean old dynamic cache items
const cleanDynamicCache = async () => {
    const cache = await caches.open(DYNAMIC_CACHE);
    const keys = await cache.keys();
    const now = Date.now();
    
    for (const request of keys) {
        // Get the cache entry
        const response = await cache.match(request);
        
        // Check if we have timestamp metadata
        const responseClone = response.clone();
        const cacheData = await responseClone.headers.get('sw-cache-timestamp');
        
        if (cacheData) {
            const timestamp = parseInt(cacheData);
            if (now - timestamp > MAX_DYNAMIC_CACHE_AGE) {
                // Item is too old, remove it
                console.log('[Service Worker] Removing old cache item:', request.url);
                await cache.delete(request);
            }
        }
    }
};

// Fetch event - with optimized cache strategy
self.addEventListener('fetch', event => {
    // Don't intercept non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Handle API requests differently (network-first)
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Clone the response
                    const responseToCache = response.clone();
                    // Store in dynamic cache
                    caches.open(DYNAMIC_CACHE)
                        .then(cache => {
                            // Create a new response with timestamp metadata
                            const headers = new Headers(responseToCache.headers);
                            headers.append('sw-cache-timestamp', Date.now().toString());
                            
                            return responseToCache.blob().then(body => {
                                const newResponse = new Response(body, {
                                    status: responseToCache.status,
                                    statusText: responseToCache.statusText,
                                    headers: headers
                                });
                                
                                cache.put(event.request, newResponse);
                            });
                        });
                    return response;
                })
                .catch(() => {
                    // If network fails, try the cache
                    return caches.match(event.request);
                })
        );
        return;
    }
    
    // For HTML pages, use network-first strategy
    if (event.request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Cache the latest version
                    const responseToCache = response.clone();
                    caches.open(STATIC_CACHE).then(cache => {
                        cache.put(event.request, responseToCache);
                    });
                    return response;
                })
                .catch(async () => {
                    // If network fails, use cache
                    const cachedResponse = await caches.match(event.request);
                    return cachedResponse || caches.match('/offline/');
                })
        );
        return;
    }
    
    // For static assets use cache-first strategy
    if (event.request.url.match(/\.(css|js|svg|png|jpg|jpeg|gif|woff2|woff|ttf)$/)) {
        event.respondWith(
            caches.match(event.request)
                .then(cachedResponse => {
                    // Return cached response if available
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    
                    // Otherwise fetch from network
                    return fetch(event.request)
                        .then(response => {
                            const responseToCache = response.clone();
                            caches.open(STATIC_CACHE).then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                            // Clean cache periodically
                            limitCacheSize(STATIC_CACHE, 100);
                            return response;
                        })
                        .catch(error => {
                            // Return default icon for images
                            if (event.request.url.match(/\.(png|jpg|jpeg|gif|svg)$/)) {
                                return caches.match('/static/images/icons/icon-192x192.svg');
                            }
                            console.error('[Service Worker] Fetch failed:', error);
                            return new Response('Network error', { status: 408 });
                        });
                })
        );
        return;
    }
    
    // Default strategy for everything else (cache first, fall back to network)
    event.respondWith(
        caches.match(event.request)
            .then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                return fetch(event.request)
                    .then(response => {
                        // Don't cache if not a valid response
                        if (!response || response.status !== 200) {
                            return response;
                        }
                        
                        // Clone the response
                        const responseToCache = response.clone();
                        // Store in dynamic cache
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                                // Limit the dynamic cache size
                                limitCacheSize(DYNAMIC_CACHE, 75);
                                // Clean old items
                                cleanDynamicCache();
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // If all fails, return the offline page for navigations
                        if (event.request.mode === 'navigate') {
                            return caches.match('/offline/');
                        }
                        
                        // Return an empty response for other requests
                        return new Response('Network error happened', {
                            status: 408,
                            headers: { 'Content-Type': 'text/plain' }
                        });
                    });
            })
    );
});

// Push event - handle push notifications
self.addEventListener('push', event => {
    console.log('[Service Worker] Push received');
    const data = event.data.json();
    
    const options = {
        body: data.body || 'پیام جدید',
        icon: '/static/images/icons/icon-192x192.svg',
        badge: '/static/images/icons/icon-192x192.svg'
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'OUrLove', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', event => {
    console.log('[Service Worker] Notification click');
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow('/')
    );
});
