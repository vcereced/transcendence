// static/js/views/2FA.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function render2FA() {
    const response = await fetch('static/html/2FA.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export function init2FA() {

    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();
    let resendTimer;
    let resendInterval;
    const resendButton = document.getElementById("resend-button");
    const timerElement = document.getElementById("timer");
    const secondsElement = document.getElementById("seconds");

    // --- DOM ELEMENTS ---

    const title = document.querySelector('.site-title');

    // --- FUNCTIONS ---

    window.startResendTimer = function startResendTimer() {
        resendButton.disabled = true;
        resendTimer = 30;
        timerElement.textContent = resendTimer;
        timerElement.style.display = "inline";
        secondsElement.style.display = "inline";
        resendInterval = setInterval(() => {
            resendTimer--;
            timerElement.textContent = resendTimer;
            if (resendTimer <= 0) {
                clearInterval(resendInterval);
                resendButton.disabled = false;
                timerElement.style.display = "none";
                secondsElement.style.display = "none";
            }
        }, 1000);
    }
    
    window.resendCode = function resendCode() {
        alert("Código reenviado");
        clearInterval(resendInterval);
        startResendTimer();
    }
    
    window.handleInput = function handleInput(input, index) {
        const inputs = document.querySelectorAll(".code-input");
        input.style.background = input.value ? "#16a085" : "#222";
        if (input.value.length === 1 && index < 5) {
            inputs[index + 1].focus();
        }
    }

    window.moveToPrev = function moveToPrev(event, input, index) {
        const inputs = document.querySelectorAll(".code-input");
        if (event.key === "Backspace") {
            if (input.value === "" && index > 0) {
                inputs[index - 1].focus();
            }
            input.style.background = input.value ? "#16a085" : "#222";
        }
    }

    window.verifyCode = function verifyCode() {
        const code = Array.from(document.querySelectorAll(".code-input"))
                          .map(input => input.value)
                          .join("");
        if (code.length === 6) {
            alert("Código ingresado: " + code);
        } else {
            alert("Por favor, ingresa los 6 dígitos del código.");
        }
    }

        
    window.toggleFullscreen = function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    // --- EVENT LISTENERS ---

    eventManager.addEventListener(title, 'mouseenter', () => {
        title.classList.add('glitch');
        title.style.transform = 'translateY(-5px)';
    });

    eventManager.addEventListener(title, 'mouseleave', () => {
        title.classList.remove('glitch');
        title.style.transform = 'translateY(0)';
    });


    // --- INITIALIZATION ---
    
    window.startResendTimer();

    return () => eventManager.removeAllEventListeners();
        
}
