document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            });
        }
    });
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
            }
        });
    });
    
    const checkboxes = document.querySelectorAll('.checkbox-item');
    checkboxes.forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
            }
        });
    });
    
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        table.addEventListener('click', function(e) {
            const row = e.target.closest('tr');
            if (row && e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                const link = row.querySelector('a');
                if (link) {
                    link.click();
                }
            }
        });
    });
});