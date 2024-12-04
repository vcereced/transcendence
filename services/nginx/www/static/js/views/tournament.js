export function renderTournament() {
    return `
        <div class="container">
            <h2>Crear Torneo</h2>
            <form id="create-tournament-form">
                <div class="mb-3">
                    <label for="tournament-name" class="form-label">Nombre del Torneo</label>
                    <input type="text" class="form-control" id="tournament-name" required>
                </div>
                <button type="submit" class="btn btn-primary">Crear Torneo</button>
            </form>

            <hr>

            <h2>Unirse a un Torneo</h2>
            <ul id="tournament-list" class="list-group">
                <!-- Aquí se cargarán los torneos disponibles -->
            </ul>
        </div>
    `;
}

export function initTournament() {
    // Obtener el formulario para crear un torneo
    const createForm = document.getElementById("create-tournament-form");
    createForm.addEventListener("submit", createTournament);

    // Cargar los torneos existentes
    loadTournaments();
}

let socket = null; // Variable global para el WebSocket

// Función para cargar los torneos disponibles
async function loadTournaments() {
    const tournamentList = document.getElementById("tournament-list");
    tournamentList.innerHTML = ""; // Limpiar la lista antes de agregar nuevos torneos

    try {
        const [tournamentResponse, playerCountsResponse] = await Promise.all([
            fetch('/api/tournament/'), // Obtener los torneos existentes
            fetch('/api/tournament/player_counts') // Obtener los contadores de jugadores
        ]);
		 //DESGLOSAR BIEN ESTE ERROR HANDLING!!
		if (tournamentResponse.status === 401 || playerCountsResponse.status === 401) {
			document.getElementById("main-content").innerHTML = "<h2>401</h2><p>UNAUTHORIZED GO TO LOGIN!</p>";
			return;
		}


        const tournaments = await tournamentResponse.json();
        const playerCounts = await playerCountsResponse.json();

        tournaments.forEach(tournament => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.id = `tournament-${tournament.id}`; // Asignar un ID basado en el tournamentId
            li.textContent = tournament.name;

            const userCountContainer = document.createElement("span");
            userCountContainer.className = "badge bg-primary rounded-pill";
            userCountContainer.textContent = `Jugadores conectados: ${playerCounts[tournament.id] || 0}`;
            li.appendChild(userCountContainer);

            const joinButton = document.createElement("button");
            joinButton.className = "btn btn-success btn-sm";
            joinButton.textContent = "Unirse";
            joinButton.onclick = () => joinTournament(tournament.id);

            li.appendChild(joinButton);
            tournamentList.appendChild(li);
        });

        // Iniciar el WebSocket global si no está iniciado
        if (socket === null) {
            socket = startGlobalWebSocket();
        }
    } catch (error) { // ERROR HANDLING SEEMS TO BE HARDCODED PLEASE FIX IT
		document.getElementById("main-content").innerHTML = "<h2>401</h2><p>UNAUTHORIZED GO TO LOGIN!</p>";
        console.error("Error al cargar los torneos:", error);
    }
}

// Función para crear un torneo
async function createTournament(event) {
    event.preventDefault(); // Evitar el comportamiento por defecto del formulario

    const tournamentName = document.getElementById("tournament-name").value;

    if (tournamentName) {
        try {
            const response = await fetch('/api/tournament/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: tournamentName }),
            });

            if (response.ok) {
                alert("Torneo creado exitosamente!");
                loadTournaments(); // Recargar los torneos disponibles
            } else {
                alert("Error al crear el torneo.");
            }
        } catch (error) {
            console.error("Error al crear el torneo:", error);
            alert("Error de conexión.");
        }
    }
}

// Función para iniciar el WebSocket global
function startGlobalWebSocket() {
    const socket = new WebSocket(`wss://${window.location.host}/ws/global_tournament_counter/`);

    socket.onopen = () => {
        console.log("Conexión WebSocket global abierta");
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
		console.log("Mensaje WebSocket global:", data);
        // Si el evento contiene un "user_count" para un torneo específico
        if (data.tournamentId && data.user_count !== undefined) {
            const tournament = document.querySelector(`#tournament-${data.tournamentId}`);
            if (tournament) {
                const userCountContainer = tournament.querySelector('.badge');
                if (userCountContainer) {
                    userCountContainer.textContent = `Jugadores conectados: ${data.user_count}`;
                }
            }
        }
    };

    socket.onclose = function (event) {
        console.log("Conexión WebSocket global cerrada", event);
    };

    socket.onerror = function (error) {
        console.error("Error en WebSocket global:", error);
    };

    return socket; // Devolver la conexión WebSocket
}

// Función para unirse a un torneo
async function joinTournament(tournamentId) {
    try {
        const response = await fetch(`/api/tournament/${tournamentId}/join`, {
            method: 'POST',
        });

        if (response.ok) {
            alert("Te has unido al torneo exitosamente!");
			// Redirigir a la sala del torneo timeout 1 seg
			setTimeout(() => {
				location.hash = `tournament/room/${tournamentId}`;
			}
			, 700);
        } else {
            alert("Error al unirse al torneo.");
        }
    } catch (error) {
        console.error("Error al unirse al torneo:", error);
        alert("Error de conexión.");
    }
}
