// main.js - Core JS functionality for OUrLove app

// Check if the device is in standalone mode (installed as PWA)
const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

// Wait for DOM to be fully loaded before initializing scripts
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components with a slight delay to prioritize critical rendering
    setTimeout(() => {
        initComponents();
    }, 50);
    
    // Immediately initialize online/offline detection
    updateOnlineStatus();
    
    // Register online/offline event listeners
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Handle PWA installation
    setupPwaInstall();
});

// Function to initialize less critical UI components
function initComponents() {
    // Initialize tooltips - using try/catch to prevent errors
    try {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        if (tooltipTriggerList.length > 0 && typeof bootstrap !== 'undefined') {
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    } catch (e) {
        console.warn('Tooltip initialization failed:', e);
    }
    
    // Initialize Persian Date Picker
    initPersianDatePicker();
}

// Check online/offline status and add indicator
function updateOnlineStatus() {
    let offlineIndicator = document.getElementById('offline-indicator');
    
    if (!offlineIndicator) {
        // Create offline indicator if it doesn't exist
        offlineIndicator = document.createElement('div');
        offlineIndicator.id = 'offline-indicator';
        offlineIndicator.className = 'offline-indicator';
        offlineIndicator.innerHTML = '<i class="fas fa-wifi-slash me-2"></i> شما آفلاین هستید';
        document.body.appendChild(offlineIndicator);
    }
    
    // Update online status and visibility
    if (navigator.onLine) {
        document.body.classList.remove('offline');
        offlineIndicator.style.display = 'none';
    } else {
        document.body.classList.add('offline');
        offlineIndicator.style.display = 'block';
    }
}

// Handle PWA installation
function setupPwaInstall() {
    let deferredPrompt;
    const installButton = document.getElementById('pwa-install');
    
    // Hide the install button by default
    if (installButton) {
        installButton.style.display = 'none';
    }
    
    // Detect if PWA installation is possible
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        
        // Show the install button if available
        if (installButton) {
            installButton.style.display = 'block';
            
            // Install button click handler
            installButton.addEventListener('click', async () => {
                // Show the install prompt
                deferredPrompt.prompt();
                // Wait for the user to respond to the prompt
                const { outcome } = await deferredPrompt.userChoice;
                // Hide the install button regardless of outcome
                installButton.style.display = 'none';
                // Reset the deferred prompt variable
                deferredPrompt = null;
            });
        }
    });
}

// Format date for display in Gregorian calendar
function getFormattedDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
}

// Initialize Date Picker on form fields with Gregorian calendar
function initPersianDatePicker() {
    // Only initialize if both jQuery and the Persian datepicker plugin are available
    if (typeof $ !== 'undefined' && typeof $.fn.persianDatepicker !== 'undefined') {
        const dateFields = document.querySelectorAll('.datepicker');
        if (dateFields.length > 0) {
            try {
                $('.datepicker').persianDatepicker({
                    format: 'YYYY/MM/DD',
                    autoClose: true,
                    initialValue: true,
                    calendar: {
                        gregorian: {
                            locale: 'en'
                        }
                    },
                    calendarType: 'gregorian',
                    onlySelectOnDate: true,
                    timePicker: {
                        enabled: false
                    },
                    toolbox: {
                        calendarSwitch: {
                            enabled: false
                        }
                    },
                    persianDigit: false,
                    onSelect: function() {
                        // Trigger change event for form validation
                        $(this.elem).trigger('change');
                    }
                });
            } catch (e) {
                console.warn('Date picker initialization failed:', e);
            }
        }
    }
}

// Lazy load non-critical images
document.addEventListener('DOMContentLoaded', () => {
    const lazyImages = [].slice.call(document.querySelectorAll('img.lazy'));
    
    if ('IntersectionObserver' in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    if (lazyImage.dataset.srcset) {
                        lazyImage.srcset = lazyImage.dataset.srcset;
                    }
                    lazyImage.classList.remove('lazy');
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });
        
        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        let active = false;
        
        const lazyLoad = function() {
            if (active === false) {
                active = true;
                
                setTimeout(function() {
                    lazyImages.forEach(function(lazyImage) {
                        if ((lazyImage.getBoundingClientRect().top <= window.innerHeight && lazyImage.getBoundingClientRect().bottom >= 0) && getComputedStyle(lazyImage).display !== "none") {
                            lazyImage.src = lazyImage.dataset.src;
                            if (lazyImage.dataset.srcset) {
                                lazyImage.srcset = lazyImage.dataset.srcset;
                            }
                            lazyImage.classList.remove("lazy");
                            
                            lazyImages = lazyImages.filter(function(image) {
                                return image !== lazyImage;
                            });
                            
                            if (lazyImages.length === 0) {
                                document.removeEventListener("scroll", lazyLoad);
                                window.removeEventListener("resize", lazyLoad);
                                window.removeEventListener("orientationchange", lazyLoad);
                            }
                        }
                    });
                    
                    active = false;
                }, 200);
            }
        };
        
        document.addEventListener("scroll", lazyLoad);
        window.addEventListener("resize", lazyLoad);
        window.addEventListener("orientationchange", lazyLoad);
        lazyLoad();
    }
});
