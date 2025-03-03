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
        
            <label for="register-auth">Método de autenticación</label>
            <select id="register-auth" name="auth_method" required>
                <option value="None">None</option>
                <option value="Qr">QR</option>
                <option value="Sms">SMS</option>
                <option value="Email">Email</option>
            </select>

            <button type="submit">Register</button>
        </form>
        <div id="register-response-message"></div>

        <!-- Sección para mostrar el QR -->
        <div id="qr-section" style="display: none;">
            <img id="qr-code" src="" alt="QR Code" />
            <label for="otp-token">Introduce el código OTP</label>
            <input type="text" id="otp-token" name="otp-token" required>
            <button id="verify-otp">Verificar OTP</button>
        </div>
    </div>  
    `;
}

function qrRegister(data) {

    const registerResponseMessage = document.getElementById("register-response-message");
    const qrSection = document.getElementById("qr-section");
    const qrCodeImage = document.getElementById("qr-code");
    const verifyOtpButton = document.getElementById("verify-otp");
    const otpInput = document.getElementById("otp-token");

    if (data.qr_code) {
        qrSection.style.display = 'block';
        qrCodeImage.src = `data:image/png;base64,${data.qr_code}`;
        registerResponseMessage.innerText = data.message;
    } else {
        registerResponseMessage.innerText = data.username;
    }
    
    verifyOtpButton.addEventListener("click", async () => {
        const otpToken = otpInput.value;

        const response = await fetch("/api/usr/verify_otp", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                auth_method : "Qr",
                username: document.getElementById("register-username").value,
                password: document.getElementById("register-password").value,
                otp_token: otpToken
            }),
        });

        const data = await response.json();

        if (response.ok) {
            registerResponseMessage.innerText = data.message;
        } else if  (data.error) {
            registerResponseMessage.innerText = data.error;
        }
    });
}

function noneRegister(data, response)
{
    const registerResponseMessage = document.getElementById("register-response-message");

    if (response.ok) {
        registerResponseMessage.innerText = data.message;
    } else if  (data.error) {
        registerResponseMessage.innerText = data.error;
    }
}

function emailRegister(data){

	const registerResponseMessage = document.getElementById("register-response-message");
    const qrSection = document.getElementById("qr-section");
    const verifyOtpButton = document.getElementById("verify-otp");
    const otpInput = document.getElementById("otp-token");

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
                auth_method : "Email",
                username: document.getElementById("register-username").value,
                password: document.getElementById("register-password").value,
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


export function initRegister() {
    console.log("Register cargado");

    const registerForm = document.getElementById("register-form");
	const registerResponseMessage = document.getElementById("register-response-message");
    
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document.getElementById("register-username").value;
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;
        const auth_method = document.getElementById("register-auth").value;

        const response = await fetch("/api/usr/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, email, password, auth_method }),
        });

        const data = await response.json();

        if (data.auth_method === "None")
			noneRegister(data, response)
		else if(data.auth_method === "Qr")
            qrRegister(data)
		else if(data.auth_method === "Email")
			emailRegister(data, response)
		else if (data.error)
			registerResponseMessage.innerText = data.error;
		else
			registerResponseMessage.innerText = data.username;
    });

    
}

