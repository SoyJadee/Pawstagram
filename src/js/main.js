// Main application entry point
import { initializeApp } from './services/app.js';
import { authService } from './services/auth.js';
import { router } from './utils/router.js';
import { loadComponent } from './utils/componentLoader.js';

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize services
        await initializeApp();
        
        // Load navigation
        await loadComponent('navbar', 'common/navbar');
        await loadComponent('footer', 'common/footer');
        
        // Check authentication status
        const user = await authService.getCurrentUser();
        
        // Initialize router
        router.init();
        
        // Set up global event listeners
        setupGlobalEventListeners();
        
        console.log('Pawstagram app initialized successfully');
    } catch (error) {
        console.error('Error initializing app:', error);
    }
});

function setupGlobalEventListeners() {
    // Handle navigation clicks
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-nav]')) {
            e.preventDefault();
            const route = e.target.getAttribute('data-nav');
            router.navigate(route);
        }
    });

    // Handle modal close clicks
    document.addEventListener('click', (e) => {
        if (e.target.matches('.modal-overlay') || e.target.matches('[data-modal-close]')) {
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }
    });

    // Handle form submissions
    document.addEventListener('submit', (e) => {
        if (e.target.matches('[data-form]')) {
            e.preventDefault();
            const formType = e.target.getAttribute('data-form');
            handleFormSubmission(formType, e.target);
        }
    });
}

function handleFormSubmission(formType, form) {
    // Handle different form types
    console.log('Form submission:', formType, form);
}