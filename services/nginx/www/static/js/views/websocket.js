import { handleJwtToken } from './jwtValidator.js';

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

export async function openWebSocket(secondTry) {
    const messagesDiv = document.getElementById("messages");
    const roomNameInput = document.getElementById("roomName");
    const roomName = roomNameInput.value.trim();

    if (!roomName) {
        console.log("Name of room empty, fill it");
        return;
    }

    let socket;
            // Establecer la conexión WebSocket si el token es válido
            await handleJwtToken();
            socket = new WebSocket(`wss://localhost:8443/ws/room/${roomName}/`);

            // Event listener cuando la conexión se abra
            socket.onopen = () => {
                console.log("Websocket connection OK");
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
            socket.onclose = async (event) => {
                console.log(`token has expired or suddenly closed: websocket.code: ${event.code}`);
            };
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

        if (!token) {
            alert("Por favor, inicia sesión.");
            return;
        }

        openWebSocket(false);
    });
}
