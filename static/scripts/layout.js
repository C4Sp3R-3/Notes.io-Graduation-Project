document.addEventListener('DOMContentLoaded', function () {
    // Toggle sidebar on mobile
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // Make page items clickable
    const pageItems = document.querySelectorAll('.notes-page-item');
    pageItems.forEach(item => {
        if (!item.querySelector('.bi-plus')) { // Skip the "Add a page" item
            item.addEventListener('click', function () {
                const title = this.getAttribute('data-title') || this.textContent.trim();

                // Update content
                document.querySelector('.notes-content-title').textContent = title;
                document.querySelector('.notes-breadcrumb').innerHTML =
                    `<i class="bi bi-house-door me-2"></i> Home / <span class="ms-2">${title}</span>`;

                // Update content text
                const contentArea = document.querySelector('.notes-content-title').nextElementSibling;
                if (contentArea) {
                    contentArea.textContent = `This is the ${title} page. Click anywhere to start editing.`;
                }

                // Close sidebar on mobile after selection
                if (window.innerWidth < 768) {
                    sidebar.classList.remove('active');
                    overlay.classList.remove('active');
                }
            });
        }
    });

    // Page search functionality
    const pageSearch = document.getElementById('page-search');
    const pagesContainer = document.getElementById('pages-container');
    const allPages = Array.from(pagesContainer.querySelectorAll('.notes-page-item'));

    pageSearch.addEventListener('input', function () {
        const searchTerm = this.value.toLowerCase().trim();

        allPages.forEach(page => {
            const pageTitle = page.getAttribute('data-title') || page.textContent.trim();
            const pageText = pageTitle.toLowerCase();

            if (searchTerm === '') {
                // Reset to original state
                page.style.display = '';
                page.innerHTML = `<i class="bi bi-file-earmark me-2 text-muted small"></i> ${pageTitle}`;
            } else if (pageText.includes(searchTerm)) {
                // Show and highlight matching text
                page.style.display = '';

                // Create highlighted version of the title
                const startIndex = pageText.indexOf(searchTerm);
                const endIndex = startIndex + searchTerm.length;

                const beforeMatch = pageTitle.substring(0, startIndex);
                const match = pageTitle.substring(startIndex, endIndex);
                const afterMatch = pageTitle.substring(endIndex);

                page.innerHTML = `<i class="bi bi-file-earmark me-2 text-muted small"></i> ${beforeMatch}<span class="notes-highlight">${match}</span>${afterMatch}`;
            } else {
                // Hide non-matching items
                page.style.display = 'none';
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
        const dropdownTrigger = document.getElementById('userMenuDropdown');
        const dropdownMenu = new bootstrap.Dropdown(dropdownTrigger);

        dropdownTrigger.addEventListener("click", function () {
            dropdownMenu.toggle();
        });
    });