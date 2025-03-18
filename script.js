<script>
document.addEventListener('DOMContentLoaded', () => {
    const track = document.querySelector('.factions-track');
    const cards = document.querySelectorAll('.faction-card');
    const prevButton = document.querySelector('.carousel-button.prev');
    const nextButton = document.querySelector('.carousel-button.next');
    const dotsContainer = document.querySelector('.carousel-dots');
    let currentIndex = 0;
    const cardWidth = cards[0].offsetWidth + 32; // Including gap

    // Create dots
    cards.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.classList.add('carousel-dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });

    const dots = document.querySelectorAll('.carousel-dot');

    function updateCarousel() {
        track.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }

    function goToSlide(index) {
        currentIndex = index;
        if (currentIndex >= cards.length) currentIndex = 0;
        if (currentIndex < 0) currentIndex = cards.length - 1;
        updateCarousel();
    }

    prevButton.addEventListener('click', () => goToSlide(currentIndex - 1));
    nextButton.addEventListener('click', () => goToSlide(currentIndex + 1));

    // Optional: Auto-scroll
    let autoScroll = setInterval(() => goToSlide(currentIndex + 1), 5000);

    // Pause auto-scroll on hover
    document.querySelector('.factions-carousel').addEventListener('mouseenter', () => clearInterval(autoScroll));
    document.querySelector('.factions-carousel').addEventListener('mouseleave', () => {
        autoScroll = setInterval(() => goToSlide(currentIndex + 1), 5000);
    });

    // Update carousel on window resize
    window.addEventListener('resize', () => {
        const newCardWidth = cards[0].offsetWidth + 32;
        track.style.transform = `translateX(-${currentIndex * newCardWidth}px)`;
    });
});
</script>