export function renderTournamentRoom(tournamentId) {
    return `
        <div class="container">
            <h2>Sala del Torneo</h2>
            <p>ID del torneo: <span id="tournament-id">${tournamentId}</span></p>

            <!-- Árbol de clasificación -->
            <div class="tournament-tree">
                <div class="round round-1">
                    <div class="match">
                        <div class="player">Jugador 1</div>
                        <div class="player">Jugador 2</div>
                    </div>
                    <div class="match">
                        <div class="player">Jugador 3</div>
                        <div class="player">Jugador 4</div>
                    </div>
                    <div class="match">
                        <div class="player">Jugador 5</div>
                        <div class="player">Jugador 6</div>
                    </div>
                    <div class="match">
                        <div class="player">Jugador 7</div>
                        <div class="player">Jugador 8</div>
                    </div>
                </div>

                <div class="round round-2">
                    <div class="match">
                        <div class="player">Ganador 1</div>
                        <div class="player">Ganador 2</div>
                    </div>
                    <div class="match">
                        <div class="player">Ganador 3</div>
                        <div class="player">Ganador 4</div>
                    </div>
                </div>

                <div class="round final">
                    <div class="match">
                        <div class="player">Ganador 5</div>
                        <div class="player">Ganador 6</div>
                    </div>
                </div>

                <div class="champion">
                    <h3>Campeón</h3>
                    <div class="player">Nombre del campeón</div>
                </div>
            </div>

            <!-- Lista de jugadores -->
            <ul id="player-list" class="list-group">
                <!-- Aquí se mostrarán los jugadores -->
            </ul>
        </div>
    `;
}

export function initTournamentRoom(tournamentId) {
    // Insertar el ID del torneo en la página
    document.getElementById("tournament-id").textContent = tournamentId;

    // Simulando jugadores iniciales (esto se debe reemplazar por los jugadores reales más adelante)
    const playerList = document.getElementById("player-list");
    const players = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4", "Jugador 5", "Jugador 6", "Jugador 7", "Jugador 8"];
    
    players.forEach(player => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = player;
        playerList.appendChild(li);
    });
}
