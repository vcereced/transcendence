let socket = null;

export function renderTournamentRoom(tournamentId) {
    return `
        <div class="container">
            <h2>Sala del Torneo</h2>
            <p>ID del torneo: <span id="tournament-id">${tournamentId.id}</span></p>

            <!-- Lista dinámica de usuarios -->
            <div class="connected-users">
                <h3>Usuarios Conectados</h3>
                <ul id="user-list"></ul>
            </div>

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
    if (socket === null) {
        socket = startTournamentWebSocket(tournamentId);
    }

    simulateTournamentProgress();
}

function startTournamentWebSocket(tournamentId) {
    console.log('tournamentId>', tournamentId.id);
    const socket = new WebSocket(`wss://${window.location.host}/ws/room/${tournamentId.id}/`);

    socket.onopen = () => {
        console.log(`Conexión WebSocket para el torneo ${tournamentId.id} abierta`);
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("Mensaje WebSocket del torneo:", data);

        if (data.type === "user_list" ) {
            updateUserList(data.user_list);
        }
    };

    socket.onclose = function (event) {
        console.log(`Conexión WebSocket para el torneo ${tournamentId.id} cerrada`, event);
    };

    socket.onerror = function (error) {
        console.error(`Error en WebSocket para el torneo ${tournamentId.id}:`, error);
    };

    return socket;
}

function updateUserList(userList) {
    const userListContainer = document.getElementById("user-list");

    if (!userListContainer) {
        console.error("Elemento de lista de usuarios no encontrado");
        return;
    }

    userListContainer.innerHTML = "";

    userList.forEach((user) => {
        const userElement = document.createElement("li");
        userElement.textContent = user;
        userListContainer.appendChild(userElement);
    });
}

function simulateTournamentProgress() {
    const matches = document.querySelectorAll(".match");

    matches.forEach((match, index) => {
        const players = match.querySelectorAll(".player");

        const winnerIndex = Math.floor(Math.random() * 2);
        const loserIndex = winnerIndex === 0 ? 1 : 0;

        players[winnerIndex].classList.add("winner");
        players[loserIndex].classList.add("loser");

        const nextMatch = document.querySelector(`.match[data-match="${Math.floor(index / 2) + 5}"]`);
        if (nextMatch) {
            const nextPlayerSlot = nextMatch.querySelector(`.player[data-player="${index + 9}"]`);
            if (nextPlayerSlot) {
                nextPlayerSlot.textContent = players[winnerIndex].textContent;
            }
        }
    });

    const finalWinner = document.querySelector(".final .player.winner");
    if (finalWinner) {
        const champion = document.querySelector(".champion .player");
        champion.textContent = finalWinner.textContent;
    }
}
