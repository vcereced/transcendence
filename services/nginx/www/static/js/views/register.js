export function renderRegister() {
    return `
    <div id="contenido">
        <h2>Register</h2>
        <form id="register-form" method="POST">
            <label for="register-username">User</label>
            <input type="text" id="register-username" name="username" autocomplete="username" required>
        
            <label for="register-email">email</label>
            <input type="email" id="register-email" name="email" autocomplete="email" required>
        
            <label for="register-password">Password</label>
            <input type="password" id="register-password" name="password" autocomplete="new-password" required>
        
            <button type="submit">Register</button>
        </form>
        <div id="register-response-message"></div>

        <!-- Sección para mostrar el QR -->
        <div id="qr-section" style="display: none;">
            <h3>Escanea el QR con tu aplicación de autenticación</h3>
            <img id="qr-code" src="" alt="QR Code" />
            <label for="otp-token">Introduce el código OTP</label>
            <input type="text" id="otp-token" name="otp-token" required>
            <button id="verify-otp">Verificar OTP</button>
        </div>
    </div>  
    `;
}

export function initRegister() {
    console.log("Register cargado");
    const registerForm = document.getElementById("register-form");
    const registerResponseMessage = document.getElementById("register-response-message");
    const qrSection = document.getElementById("qr-section");
    const qrCodeImage = document.getElementById("qr-code");
    const verifyOtpButton = document.getElementById("verify-otp");
    const otpInput = document.getElementById("otp-token");

    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document.getElementById("register-username").value;
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;

        const response = await fetch("/api/usr/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();

        if (data.qr_code) {
            // Mostrar la sección para ingresar el OTP
            qrSection.style.display = 'block';
            qrCodeImage.src = `data:image/png;base64,${data.qr_code}`;
            registerResponseMessage.innerText = data.message;
        } else {
            registerResponseMessage.innerText = data.username;
        }
    });

    verifyOtpButton.addEventListener("click", async () => {
        const otpToken = otpInput.value;

        const response = await fetch("/api/usr/verify_otp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: document.getElementById("register-username").value,
                otp_token: otpToken
            }),
        });

        console.log("esperando a la respuesta del otp");
        const data = await response.json();
        console.log("despues de la respuesta del otp");
        if (response.ok) {
            registerResponseMessage.innerText = data.message;
            window.location.href = "/login";
        } else {
            console.log("entra en el error");
            registerResponseMessage.innerText = data.error;
        }
    });
}