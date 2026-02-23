// Main JavaScript file for Quizify
document.addEventListener('DOMContentLoaded', function() {
    
    // Close alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Add form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#ef4444';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                console.warn('Please fill in all required fields');
            }
        });
    });
    
    // Add tooltips for join codes
    const joinCodes = document.querySelectorAll('[data-join-code]');
    joinCodes.forEach(element => {
        element.addEventListener('click', function() {
            const code = this.textContent.trim();
            if (navigator.clipboard) {
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                });
            }
        });
    });
    
    // Confirm before destructive actions
    const deleteButtons = document.querySelectorAll('button[type="submit"][onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('onclick').match(/'([^']*)'/)[1])) {
                e.preventDefault();
            }
        });
    });
    
});

// Disable submit button on form submission to prevent double submissions
function preventDoubleSubmit(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.style.opacity = '0.6';
        submitButton.style.cursor = 'not-allowed';
    }
    return true;
}

