document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    const scrollThreshold = 50;
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('nav ul li a');

    // Toggle mobile menu
    hamburger.addEventListener('click', () => {
        nav.classList.toggle('active');
        const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.setAttribute('aria-expanded', !isExpanded);
    });

    // Close mobile menu when clicking nav links
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!nav.contains(e.target) && !hamburger.contains(e.target) && nav.classList.contains('active')) {
            nav.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
        }
    });

    window.addEventListener('scroll', () => {
        if (window.scrollY > scrollThreshold) {
            header.style.background = 'linear-gradient(135deg, rgba(10, 10, 18, 0.95), rgba(20, 20, 30, 0.95))';
            header.style.boxShadow = '0 0 30px var(--glow-color)';
        } else {
            header.style.background = 'linear-gradient(135deg, rgba(10, 10, 18, 0.8), rgba(20, 20, 30, 0.8))';
            header.style.boxShadow = '0 0 20px var(--glow-color)';
        }
    });
});