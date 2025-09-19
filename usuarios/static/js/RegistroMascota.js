
// Datos del usuario (simulamos que vienen del paso anterior)
let userData = JSON.parse(localStorage.getItem('tempUserData') || '{}');

// Razas de perros y gatos
const breeds = {
    dog: [
        'Labrador', 'Golden Retriever', 'Bulldog', 'Pastor Alemán', 'Poodle',
        'Beagle', 'Rottweiler', 'Husky Siberiano', 'Dálmata', 'Chihuahua',
        'Border Collie', 'Boxer', 'Cocker Spaniel', 'Mestizo', 'Otro'
    ],
    cat: [
        'Persa', 'Maine Coon', 'Siamés', 'British Shorthair', 'Ragdoll',
        'Bengalí', 'Abisinio', 'Russian Blue', 'Scottish Fold', 'Sphynx',
        'Angora', 'Común Europeo', 'Mestizo', 'Otro'
    ]
};

// Función para mostrar notificación
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
        type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.style.transform = 'translateX(0)', 100);
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Cargar razas según el tipo de mascota
function loadBreeds() {
    const petType = userData.petType || 'dog';
    const breedSelect = document.getElementById('breed');
    
    if (petType === 'dog' || petType === 'cat') {
        breedSelect.innerHTML = '<option value="">Seleccionar raza</option>';
        breeds[petType].forEach(breed => {
            breedSelect.innerHTML += `<option value="${breed.toLowerCase()}">${breed}</option>`;
        });
        
        document.getElementById('dogCatFields').classList.remove('hidden');
        document.getElementById('otherFields').classList.add('hidden');
    } else {
        document.getElementById('dogCatFields').classList.add('hidden');
        document.getElementById('otherFields').classList.remove('hidden');
    }
}

// Validar formulario
function validateForm() {
    const petName = document.getElementById('petName').value.trim();
    const location = document.getElementById('location').value.trim();
    const owner = document.getElementById('owner').value.trim();
    
    if (!petName || !location || !owner) {
        showNotification('Por favor completa todos los campos obligatorios', 'error');
        return false;
    }
    
    const petType = userData.petType;
    
    if (petType === 'dog' || petType === 'cat') {
        const breed = document.getElementById('breed').value;
        const age = document.getElementById('age').value;
        const weight = document.getElementById('weight').value;
        const gender = document.getElementById('gender').value;
        const availability = document.querySelector('input[name="availability"]:checked');
        const vaccines = document.querySelector('input[name="vaccines"]:checked');
        const pedigree = document.querySelector('input[name="pedigree"]:checked');
        
        if (!breed || !age || !weight || !gender || !availability || !vaccines || !pedigree) {
            showNotification('Por favor completa todos los campos de tu mascota', 'error');
            return false;
        }
    } else {
        const age = document.getElementById('ageOther').value;
        const weight = document.getElementById('weightOther').value;
        const gender = document.getElementById('genderOther').value;
        const availability = document.querySelector('input[name="availabilityOther"]:checked');
        
        if (!age || !weight || !gender || !availability) {
            showNotification('Por favor completa todos los campos de tu mascota', 'error');
            return false;
        }
    }
    
    return true;
}

// Recopilar datos de la mascota
function collectPetData() {
    const petType = userData.petType;
    const baseData = {
        name: document.getElementById('petName').value.trim(),
        location: document.getElementById('location').value.trim(),
        owner: document.getElementById('owner').value.trim()
    };
    
    if (petType === 'dog' || petType === 'cat') {
        return {
            ...baseData,
            breed: document.getElementById('breed').value,
            age: parseInt(document.getElementById('age').value),
            weight: parseFloat(document.getElementById('weight').value),
            gender: document.getElementById('gender').value,
            availability: document.querySelector('input[name="availability"]:checked').value,
            vaccines: document.querySelector('input[name="vaccines"]:checked').value,
            pedigree: document.querySelector('input[name="pedigree"]:checked').value
        };
    } else {
        return {
            ...baseData,
            age: parseInt(document.getElementById('ageOther').value),
            weight: parseFloat(document.getElementById('weightOther').value),
            gender: document.getElementById('genderOther').value,
            availability: document.querySelector('input[name="availabilityOther"]:checked').value
        };
    }
}

// Volver al paso anterior
function goBack() {
    window.location.href = 'Registro.html';
}

// Inicializar página
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay datos del usuario
    if (!userData.petType) {
        showNotification('Error: Datos del usuario no encontrados', 'error');
        setTimeout(() => {
            window.location.href = 'Registro.html';
        }, 2000);
        return;
    }
    
    // Cargar razas según tipo de mascota
    loadBreeds();
    
    // Manejar envío del formulario
    const petForm = document.getElementById('petForm');
    petForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        // Recopilar todos los datos
        const petData = collectPetData();
        const completeData = {
            user: userData,
            pet: petData,
            timestamp: new Date().toISOString()
        };
        
        // Simular creación de cuenta
        const submitBtn = petForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Creando cuenta...';
        submitBtn.disabled = true;
        
        setTimeout(() => {
            // Limpiar datos temporales
            localStorage.removeItem('tempUserData');
            
            // Mostrar éxito
            showNotification('¡Cuenta creada exitosamente! Bienvenido a Pawly 🐾');
            
            // Log de datos 
            console.log('Datos completos del registro:', completeData);
            
            // Redireccionar al login
            setTimeout(() => {
                window.location.href = 'Login.html';
            }, 2000);
            
        }, 2500);
    });
});