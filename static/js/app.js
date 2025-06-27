// Kolekta - Modern Web App JavaScript
// Handles liquid glass UI interactions, notifications, and real-time features

class KolektaApp {
    constructor() {
        this.notifications = [];
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupNotifications();
        this.setupLocationServices();
        this.setupRealTimeUpdates();
        this.setupAnimations();
    }

    // Navigation and UI interactions
    setupNavigation() {
        // Mobile navigation toggle
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
        }

        // Profile dropdown
        const profileDropdown = document.querySelector('.profile-dropdown');
        if (profileDropdown) {
            const profileBtn = profileDropdown.querySelector('.profile-btn');
            const dropdownMenu = profileDropdown.querySelector('.dropdown-menu');
            
            profileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownMenu.classList.toggle('show');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                dropdownMenu.classList.remove('show');
            });
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Modern notification system
    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Check for new notifications periodically
        if (this.isAuthenticated()) {
            setInterval(() => {
                this.checkForNewNotifications();
            }, 30000); // Check every 30 seconds
        }
    }

    // Show notification with liquid glass effect
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification glass-effect notification-${type}`;
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${icon} notification-icon"></i>
                <span class="notification-message">${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add enter animation
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        container.appendChild(notification);

        // Trigger animation
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        });

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification);
            }, duration);
        }

        return notification;
    }

    removeNotification(notification) {
        if (!notification.parentElement) return;
        
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle',
            match: 'handshake',
            exchange: 'coins'
        };
        return icons[type] || 'info-circle';
    }

    // Location services
    setupLocationServices() {
        this.userLocation = null;
        this.watchId = null;

        // Start watching user location if on relevant pages
        const locationPages = ['/find-exchanges', '/request-exchange', '/'];
        if (locationPages.some(page => window.location.pathname.includes(page))) {
            this.startLocationTracking();
        }
    }

    startLocationTracking() {
        if (!navigator.geolocation) {
            console.warn('Geolocation not supported');
            return;
        }

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 minutes
        };

        this.watchId = navigator.geolocation.watchPosition(
            (position) => {
                this.userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: Date.now()
                };
                this.onLocationUpdate();
            },
            (error) => {
                console.warn('Location error:', error);
                this.handleLocationError(error);
            },
            options
        );
    }

    onLocationUpdate() {
        // Update location in backend if user is authenticated
        if (this.isAuthenticated() && this.userLocation) {
            this.updateServerLocation();
        }

        // Trigger location-based updates
        this.dispatchEvent('locationUpdate', this.userLocation);
    }

    updateServerLocation() {
        if (!this.userLocation) return;

        fetch('/update-location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                latitude: this.userLocation.lat,
                longitude: this.userLocation.lng
            })
        }).catch(error => {
            console.error('Failed to update location:', error);
        });
    }

    handleLocationError(error) {
        switch(error.code) {
            case error.PERMISSION_DENIED:
                this.showNotification('Location access denied. Some features may be limited.', 'warning');
                break;
            case error.POSITION_UNAVAILABLE:
                this.showNotification('Location information unavailable.', 'warning');
                break;
            case error.TIMEOUT:
                this.showNotification('Location request timed out.', 'warning');
                break;
        }
    }

    // Real-time updates using WebSocket or polling
    setupRealTimeUpdates() {
        if (!this.isAuthenticated()) return;

        // For now, use polling. In production, consider WebSocket
        this.startPolling();
    }

    startPolling() {
        // Poll for new matches and notifications
        setInterval(() => {
            this.checkForNewMatches();
            this.checkForNewNotifications();
        }, 15000); // Every 15 seconds
    }

    async checkForNewMatches() {
        try {
            const response = await fetch('/api/check-new-matches');
            if (response.ok) {
                const data = await response.json();
                if (data.newMatches && data.newMatches.length > 0) {
                    data.newMatches.forEach(match => {
                        this.showNotification(
                            `New match found! ${match.distance}km away`,
                            'match',
                            8000
                        );
                    });
                }
            }
        } catch (error) {
            console.error('Error checking for new matches:', error);
        }
    }

    async checkForNewNotifications() {
        try {
            const response = await fetch('/api/check-notifications');
            if (response.ok) {
                const data = await response.json();
                if (data.unreadCount > 0) {
                    this.updateNotificationBadge(data.unreadCount);
                }
            }
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }

    updateNotificationBadge(count) {
        const badges = document.querySelectorAll('.notification-badge');
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count.toString();
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        });
    }

    // Liquid glass animations and effects
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe cards and glass elements
        document.querySelectorAll('.card, .glass-effect, .action-card').forEach(el => {
            observer.observe(el);
        });

        // Parallax effect for background
        window.addEventListener('scroll', this.throttle(() => {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.bg-gradient');
            
            parallaxElements.forEach(el => {
                const speed = 0.5;
                el.style.transform = `translateY(${scrolled * speed}px)`;
            });
        }, 16)); // ~60fps

        // Glass morphism hover effects
        document.querySelectorAll('.glass-btn, .glass-effect').forEach(el => {
            el.addEventListener('mouseenter', () => {
                el.style.background = 'rgba(255, 255, 255, 0.15)';
            });
            
            el.addEventListener('mouseleave', () => {
                el.style.background = 'rgba(255, 255, 255, 0.1)';
            });
        });
    }

    // Utility functions
    isAuthenticated() {
        return document.body.classList.contains('authenticated') || 
               document.querySelector('.navbar') !== null;
    }

    throttle(func, delay) {
        let timeoutId;
        let lastExecTime = 0;
        return function (...args) {
            const currentTime = Date.now();
            
            if (currentTime - lastExecTime > delay) {
                func.apply(this, args);
                lastExecTime = currentTime;
            } else {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    func.apply(this, args);
                    lastExecTime = Date.now();
                }, delay - (currentTime - lastExecTime));
            }
        };
    }

    dispatchEvent(eventName, data) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
    }

    // Public API methods
    getCurrentLocation() {
        return this.userLocation;
    }

    requestLocationPermission() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: Date.now()
                    };
                    resolve(this.userLocation);
                },
                (error) => {
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            );
        });
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in kilometers
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c; // Distance in kilometers
    }

    toRad(value) {
        return value * Math.PI / 180;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.kolektaApp = new KolektaApp();
});

// Add CSS for animations
const animationCSS = `
.animate-in {
    animation: slideUp 0.6s ease-out forwards;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.notification {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.notification-icon {
    font-size: 1.2rem;
}

.notification-message {
    flex: 1;
}

.notification-close {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: var(--transition);
}

.notification-close:hover {
    background: rgba(255, 255, 255, 0.1);
}

.notification-success {
    border-left: 4px solid var(--success);
}

.notification-error {
    border-left: 4px solid var(--error);
}

.notification-warning {
    border-left: 4px solid var(--warning);
}

.notification-info {
    border-left: 4px solid var(--info);
}

.notification-match {
    border-left: 4px solid var(--accent-blue);
}

.notification-exchange {
    border-left: 4px solid #FFD700;
}

/* Mobile navigation active state */
.nav-menu.active {
    display: flex;
    position: fixed;
    top: 100px;
    left: 1rem;
    right: 1rem;
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius);
    flex-direction: column;
    padding: 1rem;
    gap: 0.5rem;
    z-index: 1001;
}

.nav-toggle.active span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
}

.nav-toggle.active span:nth-child(2) {
    opacity: 0;
}

.nav-toggle.active span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -6px);
}

.dropdown-menu.show {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

/* Loading animation improvements */
.loading {
    border-top-color: currentColor;
}

/* Improved button states */
.glass-btn:disabled,
.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
}

/* Better focus states for accessibility */
.glass-btn:focus,
.btn-primary:focus,
.form-control:focus {
    outline: 2px solid var(--accent-blue);
    outline-offset: 2px;
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = animationCSS;
document.head.appendChild(style);