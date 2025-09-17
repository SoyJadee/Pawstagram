export function init() {
    setupNotificationTabs();
    setupNotificationActions();
}

function setupNotificationTabs() {
    const tabs = document.querySelectorAll('.notification-tab');
    const notifications = document.querySelectorAll('.notification-item');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Filter notifications
            const filter = tab.getAttribute('data-filter');
            filterNotifications(filter, notifications);
        });
    });
}

function filterNotifications(filter, notifications) {
    notifications.forEach(notification => {
        const type = notification.getAttribute('data-type');
        
        if (filter === 'all' || type === filter) {
            notification.style.display = 'block';
        } else {
            notification.style.display = 'none';
        }
    });
}

function setupNotificationActions() {
    // Mark all as read
    const markAllReadBtn = document.getElementById('mark-all-read');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', () => {
            const unreadNotifications = document.querySelectorAll('.notification-item.unread');
            unreadNotifications.forEach(notification => {
                notification.classList.remove('unread');
                notification.classList.add('read');
                
                // Remove the unread indicator dot
                const indicator = notification.querySelector('.w-3.h-3.bg-primary-500');
                if (indicator) {
                    indicator.remove();
                }
            });
            
            // Update button text
            markAllReadBtn.textContent = 'Todo marcado como leído';
            markAllReadBtn.disabled = true;
            markAllReadBtn.classList.add('opacity-50');
        });
    }

    // Handle notification clicks
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Don't trigger if clicking on a button
            if (e.target.tagName === 'BUTTON') return;
            
            // Mark as read
            item.classList.remove('unread');
            item.classList.add('read');
            
            // Remove unread indicator
            const indicator = item.querySelector('.w-3.h-3.bg-primary-500');
            if (indicator) {
                indicator.remove();
            }
            
            // Here you would typically navigate to the related content
            console.log('Clicked notification:', item);
        });
    });
}