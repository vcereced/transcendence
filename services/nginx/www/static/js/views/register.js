//static/js/views/register.js

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
    </div>  
    `;
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

        const response = await fetch("/api/usr/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, email, password }),
        });

        const data = await response.json();

        if (data.success) {
            registerResponseMessage.innerText = "Registro exitoso";
            window.location.href = "/login";
        } else {
            registerResponseMessage.innerText = data.message;
        }
    });
}