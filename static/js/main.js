/**
 * Qetero Booking - Main JavaScript
 */

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = '#FF4D94';
        } else {
            field.style.borderColor = '';
        }
    });

    return isValid;
}

// Date input validation - prevent past dates
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(function(input) {
        if (!input.min) {
            input.min = today;
        }
    });
});

// Time validation
function validateTime(startTime, endTime) {
    if (startTime && endTime) {
        if (startTime >= endTime) {
            alert('Start time must be before end time.');
            return false;
        }
    }
    return true;
}

// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('form[action*="delete"] button[type="submit"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form && !form.hasAttribute('onsubmit')) {
                if (!confirm('Are you sure you want to delete this item?')) {
                    e.preventDefault();
                }
            }
        });
    });
});

// Auto-resize textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});

// Phone number formatting
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6, 10);
            }
            e.target.value = value;
        });
    });
});

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

