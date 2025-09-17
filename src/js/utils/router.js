class Router {
    constructor() {
        this.routes = {
            '/': () => this.loadPage('home'),
            '/login': () => this.loadPage('auth/login'),
            '/register': () => this.loadPage('auth/register'),
            '/profile': () => this.loadPage('profile/profile'),
            '/feed': () => this.loadPage('posts/feed'),
            '/adoption': () => this.loadPage('adoption/adoption'),
            '/stores': () => this.loadPage('stores/stores'),
            '/notifications': () => this.loadPage('notifications/notifications'),
        };
        
        this.currentRoute = '/';
    }

    init() {
        // Handle initial route
        this.handleRoute();
        
        // Listen for browser navigation
        window.addEventListener('popstate', () => this.handleRoute());
    }

    navigate(route) {
        if (route !== this.currentRoute) {
            this.currentRoute = route;
            history.pushState(null, '', route);
            this.handleRoute();
        }
    }

    handleRoute() {
        const path = window.location.pathname;
        const routeHandler = this.routes[path] || this.routes['/'];
        routeHandler();
    }

    async loadPage(page) {
        try {
            const response = await fetch(`./src/pages/${page}.html`);
            if (!response.ok) {
                throw new Error(`Page not found: ${page}`);
            }
            
            const html = await response.text();
            document.getElementById('main-content').innerHTML = html;
            
            // Load page-specific JavaScript if it exists
            this.loadPageScript(page);
        } catch (error) {
            console.error('Error loading page:', error);
            this.loadErrorPage();
        }
    }

    async loadPageScript(page) {
        try {
            const script = await import(`../components/${page}.js`);
            if (script.init) {
                script.init();
            }
        } catch (error) {
            // Page script doesn't exist, which is fine
            console.log(`No script found for page: ${page}`);
        }
    }

    loadErrorPage() {
        document.getElementById('main-content').innerHTML = `
            <div class="flex items-center justify-center min-h-96">
                <div class="text-center">
                    <h1 class="text-4xl font-bold text-gray-800 mb-4">404</h1>
                    <p class="text-gray-600 mb-8">Página no encontrada</p>
                    <button onclick="router.navigate('/')" class="btn-primary">
                        Volver al inicio
                    </button>
                </div>
            </div>
        `;
    }
}

export const router = new Router();