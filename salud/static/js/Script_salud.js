// Cerrar modal de comentarios al hacer click fuera
document.addEventListener('mousedown', function(e) {
    const modal = document.getElementById('commentsModal');
    if (!modal.classList.contains('hidden')) {
        const modalContent = modal.querySelector('div.max-w-2xl');
        if (modalContent && !modalContent.contains(e.target)) {
            closeCommentsModal();
        }
    }
});
window._userLocation = {lat: null, lon: null};
function initUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            window._userLocation.lat = position.coords.latitude;
            window._userLocation.lon = position.coords.longitude;
        }, function() {
            window._userLocation.lat = null;
            window._userLocation.lon = null;
        });
    }
}
document.addEventListener('DOMContentLoaded', initUserLocation);
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'mint': '#98E4D6',
                'light-blue': '#87CEEB',
                'soft-mint': '#E8F8F5'
            }
        }
    }
}
window.veterinariasData = window.veterinariasData || [];
let currentRating = 0;
function getUserLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            callback(position.coords.latitude, position.coords.longitude);
        }, function() {
            callback(null, null);
        });
    } else {
        callback(null, null);
    }
}
function calculateDistance(lat1, lon1, lat2, lon2) {
    function toRad(x) { return x * Math.PI / 180; }
    var R = 6371;
    var dLat = toRad(lat2 - lat1);
    var dLon = toRad(lon2 - lon1);
    var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}
function filterServices(type) {
    const cards = document.querySelectorAll('.service-card');
    const buttons = document.querySelectorAll('.filter-btn');
    const distanceSelect = document.querySelector('select');
    const maxDistance = distanceSelect.value;
    buttons.forEach(btn => {
        btn.classList.remove('bg-mint', 'text-white');
        btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    buttons.forEach(btn => {
        if ((type === 'all' && btn.textContent.includes('Todos')) ||
            ((type === 'veterinaria' || type === 'veterinario') && btn.textContent.includes('Veterinarios')) ||
            (type === 'peluqueria' && btn.textContent.includes('Peluquerías')) ||
            (type === 'spa' && btn.textContent.includes('Spa'))) {
            btn.classList.remove('bg-gray-200', 'text-gray-700');
            btn.classList.add('bg-mint', 'text-white');
        }
    });
    const userLat = window._userLocation.lat;
    const userLon = window._userLocation.lon;
    cards.forEach((card) => {
        let cardType = card.dataset.type;
        let showType = (type === 'all') || (type === cardType) || (type === 'veterinaria' && cardType === 'veterinaria');
        let showDistance = true;
        let cardName = card.querySelector('h3') ? card.querySelector('h3').textContent.trim() : null;
        let v = null;
        if (cardName && window.veterinariasData) {
            v = window.veterinariasData.find(obj => obj.name === cardName);
        }
        if (maxDistance !== 'all') {
            if (userLat !== null && userLon !== null && v && v.coords) {
                let lat = v.coords.lat;
                let lon = v.coords.lon;
                let dist = calculateDistance(userLat, userLon, lat, lon);
                showDistance = dist <= parseInt(maxDistance);
            } else {
                showDistance = false;
            }
        }
        card.style.display = (showType && showDistance) ? 'block' : 'none';
    });
}
document.querySelector('select').addEventListener('change', function() {
    filterServices('all');
});
function showContact(name, phone, email) {
    document.getElementById('contactName').textContent = name;
    document.getElementById('contactPhone').innerHTML = phone ? `<span>${phone}</span>` : '<span class="text-gray-400">No disponible</span>';
    document.getElementById('contactEmail').innerHTML = email ? `<span>${email}</span>` : '<span class="text-gray-400">No disponible</span>';
    document.getElementById('contactModal').classList.remove('hidden');
}
function closeContactModal() {
    document.getElementById('contactModal').classList.add('hidden');
}
function callNow() {
    const phone = document.getElementById('contactPhone').textContent;
    alert(`Llamando a ${phone}...`);
    closeContactModal();
}
