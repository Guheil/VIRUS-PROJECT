// Confetti animation for success screen
const confetti = {
    maxCount: 150,    // Max confetti count
    speed: 3,         // Speed factor
    frameInterval: 15, // Frame interval for animation
    alpha: 1.0,       // Alpha transparency
    gradient: false,  // Use gradients
    start: null,      // Start function (defined below)
    stop: null,       // Stop function (defined below)
    toggle: null,     // Toggle function (defined below)
    pause: null,      // Pause function (defined below)
    resume: null,     // Resume function (defined below)
    togglePause: null,// Toggle pause function (defined below)
    remove: null,     // Remove confetti function (defined below)
    isPaused: null,   // Status function (defined below)
    isRunning: null   // Status function (defined below)
};

(function() {
    confetti.start = startConfetti;
    confetti.stop = stopConfetti;
    confetti.toggle = toggleConfetti;
    confetti.pause = pauseConfetti;
    confetti.resume = resumeConfetti;
    confetti.togglePause = toggleConfettiPause;
    confetti.isPaused = isConfettiPaused;
    confetti.remove = removeConfetti;
    confetti.isRunning = isConfettiRunning;
    const supportsAnimationFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame;
    const colors = ["rgba(30,144,255,", "rgba(107,142,35,", "rgba(255,215,0,", "rgba(255,192,203,", "rgba(106,90,205,", "rgba(173,216,230,", "rgba(238,130,238,", "rgba(152,251,152,", "rgba(70,130,180,", "rgba(244,164,96,", "rgba(210,105,30,", "rgba(220,20,60,"];
    let streamingConfetti = false;
    let pause = false;
    let lastFrameTime = Date.now();
    let particles = [];
    let waveAngle = 0;
    let context = null;
    
    function resetParticle(particle, width, height) {
        particle.color = colors[(Math.random() * colors.length) | 0] + (confetti.alpha + ")");
        particle.color2 = colors[(Math.random() * colors.length) | 0] + (confetti.alpha + ")");
        particle.x = Math.random() * width;
        particle.y = Math.random() * height - height;
        particle.diameter = Math.random() * 10 + 5;
        particle.tilt = Math.random() * 10 - 10;
        particle.tiltAngleIncrement = Math.random() * 0.07 + 0.05;
        particle.tiltAngle = Math.random() * Math.PI;
        return particle;
    }

    function toggleConfettiPause() {
        if (pause)
            resumeConfetti();
        else
            pauseConfetti();
    }

    function isConfettiPaused() {
        return pause;
    }

    function pauseConfetti() {
        pause = true;
    }

    function resumeConfetti() {
        pause = false;
        runAnimation();
    }

    function runAnimation() {
        if (pause)
            return;
        else if (particles.length === 0) {
            context.clearRect(0, 0, window.innerWidth, window.innerHeight);
            animationTimer = null;
        } else {
            const now = Date.now();
            const delta = now - lastFrameTime;
            if (!supportsAnimationFrame || delta > confetti.frameInterval) {
                context.clearRect(0, 0, window.innerWidth, window.innerHeight);
                updateParticles();
                drawParticles(context);
                lastFrameTime = now - (delta % confetti.frameInterval);
            }
            animationTimer = requestAnimationFrame(runAnimation);
        }
    }

    function startConfetti(timeout, min, max) {
        const width = window.innerWidth;
        const height = window.innerHeight;
        window.requestAnimationFrame = (function() {
            return window.requestAnimationFrame ||
                window.webkitRequestAnimationFrame ||
                window.mozRequestAnimationFrame ||
                window.oRequestAnimationFrame ||
                window.msRequestAnimationFrame ||
                function (callback) {
                    return window.setTimeout(callback, confetti.frameInterval);
                };
        })();
        let canvas = document.getElementById("confetti-canvas");
        if (canvas === null) {
            canvas = document.createElement("canvas");
            canvas.setAttribute("id", "confetti-canvas");
            canvas.setAttribute("style", "display:block;z-index:999999;pointer-events:none;position:fixed;top:0");
            document.body.prepend(canvas);
            canvas.width = width;
            canvas.height = height;
            window.addEventListener("resize", function() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }, true);
            context = canvas.getContext("2d");
        } else if (context === null)
            context = canvas.getContext("2d");
        let count = confetti.maxCount;
        if (min) {
            if (max) {
                if (min == max)
                    count = particles.length + max;
                else {
                    if (min > max) {
                        const temp = min;
                        min = max;
                        max = temp;
                    }
                    count = particles.length + ((Math.random() * (max - min) + min) | 0);
                }
            } else
                count = particles.length + min;
        } else if (max)
            count = particles.length + max;
        while (particles.length < count)
            particles.push(resetParticle({}, width, height));
        streamingConfetti = true;
        pause = false;
        runAnimation();
        if (timeout) {
            window.setTimeout(stopConfetti, timeout);
        }
    }

    function stopConfetti() {
        streamingConfetti = false;
    }

    function removeConfetti() {
        stop();
        pause = false;
        particles = [];
    }

    function toggleConfetti() {
        if (streamingConfetti)
            stopConfetti();
        else
            startConfetti();
    }
    
    function isConfettiRunning() {
        return streamingConfetti;
    }

    function drawParticles(context) {
        let particle;
        let x, y, x2, y2;
        for (let i = 0; i < particles.length; i++) {
            particle = particles[i];
            context.beginPath();
            context.lineWidth = particle.diameter;
            x2 = particle.x + particle.tilt;
            x = x2 + particle.diameter / 2;
            y2 = particle.y + particle.tilt + particle.diameter / 2;
            if (confetti.gradient) {
                const gradient = context.createLinearGradient(x, particle.y, x2, y2);
                gradient.addColorStop("0", particle.color);
                gradient.addColorStop("1.0", particle.color2);
                context.strokeStyle = gradient;
            } else
                context.strokeStyle = particle.color;
            context.moveTo(x, particle.y);
            context.lineTo(x2, y2);
            context.stroke();
        }
    }

    function updateParticles() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        let particle;
        waveAngle += 0.01;
        for (let i = 0; i < particles.length; i++) {
            particle = particles[i];
            if (!streamingConfetti && particle.y < -15)
                particle.y = height + 100;
            else {
                particle.tiltAngle += particle.tiltAngleIncrement;
                particle.x += Math.sin(waveAngle) - 0.5;
                particle.y += (Math.cos(waveAngle) + particle.diameter + confetti.speed) * 0.5;
                particle.tilt = Math.sin(particle.tiltAngle) * 15;
            }
            if (particle.x > width + 20 || particle.x < -20 || particle.y > height) {
                if (streamingConfetti && particles.length <= confetti.maxCount)
                    resetParticle(particle, width, height);
                else {
                    particles.splice(i, 1);
                    i--;
                }
            }
        }
    }
})();

// Start confetti when success screen is shown
document.addEventListener('DOMContentLoaded', function() {
    const successScreen = document.getElementById('success-screen');
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'style' && 
                successScreen.style.display === 'block') {
                confetti.start();
                setTimeout(function() {
                    confetti.stop();
                }, 5000); // Run for 5 seconds
            }
        });
    });
    
    observer.observe(successScreen, { attributes: true });
});