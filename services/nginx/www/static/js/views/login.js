// static/js/views/login.js

export function renderLogin() {
	return `
	<div id="login-content" class="d-flex justify-content-center align-items-center vh-100">
    <div class="card p-4 shadow-sm" style="max-width: 400px; width: 100%;">
        <h2 class="card-title text-center mb-4">Iniciar Sesión</h2>
        <form id="login-form" method="POST">
            
            <div class="form-group">
                <label for="username">Usuario</label>
                <input type="text" id="login-username" name="username" class="form-control" required placeholder="Ingresa tu usuario">
            </div>

            <div class="form-group">
                <label for="password">Contraseña</label>
                <input type="password" id="login-password" name="password" class="form-control" required placeholder="Ingresa tu contraseña">
            </div>

			<div class="form-group">
                <label for="otp_token">otp</label>
                <input type="otp" id="login-otp" name="password" class="form-control" required placeholder="Ingresa tu otp">
            </div>

            <button type="submit" class="btn btn-primary btn-block">Iniciar Sesión</button>
        </form>

        <div id="login-response-message" class="mt-3 text-danger"></div>
    </div>
</div>

	`;
}

export function initLogin() {
	console.log("Login cargado");
	const loginForm = document.getElementById("login-form");
	const loginResponseMessage = document.getElementById("login-response-message");

	loginForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		const username = document.getElementById("login-username").value;
		const password = document.getElementById("login-password").value;
		const otp_token = document.getElementById("login-otp").value;

		const response = await fetch("/api/usr/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ username, password, otp_token }),
		});

		const data = await response.json();

		if (response.ok) {
			console.log("Inicio de sesión ok");
			localStorage.setItem("accessToken", data.access);
        	localStorage.setItem("refreshToken", data.refresh);
			// loginResponseMessage.innerText = data.message;
			loginResponseMessage.innerHTML = data.message;

			document.cookie = `accessToken=${data.access}; path=/; secure; SameSite=Lax`;
			document.cookie = `refreshToken=${data.refresh}; path=/; secure; SameSite=Lax`;

			handle_login_redirections();

		} else {
			console.log("Error al iniciar sesión");
			loginResponseMessage.innerHTML = data.error;
		}
	});

	function handle_login_redirections() {
		let afterLoginRedirect = window.sessionStorage.getItem("afterLoginRedirect");
		if (afterLoginRedirect) {
			window.sessionStorage.removeItem("afterLoginRedirect");
			window.location.hash = afterLoginRedirect;
		} else {
			window.location.hash = "#index";
		}
	}

}



