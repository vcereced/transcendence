let socket = null;

export function renderTournamentRoom(tournamentId) {
    return `
        <div class="container">
            <h2>Sala del Torneo</h2>
            <p>ID del torneo: <span id="tournament-id">${tournamentId}</span></p>

            <!-- Árbol de clasificación -->
            <div class="tournament-tree">
                <div class="round round-1">
                    <div class="match" data-match="1">
                        <div class="player" data-player="1">Jugador 1</div>
                        <div class="player" data-player="2">Jugador 2</div>
                    </div>
                    <div class="match" data-match="2">
                        <div class="player" data-player="3">Jugador 3</div>
                        <div class="player" data-player="4">Jugador 4</div>
                    </div>
                    <div class="match" data-match="3">
                        <div class="player" data-player="5">Jugador 5</div>
                        <div class="player" data-player="6">Jugador 6</div>
                    </div>
                    <div class="match" data-match="4">
                        <div class="player" data-player="7">Jugador 7</div>
                        <div class="player" data-player="8">Jugador 8</div>
                    </div>
                </div>

                <div class="round round-2">
                    <div class="match" data-match="5">
                        <div class="player" data-player="9">Ganador 1</div>
                        <div class="player" data-player="10">Ganador 2</div>
                    </div>
                    <div class="match" data-match="6">
                        <div class="player" data-player="11">Ganador 3</div>
                        <div class="player" data-player="12">Ganador 4</div>
                    </div>
                </div>

                <div class="round final">
                    <div class="match" data-match="7">
                        <div class="player" data-player="13">Ganador 5</div>
                        <div class="player" data-player="14">Ganador 6</div>
                    </div>
                </div>

                <div class="champion">
                    <h3>Campeón</h3>
                    <div class="player" data-player="15">Pendiente...</div>
                </div>
            </div>
        </div>
    `;
}

export function initTournamentRoom(tournamentId) {
    document.getElementById("tournament-id").textContent = tournamentId;

    // Iniciar el WebSocket específico para este torneo
    if (socket === null) {
        socket = startTournamentWebSocket(tournamentId);
    }

    // Simulación de lógica dinámica para actualizar resultados
    simulateTournamentProgress();
}

function startTournamentWebSocket(tournamentId) {
    const socket = new WebSocket(`ws://${window.location.host}/ws/room/${tournamentId}/`);

    socket.onopen = () => {
        console.log(`Conexión WebSocket para el torneo ${tournamentId} abierta`);
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("Mensaje WebSocket del torneo:", data);

        // Aquí podrías manejar los cambios que recibes del WebSocket y actualizar la interfaz si es necesario
        // Ejemplo: actualizar los resultados de las partidas, mostrar el número de jugadores, etc.
    };

    socket.onclose = function (event) {
        console.log(`Conexión WebSocket para el torneo ${tournamentId} cerrada`, event);
    };

    socket.onerror = function (error) {
        console.error(`Error en WebSocket para el torneo ${tournamentId}:`, error);
    };

    return socket;
}

function simulateTournamentProgress() {
    const matches = document.querySelectorAll(".match");

    matches.forEach((match, index) => {
        const players = match.querySelectorAll(".player");

        // Simula un resultado aleatorio
        const winnerIndex = Math.floor(Math.random() * 2);
        const loserIndex = winnerIndex === 0 ? 1 : 0;

        players[winnerIndex].classList.add("winner");
        players[loserIndex].classList.add("loser");

        // Actualiza al ganador en la siguiente ronda (si corresponde)
        const nextMatch = document.querySelector(`.match[data-match="${Math.floor(index / 2) + 5}"]`);
        if (nextMatch) {
            const nextPlayerSlot = nextMatch.querySelector(`.player[data-player="${index + 9}"]`);
            if (nextPlayerSlot) {
                nextPlayerSlot.textContent = players[winnerIndex].textContent;
            }
        }
    });

    // Actualiza al campeón
    const finalWinner = document.querySelector(".final .player.winner");
    if (finalWinner) {
        const champion = document.querySelector(".champion .player");
        champion.textContent = finalWinner.textContent;
    }
}
