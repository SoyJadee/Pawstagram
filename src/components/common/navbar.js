import { authService } from '../../services/auth.js';

export function init() {
    setupNavigation();
    updateAuthUI();
    setupEventListeners();
}

function setupNavigation() {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Profile dropdown
    const profileDropdown = document.getElementById('profile-dropdown');
    const dropdownMenu = document.getElementById('dropdown-menu');
    
    if (profileDropdown && dropdownMenu) {
        profileDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('hidden');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            dropdownMenu.classList.add('hidden');
        });
    }
}

async function updateAuthUI() {
    const user = await authService.getCurrentUser();
    const userMenu = document.getElementById('user-menu');
    const authButtons = document.getElementById('auth-buttons');
    
    if (user) {
        userMenu?.classList.remove('hidden');
        authButtons?.classList.add('hidden');
        
        // Update user info if profile exists
        // This would typically fetch profile data from the database
        updateUserDisplay(user);
    } else {
        userMenu?.classList.add('hidden');
        authButtons?.classList.remove('hidden');
    }
}

function updateUserDisplay(user) {
    const userName = document.getElementById('user-name');
    const userAvatar = document.getElementById('user-avatar');
    
    if (userName) {
        userName.textContent = user.email.split('@')[0]; // Fallback to email username
    }
    
    // Avatar would be updated with actual profile image
    // This is a placeholder implementation
}

function setupEventListeners() {
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const result = await authService.signOut();
            if (result.success) {
                updateAuthUI();
                window.location.href = '/';
            }
        });
    }
}