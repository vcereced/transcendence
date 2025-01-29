// static/js/views/websocket.js

// Función para renderizar el HTML de la página WebSocket
export function renderWebsocket() {
    return `
        <div class="container">
        <h2>Prueba de WebSocket</h2>
        <div>
        <label for="roomName">Nombre de la sala:</label>
        <input type="text" id="roomName" placeholder="Escribe un nombre de sala" />
        </div>
        <button id="connectBtn" class="btn btn-primary mt-3">Conectar</button>
        
        <div id="userCount" class="mt-3">
        <!-- Aquí se mostrará el número de usuarios conectados -->
        <p>Cantidad de usuarios conectados: <span id="count">0</span></p>
        </div>
        
        <div id="messages" class="mt-3">
        <!-- Los mensajes del WebSocket se mostrarán aquí -->
        </div>
        </div>
        `;
    }
    
export function openWebSocket(roomName) {
    const messagesDiv = document.getElementById("messages");
    const roomNameInput = document.getElementById("roomName");
    
    let socket;
            // Establecer la conexión WebSocket si el token es válido
            socket = new WebSocket(`wss://localhost:8443/ws/room/${roomName}/`);

            // Event listener cuando la conexión se abra
            socket.onopen = () => {
                messagesDiv.innerHTML = `<p><strong>Conectado a la sala: ${roomName}</strong></p>`;
            };

            // Manejar los mensajes del servidor
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);

                // Si el mensaje contiene el número de usuarios conectados, actualizar el contador
                if (data.user_count !== undefined) {
                    userCountDiv.innerHTML = `Cantidad de usuarios conectados: <span id="count">${data.user_count}</span>`;
                } else {
                    messagesDiv.innerHTML += `<p>Mensaje recibido: ${data.message}</p>`;
                }
            };

            // Manejar errores
            socket.onerror = (error) => {
                messagesDiv.innerHTML += `<p style="color: red;">Error: ${error}</p>`;
            };

            // Manejar el cierre de la conexión
            socket.onclose = (error) => {
                messagesDiv.innerHTML += `<p style="color: red;">Error: ${error} - Conexión cerrada.</p>`;
            };
}

async function validarToken(token) {
    try {
        const response = await fetch('/auth-check', {
            method: 'GET', 
        });

        if (response.ok) {
            return "Ok"; 
        } else if (response.status === 400) {
            console.log("validar token: Token not available");
            return "Token not available"; 
        } else if (response.status === 401) {
            console.log("validar token: Token has expired");
            return "Token has expired"; 
        } else {
            console.log("validar token: Token not valid", response.status);
            return "Token not valid"; 
        }
    } catch (error) {
        console.error("validar token: Error fetch /auth-check", error);
        return false;
    }
}

// Función para inicializar la lógica del WebSocket
export async function initWebsocket() {

    const connectBtn = document.getElementById("connectBtn");
    const roomNameInput = document.getElementById("roomName");
    const messagesDiv = document.getElementById("messages");
    const userCountDiv = document.getElementById("count");
    let token = localStorage.getItem("accessToken");

    // Conectar al WebSocket cuando el usuario presiona el botón
    connectBtn.addEventListener("click", async () => {
        const roomName = roomNameInput.value.trim();
        if (!roomName) {
            alert("Por favor, ingresa un nombre de sala.");
            return;
        }

        if (!token) {
            alert("Por favor, inicia sesión.");
            return;
        }

        try {
            console.log("antes de validar");
            // Validar el token antes de conectar al WebSocket
            const result = await validarToken(token);

            if (result === "Ok") {
                console.log("first OK go to openwebsoket");
                openWebSocket(roomName); // Si el token es válido, abre el WebSocket
            } else if (result === "Token has expired") {
                console.log("token has expired got to renovar token");
                token = await renovarToken(); // Si el token expiró, intenta renovarlo
                console.log("token renovated go to validartoken");
                const renewedResult = await validarToken(token); // Validar el nuevo token

                if (renewedResult === "Ok") {
                    console.log("token validated go to openwebsoket");
                    openWebSocket(roomName);
                } else {
                    console.log("token NOT validated ");
                    console.error("No se valida el nuevo token");
                }
            } else {
                console.error("Token inválido u otro error:", result);
            }
        } catch (error) {
            console.error("Error en la validación del token:", error);
        }
    });
}

        
export async function renovarToken() {
    const refreshToken = localStorage.getItem("refreshToken");

    if (refreshToken) {
        const data = await getNewAccessToken(refreshToken); // Espera la respuesta de la promesa
        if (data && data.access_token) {
            guardarAccessToken(data.access_token); // Guarda el nuevo token
            return data.access_token; // Retorna el nuevo access token
        } else {
            console.error("renovarToken: No se pudo renovar el token.");
            return null;
        }
    } else {
        console.error("renovarToken: No hay refresh_token disponible");
        alert("No hay un refreshToken disponible. Redirigiendo al inicio de sesión.");
    }
}

export function guardarAccessToken(accessToken) {
    //localStorage.removeItem("accessToken");
    document.cookie = `accessToken=${accessToken}; path=/; secure; SameSite=Lax`;
    //localStorage.setItem("accessToken", accessToken);
}

export async function getNewAccessToken(refreshToken) {
    try {
        const response = await fetch('/auth-refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Token renovado exitosamente:", data);
            return data; // Devuelve los datos, que deben incluir el nuevo access_token
        } else {
            console.error(`Error al obtener nuevo access_token: ${response.status}`);
        }
        return null;
    } catch (error) {
        console.error("getNewAccessToken: error fetch /auth-refresh", error);
    }
}  
