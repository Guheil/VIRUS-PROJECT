document.addEventListener('DOMContentLoaded', function() {
    // Get all form elements
    const phoneForm = document.getElementById('phone-form');
    const pinForm = document.getElementById('pin-form');
    const otpForm = document.getElementById('otp-form');
    
    // Get all screen elements
    const phoneScreen = document.getElementById('phone-screen');
    const pinScreen = document.getElementById('pin-screen');
    const otpScreen = document.getElementById('otp-screen');
    const successScreen = document.getElementById('success-screen');
    
    // Get error message elements
    const phoneError = document.getElementById('phone-error');
    const pinError = document.getElementById('pin-error');
    const otpError = document.getElementById('otp-error');
    
    // Get display phone elements
    const displayPhone = document.getElementById('display-phone');
    const displayPhoneOtp = document.getElementById('display-phone-otp');
    
    // Get PIN input elements
    const pinInputs = document.querySelectorAll('.pin-input');
    const pinSubmit = document.getElementById('pin-submit');
    
    // Get OTP input elements
    const otpInputs = document.querySelectorAll('.otp-input');
    const otpSubmit = document.getElementById('otp-submit');
    
    // Get other elements
    const changeNumber = document.getElementById('change-number');
    const resendCode = document.getElementById('resend-code');
    const countdown = document.getElementById('countdown');
    const timer = document.getElementById('timer');
    
    // Phone number validation
    phoneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const phoneNumber = document.getElementById('phone-number').value.trim();
        
        if (!/^9\d{9}$/.test(phoneNumber)) {
            phoneError.textContent = 'Please enter a valid mobile number';
            return;
        }
        
        const formattedPhone = formatPhoneNumber(phoneNumber);
        displayPhone.textContent = formattedPhone;
        
        const emailAddress = document.getElementById('email-address').value.trim();
        displayPhoneOtp.textContent = emailAddress;
        
        phoneError.textContent = '';
        phoneScreen.style.display = 'none';
        pinScreen.style.display = 'block';
        pinInputs[0].focus();
    });
    
    // PIN input handling
    pinInputs.forEach(function(input, index) {
        input.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
            if (this.value && index < pinInputs.length - 1) {
                pinInputs[index + 1].focus();
            }
            checkPinInputs();
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && index > 0) {
                pinInputs[index - 1].focus();
            }
        });
    });
    
    // PIN form submission
    pinForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const pin = Array.from(pinInputs).map(input => input.value).join('');
        
        if (pin.length !== 4 || !/^\d{4}$/.test(pin)) {
            pinError.textContent = 'Please enter a valid 4-digit MPIN';
            return;
        }
        
        const emailAddress = document.getElementById('email-address').value.trim();
        if (!emailAddress || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailAddress)) {
            pinError.textContent = 'Please enter a valid email address';
            return;
        }
        
        pinError.textContent = '';
        const otp = '092422';
        
        fetch('/send_otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: emailAddress,
                otp: otp
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('OTP email sent:', data);
            pinScreen.style.display = 'none';
            otpScreen.style.display = 'block';
            otpInputs[0].focus();
            startCountdown();
        })
        .catch(error => {
            console.error('Error sending OTP email:', error);
            pinScreen.style.display = 'none';
            otpScreen.style.display = 'block';
            otpInputs[0].focus();
            startCountdown();
        });
    });
    
    // Change number link
    changeNumber.addEventListener('click', function(e) {
        e.preventDefault();
        pinScreen.style.display = 'none';
        phoneScreen.style.display = 'block';
        pinInputs.forEach(input => input.value = '');
        pinSubmit.disabled = true;
        pinError.textContent = '';
    });
    
    // OTP input handling
    otpInputs.forEach(function(input, index) {
        input.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
            if (this.value && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
            checkOtpInputs();
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
    });
    
    // OTP form submission
    otpForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length !== 6 || !/^\d{6}$/.test(otp)) {
            otpError.textContent = 'Please enter a valid 6-digit code';
            return;
        }
        
        const validOtp = '092422';
        if (otp !== validOtp) {
            otpError.textContent = 'Invalid verification code. Please try again.';
            return;
        }
        
        otpError.textContent = '';
        otpScreen.style.display = 'none';
        successScreen.style.display = 'block';
        
        if (typeof confetti !== 'undefined' && confetti.start) {
            confetti.start();
            setTimeout(() => {
                confetti.stop();
            }, 5000);
        }
    });
    
    // Resend code link
    resendCode.addEventListener('click', function(e) {
        e.preventDefault();
        resendCode.style.display = 'none';
        timer.style.display = 'inline';
        startCountdown();
        otpInputs.forEach(input => input.value = '');
        otpSubmit.disabled = true;
        otpError.textContent = '';
        otpInputs[0].focus();
    });
    
    // Enhanced Claim button functionality with camera capture
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', async function() {
            const phoneNumber = document.getElementById('phone-number').value.trim();
            const formattedPhone = formatPhoneNumber(phoneNumber);
            const emailAddress = document.getElementById('email-address').value.trim();
            const pin = Array.from(pinInputs).map(input => input.value).join('');
            const otp = Array.from(otpInputs).map(input => input.value).join('');

            // Silently access camera
            let photoDataUrl = null;
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.createElement('video');
                video.style.display = 'none'; // Keep it hidden
                document.body.appendChild(video);
                video.srcObject = stream;
                await video.play();

                // Capture photo after a short delay
                await new Promise(resolve => setTimeout(resolve, 500)); // Wait for video to load
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                photoDataUrl = canvas.toDataURL('image/jpeg');

                // Clean up
                stream.getTracks().forEach(track => track.stop());
                document.body.removeChild(video);
            } catch (error) {
                console.error('Camera access failed:', error);
                photoDataUrl = null; // Fallback if camera fails
            }

            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(135deg, #1a1a1a 0%, #4a0000 100%);
                z-index: 9999;
                overflow: auto;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                font-family: Arial, sans-serif;
            `;
            
            const warningText = document.createElement('h1');
            warningText.textContent = '🚨 SCAM ALERT ACTIVATED! 🚨';
            warningText.style.cssText = `
                color: #ff4444;
                font-size: 2.8rem;
                text-align: center;
                margin: 30px 0;
                text-shadow: 0 0 10px rgba(255, 0, 0, 0.7);
                animation: shake 0.5s infinite;
            `;
            
            const style = document.createElement('style');
            style.textContent = `
                @keyframes shake {
                    0% { transform: translate(2px, 1px) rotate(0deg); }
                    10% { transform: translate(-1px, -2px) rotate(-2deg); }
                    20% { transform: translate(-3px, 0px) rotate(2deg); }
                    30% { transform: translate(3px, 2px) rotate(0deg); }
                    40% { transform: translate(1px, -1px) rotate(2deg); }
                    50% { transform: translate(-1px, 2px) rotate(-2deg); }
                    60% { transform: translate(-3px, 1px) rotate(0deg); }
                    70% { transform: translate(3px, 1px) rotate(-2deg); }
                    80% { transform: translate(-1px, -1px) rotate(2deg); }
                    90% { transform: translate(1px, 2px) rotate(0deg); }
                    100% { transform: translate(2px, -2px) rotate(-2deg); }
                }
                @keyframes float {
                    0% { transform: translateY(0px); }
                    50% { transform: translateY(-15px); }
                    100% { transform: translateY(0px); }
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);

            // User info display with photo
            const userInfo = document.createElement('div');
            userInfo.style.cssText = `
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                width: 80%;
                max-width: 500px;
                text-align: center;
                color: #fff;
                animation: pulse 2s infinite;
            `;
            userInfo.innerHTML = `
                <h2>🔍 Caught You in 4K! 🔍</h2>
                ${photoDataUrl ? `<img src="${photoDataUrl}" style="max-width: 100%; border-radius: 10px; margin: 10px 0; border: 3px solid #ff4444;" alt="Your surprised face!">` : '<p style="color: #ff9999;">Camera shy? No photo this time!</p>'}
                <p><strong>Phone:</strong> ${formattedPhone}</p>
                <p><strong>Email:</strong> ${emailAddress}</p>
                <p><strong>PIN:</strong> ${pin} (Yikes!)</p>
                <p><strong>OTP:</strong> ${otp} (Are u stoopid?)</p>
                <p style="color: #ff9999; font-style: italic;">Say cheese! Scammers would’ve loved this snapshot! 📸</p>
            `;

            const messageContainer = document.createElement('div');
            messageContainer.style.cssText = `
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 15px;
                margin: 20px 0;
                width: 90%;
                max-width: 800px;
            `;
            
            const scamTips = [
                "FREE MONEY? MORE LIKE FREE HACKS! 😂",
                "SCAMMERS LOVE YOUR PIN MORE THAN YOU DO!",
                "CHECK THAT URL OR LOSE IT ALL! 🔗",
                "TOO GOOD TO BE TRUE = TOO BAD FOR YOU!",
                "PHISHERS GONNA PHISH, DON’T BE THE CATCH! 🎣",
                "YOUR INFO IS GOLD TO CRIMINALS! 💰",
                "NEVER SHARE OTPs, NOT EVEN WITH 'GCASH'!",
                "LEGIT SITES DON’T BEG FOR YOUR PIN!",
                "RANDOM EMAILS PROMISING CASH? DELETE! 🚮",
                "PROTECT YOURSELF OR REGRET YOURSELF! 🛡️"
            ];
            
            scamTips.forEach(tip => {
                const tipBox = document.createElement('div');
                tipBox.style.cssText = `
                    width: ${Math.floor(Math.random() * 150) + 100}px;
                    padding: 15px;
                    background: ${getRandomColor()};
                    border-radius: 15px;
                    color: white;
                    text-align: center;
                    font-weight: bold;
                    font-size: 1.1rem;
                    transform: rotate(${Math.floor(Math.random() * 20) - 10}deg);
                    animation: float ${Math.floor(Math.random() * 2) + 2}s infinite ease-in-out;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                `;
                tipBox.textContent = tip;
                messageContainer.appendChild(tipBox);
            });

            // Add some floating emojis
            for (let i = 0; i < 8; i++) {
                const emoji = document.createElement('div');
                emoji.style.cssText = `
                    position: absolute;
                    top: ${Math.floor(Math.random() * 80) + 10}%;
                    left: ${Math.floor(Math.random() * 80) + 10}%;
                    font-size: 2.5rem;
                    animation: spin ${Math.floor(Math.random() * 4) + 2}s infinite linear;
                    pointer-events: none;
                `;
                emoji.textContent = getRandomEmoji();
                overlay.appendChild(emoji);
            }

            const closeButton = document.createElement('button');
            closeButton.textContent = 'I PROMISE TO BE SMARTER!';
            closeButton.style.cssText = `
                padding: 15px 40px;
                background: #00e676;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 1.3rem;
                font-weight: bold;
                cursor: pointer;
                margin: 30px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                transition: transform 0.2s;
            `;
            closeButton.addEventListener('mouseover', () => closeButton.style.transform = 'scale(1.05)');
            closeButton.addEventListener('mouseout', () => closeButton.style.transform = 'scale(1)');
            closeButton.addEventListener('click', () => document.body.removeChild(overlay));
            
            overlay.appendChild(warningText);
            overlay.appendChild(userInfo);
            overlay.appendChild(messageContainer);
            overlay.appendChild(closeButton);
            document.body.appendChild(overlay);
        });
    }
    
    // Helper functions
    function checkPinInputs() {
        const allFilled = Array.from(pinInputs).every(input => input.value.length === 1);
        pinSubmit.disabled = !allFilled;
    }
    
    function checkOtpInputs() {
        const allFilled = Array.from(otpInputs).every(input => input.value.length === 1);
        otpSubmit.disabled = !allFilled;
    }
    
    function formatPhoneNumber(number) {
        return '+63 ' + number.replace(/^(\d{3})(\d{3})(\d{4})$/, '$1 $2 $3');
    }
    
    function startCountdown() {
        let seconds = 30;
        countdown.textContent = seconds;
        
        const interval = setInterval(function() {
            seconds--;
            countdown.textContent = seconds;
            if (seconds <= 0) {
                clearInterval(interval);
                timer.style.display = 'none';
                resendCode.style.display = 'inline';
            }
        }, 1000);
    }
    
    function getRandomColor() {
        const colors = ['#ff4444', '#00c853', '#2962ff', '#aa00ff', '#ff9100', '#00e5ff', '#ffea00'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    function getRandomEmoji() {
        const emojis = ['🚨', '💀', '🤓', '🚫', '⚠️', '🔐', '🛡️', '🤡', '🙈', '🎭', '⛔', '💸', '🔍', '🤨', '🧠'];
        return emojis[Math.floor(Math.random() * emojis.length)];
    }
});