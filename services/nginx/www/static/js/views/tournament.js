// static/js/views/tournament.js

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

// static/js/views/torneo.js

export function initTournament() {
    // Obtener el formulario para crear un torneo
    const createForm = document.getElementById("create-tournament-form");
    createForm.addEventListener("submit", createTournament);

    // Cargar los torneos existentes
    loadTournaments();
}

// Función para crear un torneo
async function createTournament(event) {
    event.preventDefault();  // Evitar el comportamiento por defecto del formulario

    const tournamentName = document.getElementById("tournament-name").value;

    if (tournamentName) {
        try {
            const response = await fetch('/api/tournament/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: tournamentName })
            });

            if (response.ok) {
                alert("Torneo creado exitosamente!");
                loadTournaments();  // Recargar los torneos disponibles
            } else {
                alert("Error al crear el torneo.");
            }
        } catch (error) {
            console.error("Error al crear el torneo:", error);
            alert("Error de conexión.");
        }
    }
}

// Función para cargar los torneos disponibles
async function loadTournaments() {
    const tournamentList = document.getElementById("tournament-list");
    tournamentList.innerHTML = "";  // Limpiar la lista antes de agregar nuevos torneos

    try {
        const response = await fetch('/api/tournament');  // Obtener los torneos existentes
        const tournaments = await response.json();

        tournaments.forEach(tournament => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.textContent = tournament.name;

            // Agregar el botón para unirse al torneo
            const joinButton = document.createElement("button");
            joinButton.className = "btn btn-success btn-sm";
            joinButton.textContent = "Unirse";
            joinButton.onclick = () => joinTournament(tournament.id);

            li.appendChild(joinButton);
            tournamentList.appendChild(li);
        });
    } catch (error) {
        console.error("Error al cargar los torneos:", error);
    }
}

// Función para unirse a un torneo
async function joinTournament(tournamentId) {
    try {
        const response = await fetch(`/api/tournament/${tournamentId}/join`, {
            method: 'POST'
        });

        if (response.ok) {
            alert("Te has unido al torneo exitosamente!");
        } else {
            alert("Error al unirse al torneo.");
        }
    } catch (error) {
        console.error("Error al unirse al torneo:", error);
        alert("Error de conexión.");
    }
}
