// static/js/views/new_login.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderNewLogin() {
    const response = await fetch('static/html/new_login.html');
    const htmlContent = await response.text();
    return htmlContent;
}

function emailRegister(data){

	const registerResponseMessage = document.getElementById("register-response-message");
    const registerDataSection = document.getElementById("register-data-container");
    const qrSection = document.getElementById("qr-section");
    const verifyOtpButton = document.getElementById("reg-verify-otp");
    const otpInput = document.getElementById("otp-token");

    registerDataSection.style.display = 'none';
	qrSection.style.display = 'block';
    registerResponseMessage.innerText = data.message;

	verifyOtpButton.addEventListener("click", async () => {
        const otpToken = otpInput.value;

        const response = await fetch("/api/usr/verify_email_otp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                //auth_method : "Email",
                //username: document.getElementById("reg-name").value,
                //password: document.getElementById("reg-password").value,
                email: document.getElementById("reg-email").value,
                otp_token: otpToken
            }),
        });

        const data = await response.json();

        if (response.ok) {
            registerResponseMessage.innerText = data.message;
        } else if (data.error) {
            registerResponseMessage.innerText = data.error;
        }
    });
}


function loginOtp(data) {
	const loginResponseMessage = document.getElementById("login-response-message");
    const qrSection2 = document.getElementById("login-otp-section");
	const loginForm = document.getElementById("login-form");
    const verifyOtpButton = document.getElementById("verify-otp");
	const otpInput = document.getElementById("login-otp-token");
    const loginDataSection = document.getElementById("login-data-container");
    
    loginDataSection.style.display = 'none';
    qrSection2.style.display = 'block';
    loginResponseMessage.innerText = data.message;
    
    verifyOtpButton.addEventListener("click", async (event) => {
        const otpToken = otpInput.value;

        const response = await fetch("/api/usr/login_email", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: document.getElementById("login-email").value,
                password: document.getElementById("login-password").value,
                otp_token: otpToken
            }),
        });

        const data = await response.json();

        if (response.ok) {
            console.log("Inicio de sesión ok");

            loginResponseMessage.innerHTML = data.message;

            document.cookie = `accessToken=${data.access}; path=/; secure; SameSite=Lax`;
            document.cookie = `refreshToken=${data.refresh}; path=/; secure; SameSite=Lax`;

        } else {
            console.log("Error al iniciar sesión");
            loginResponseMessage.innerHTML = data.error;
        }
    });
	
}

export function initNewLogin() {

    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();


    // --- DOM ELEMENTS ---

    const title = document.querySelector('.site-title');
    const registerButton = document.getElementById('register-btn');
    const loginButton = document.getElementById('login-btn');
    const registerResponseMessage = document.getElementById("register-response-message");
    const loginResponseMessage = document.getElementById("login-response-message");
    const registerDataSection = document.getElementById("register-data-container");
    const verifyOtpRegisterButton = document.getElementById("reg-verify-otp");

    const qrSection = document.getElementById("qr-section");
    // --- FUNCTIONS ---

    window.toggleForm = function toggleForm() {

        let loginContainer = document.getElementById('login-container');
        let registerContainer = document.getElementById('register-container');

        if (loginContainer.style.display === 'none') {
            loginContainer.style.display = 'block';
            registerContainer.style.display = 'none';
            qrSection.style.display = 'none';
        } else {
            loginContainer.style.display = 'none';
            registerContainer.style.display = 'block';
            registerDataSection.style.display = 'block';//data contaniner register
            qrSection.style.display = 'none';
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
    
    async function registerUser() {
        const username = document.getElementById("reg-name").value;
        const email = document.getElementById("reg-email").value;
        const password = document.getElementById("reg-password").value;

        if (!username || !email || !password) {
            console.log(username, email, password)
            alert("Todos los campos son obligatorios siuu.");
            return;
        }

        try {

            const response = await fetch("/api/usr/register", { // Ajusta la URL
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                auth_method : "Email",
                username: username,
                password: password,
                email: email
                })
            });
            const data = await response.json();

        if(response.ok)
                emailRegister(data)
        else
            if (data.email)
                registerResponseMessage.innerText = data.email; // Mostrar el primer mensaje de error
            else if (data.username)
                registerResponseMessage.innerText = data.username; // Mostrar el primer mensaje de error
            else if (data.error)
                registerResponseMessage.innerText = data.error; // Mostrar el primer mensaje de error
            else
                registerResponseMessage.innerText = "Hay un mensaje de error no definido en el front para inyectarlo.";
        } catch (error) {
            console.error("Error en la solicitud:", error);
            alert("Hubo un problema con el registro.");
        }
        
    }

    async function loginUser() {
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        const loginResponseMessage = document.getElementById("login-response-message");
        

        if (!email || !password) {
            alert("Todos los campos son obligatorios.");
            return;
        }

        try {

            const response = await fetch("/api/usr/login", { // Ajusta la URL
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                email: email,
                password: password,
                })
            });

            const data = await response.json();

            if (response.ok) {
                console.log("da ok la respuesta")
                loginResponseMessage.innerHTML = data.message;
                loginOtp(data, response)
            } else if (data.error)
                loginResponseMessage.innerText = data.error;
            else
                loginResponseMessage.innerText = data.username;
        } catch (error) {
            console.error("Error en la solicitud:", error);
            alert("Hubo un problema con el registro.");
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
    
    if (registerButton) {
        eventManager.addEventListener(registerButton, "click", registerUser);
    }

    // if(verifyOtpRegisterButton) {
    //     eventManager.addEventListener(verifyOtpRegisterButton, "click", emailRegister);
    // }

    if(loginButton) {
        eventManager.addEventListener(loginButton, "click", loginUser);
    }


    // --- INITIALIZATION ---

    return () => eventManager.removeAllEventListeners();
}
