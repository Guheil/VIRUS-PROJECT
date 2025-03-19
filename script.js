document.addEventListener('DOMContentLoaded', () => {
    // Header scrolling effect
    const header = document.querySelector('header');
    const scrollThreshold = 50;
    
    // Mobile menu toggle elements
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('nav ul li a');
    
    // Toggle mobile menu
    hamburger.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent the document click handler from firing
        nav.classList.toggle('active');
        const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.setAttribute('aria-expanded', !isExpanded);
        
        // Log to verify the event is firing
        console.log('Hamburger clicked, nav active:', nav.classList.contains('active'));
    });
    
    // Close mobile menu when clicking nav links
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
            console.log('Nav link clicked, closing menu');
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (nav.classList.contains('active') && 
            !nav.contains(e.target) && 
            !hamburger.contains(e.target)) {
            nav.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
            console.log('Clicked outside, closing menu');
        }
    });
    
    // Header scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > scrollThreshold) {
            header.style.background = 'linear-gradient(135deg, rgba(10, 10, 18, 0.95), rgba(20, 20, 30, 0.95))';
            header.style.boxShadow = '0 0 30px var(--glow-color, #ff0055)';
        } else {
            header.style.background = 'linear-gradient(135deg, rgba(10, 10, 18, 0.8), rgba(20, 20, 30, 0.8))';
            header.style.boxShadow = '0 0 20px var(--glow-color, #ff0055)';
        }
    });
    
    // Debug info
    console.log('Mobile menu script loaded');
    console.log('Hamburger element:', hamburger);
    console.log('Nav element:', nav);
});