document.addEventListener('DOMContentLoaded', function() {
    const backToTopButton = document.getElementById('back-to-top');
    
    // If the button doesn't exist, exit the function
    if (!backToTopButton) return;
    
    const scrollThreshold = 300;
    let isVisible = false;
    let lastScrollPosition = 0;
    
    // Function to handle scroll checks with performance optimization
    function checkScroll() {
        const currentScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        const scrollDirection = currentScrollPosition > lastScrollPosition ? 'down' : 'up';
        lastScrollPosition = currentScrollPosition;
        
        // Only update visibility if crossing the threshold or changing direction near threshold
        const shouldBeVisible = currentScrollPosition > scrollThreshold;
        
        if (shouldBeVisible !== isVisible) {
            isVisible = shouldBeVisible;
            backToTopButton.classList.toggle('show', isVisible);
            
            // Additional animation control
            if (isVisible) {
                backToTopButton.style.opacity = '0';
                backToTopButton.style.display = 'block';
                setTimeout(() => {
                    backToTopButton.style.opacity = '1';
                }, 10);
            } else {
                backToTopButton.style.opacity = '0';
                setTimeout(() => {
                    if (!isVisible) {
                        backToTopButton.style.display = 'none';
                    }
                }, 300); // Match this with your CSS transition duration
            }
        }
    }
    
    // Initial check
    checkScroll();
    
    // Scroll event with debouncing for performance
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(checkScroll, 50);
    });
    
    // Smooth scroll to top with additional animation
    backToTopButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Add active class for click effect
        this.classList.add('active');
        setTimeout(() => {
            this.classList.remove('active');
        }, 300);
        
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Keyboard accessibility
    backToTopButton.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this.click();
        }
    });
});