// static/js/views/new_login.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderNewLogin() {
    const response = await fetch('static/html/new_login.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export function initNewLogin() {

    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();


    // --- DOM ELEMENTS ---

    const title = document.querySelector('.site-title');

    // --- FUNCTIONS ---

    window.toggleForm = function toggleForm() {

        let loginContainer = document.getElementById('login-container');
        let registerContainer = document.getElementById('register-container');

        if (loginContainer.style.display === 'none') {
            loginContainer.style.display = 'block';
            registerContainer.style.display = 'none';
        } else {
            loginContainer.style.display = 'none';
            registerContainer.style.display = 'block';
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

    return () => eventManager.removeAllEventListeners();
}
