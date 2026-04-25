// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

// Check saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Mobile Menu Toggle
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
}

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s ease';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});

// Confirm before deleting or cancelling orders
function confirmAction(message) {
    return confirm(message || 'Are you sure?');
}

// Star Rating Interaction
document.addEventListener('DOMContentLoaded', () => {
    const stars = document.querySelectorAll('.star-rating .star');
    const ratingInput = document.getElementById('ratingInput');
    
    if (stars.length > 0 && ratingInput) {
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const rating = parseInt(star.dataset.rating);
                ratingInput.value = rating;
                
                // Update visual stars
                stars.forEach((s, index) => {
                    if (index < rating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
            
            star.addEventListener('mouseenter', () => {
                const rating = parseInt(star.dataset.rating);
                stars.forEach((s, index) => {
                    if (index < rating) {
                        s.style.color = '#f59e0b';
                    }
                });
            });
            
            star.addEventListener('mouseleave', () => {
                const currentRating = parseInt(ratingInput.value);
                stars.forEach((s, index) => {
                    if (index >= currentRating) {
                        s.style.color = '#d1d5db';
                    }
                });
            });
        });
    }
});
// ==========================================
// PASSWORD TOGGLE FUNCTION
// ==========================================
function togglePassword(inputId, button) {
    const passwordInput = document.getElementById(inputId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        button.innerHTML = '🙈';
        button.classList.add('show');
        button.title = 'Hide password';
    } else {
        passwordInput.type = 'password';
        button.innerHTML = '👁️';
        button.classList.remove('show');
        button.title = 'Show password';
    }
}