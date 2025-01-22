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

// Función para inicializar la lógica del WebSocket
export function initWebsocket() {
    
    const connectBtn = document.getElementById("connectBtn");
    const roomNameInput = document.getElementById("roomName");
    const messagesDiv = document.getElementById("messages");
    const userCountDiv = document.getElementById("count");
    const token = localStorage.getItem("accessToken");

    // Conectar al WebSocket cuando el usuario presiona el botón
    connectBtn.addEventListener("click", () => {
        const roomName = roomNameInput.value.trim();
        if (!roomName) {
            alert("Por favor, ingresa un nombre de sala.");
            return;
        }

        if (!token) {
            alert("Por favor, inicia sesión.");
            return;
        }

        //Validar el token antes de conectar al WebSocket
        validarToken(token)
        .then((result) => {
            if (result === 200) {
                abrirWebSocket(roomName); // Si el token es válido, abre el WebSocket
            } else if (result === 401) {
                renovarToken(); // Si el token expiró, intenta renovarlo
                abrirWebSocket(roomName);
            } else {
                console.error("Token inválido u otro error:", result);
            }
        })
        .catch((error) => {
            console.error("Error en la validación del token:", error);
        });


        // // Validar el token antes de conectar al WebSocket
        // validarToken(token)
        //     .then((isValid) => {
        //         if (isValid) {
        //             // Establecer la conexión WebSocket si el token es válido
        //             socket = new WebSocket(`wss://localhost:8443/ws/room/${roomName}/`);

        //             // Event listener cuando la conexión se abra
        //             socket.onopen = () => {
        //                 messagesDiv.innerHTML = `<p><strong>Conectado a la sala: ${roomName}</strong></p>`;
        //             };

        //             // Manejar los mensajes del servidor
        //             socket.onmessage = (event) => {
        //                 const data = JSON.parse(event.data);

        //                 // Si el mensaje contiene el número de usuarios conectados, actualizar el contador
        //                 if (data.user_count !== undefined) {
        //                     userCountDiv.innerHTML = `Cantidad de usuarios conectados: <span id="count">${data.user_count}</span>`;
        //                 } else {
        //                     messagesDiv.innerHTML += `<p>Mensaje recibido: ${data.message}</p>`;
        //                 }
        //             };

        //             // Manejar errores
        //             socket.onerror = (error) => {
        //                 messagesDiv.innerHTML += `<p style="color: red;">Error: ${error}</p>`;
        //             };

        //             // Manejar el cierre de la conexión
        //             socket.onclose = (error) => {
        //                 messagesDiv.innerHTML += `<p style="color: red;">Error: ${error} - Conexión cerrada.</p>`;
        //             };
        //         } else {
        //             messagesDiv.innerHTML += "<p style='color: red;'>El token no es válido. Por favor, inicia sesión nuevamente.</p>";
        //         }
        //     })
            // .catch((error) => {
            //     console.error("Error al validar el token:", error);
            //     alert("Hubo un error al validar el token.");
            // });
    });
}

async function validarToken(token) {
    try {
        const response = await fetch('/auth-check', {
            method: 'GET', 
            headers: {
                'Authorization': `Bearer ${token}`, 
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            return 200; 
        } else if (response.status === 400) {
            console.error("Token not available");
            return 400; 
        } else if (response.status === 401) {
            console.error("Token has expired");
            return 401; 
        } else {
            console.error("Token not valid", response.status);
            return 401; 
        }
    } catch (error) {
        console.error("Error al validar el token:", error);
        return false;
    }
}

export function abrirWebSocket(roomName) {
    const messagesDiv = document.getElementById("messages");
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
            
export function renovarToken() {
    let data;
    const refreshToken = localStorage.getItem("refreshToken");
    
    if (refreshToken) {
        data = getNewAccessToken(refreshToken);
        guardarAccessToken(data.access_token);
    } else {
        console.error("No hay un refreshToken disponible. Redirigiendo al inicio de sesión.");
        alert("Por favor, inicia sesión nuevamente.");
    }
}

export function guardarAccessToken(accessToken) {
    localStorage.setItem("accessToken", accessToken);
}

async function getNewAccessToken(refreshToken) {
    try {
        const response = await fetch('/auth-refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh_token: refreshToken,
                access_token: accessToken,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Token renovado exitosamente:", data);
            return data;
        } else {
            console.error(`Error al obtener nuevo accesstoken: ${response.status}`);
            alert("Ocurrió un error inesperado. Por favor, intenta nuevamente.");
        }
        return null; 
    } catch (error) {
        console.error("Error al renovar el token:", error);
        alert("Ocurrió un error al intentar renovar el token.");
    }
}   
