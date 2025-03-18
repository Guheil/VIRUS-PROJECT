document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    const scrollThreshold = 50;

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