// static/js/views/tournaments_list.js

import EventListenerManager from '../utils/eventListenerManager.js';
import { handleJwtToken } from './jwtValidator.js';

export async function renderTournamentsList() {
    const response = await fetch('static/html/tournaments_list.html');
    const htmlContent = await response.text();
    return htmlContent;
}

let global_socket = null;
export function initTournamentsList() {

    // --- VARIABLES AND CONSTANTS ---

    

   
       
    // --- DOM ELEMENTS ---
    
    
    const gameLists = document.querySelectorAll('.game-list');
    const title = document.querySelector('.site-title');
    const availableContainer = document.getElementById('available-games');
    

    // --- FUNCTIONS ---

    async function loadTournaments() {
        availableContainer.innerHTML = "";

        try {
            await handleJwtToken();
            const [tournamentResponse, playerCountsResponse] = await Promise.all([
                fetch('/api/tournament/'),
                fetch('/api/tournament/player_counts')
            ]);

            if (!tournamentResponse.ok || !playerCountsResponse.ok) {
                console.error("Error al obtener torneos o contadores de jugadores");
                alert("Hubo un problema al cargar los torneos.");
                return;
            }

            const tournaments = await tournamentResponse.json();
            const playerCounts = await playerCountsResponse.json();

            tournaments.forEach(tournament => {
                const gameItem = createGameItem({
                    id: tournament.id,
                    name: tournament.name,
                    date: "-", // TO DO : No hay fecha en la API
                    users: playerCounts[tournament.id] || 0
                }, 'available');
                const joinButton = gameItem.querySelector('.btn');
                joinButton.addEventListener('click', () => joinTournament(tournament.id, tournament.name));
                availableContainer.appendChild(gameItem);
            });

            if (global_socket === null) {
                global_socket = startGlobalWebSocket();
            }
        } catch (error) {
            console.error("Error al cargar los torneos:", error);
        }
    }

    window.createGameItem = function createGameItem(game, type) {
        const gameItem = document.createElement('div');
        gameItem.classList.add('game-item');

        gameItem.innerHTML = `
            <div class="game-info" id="tournament-${game.id}">
                <div class="game-name">${game.name}</div>
                <div class="badge game-meta">Usuarios conectados: ${game.users}</div>
                <div class="game-meta">Fecha de creación: ${game.date}</div>
            </div>
            <button class="btn">${type === 'available' ? 'Unirse' : 'Visualizar'}</button>
        `;
        return gameItem;
    }

    window.displayGames = function displayGames() {
        const availableContainer = document.getElementById('available-games');

        availableGames.forEach(game => {
            const gameItem = createGameItem(game, 'available');
            availableContainer.appendChild(gameItem);
        });

    }

    async function joinTournament(tournamentId, tournamentName) {
        try {
            await handleJwtToken();
            const response = await fetch(`/api/tournament/${tournamentId}/join`, {
                method: 'POST',
            });

            if (response.ok) {
                alert("Te has unido al torneo exitosamente!"); //GARYDD1 TO DO: REPLACE THIS WITH THE POPUP
                sessionStorage.setItem("tournamentName", tournamentName);
                console.log("%ctournamentName settled", "color:blue", tournamentName);
                setTimeout(() => {
                    location.hash = `tournament/room/${tournamentId}`;
                }, 700);
            } else {
                alert("Error al unirse al torneo.");
            }
        } catch (error) {
            console.error("Error al unirse al torneo:", error);
            alert("Error de conexión.");
        }
    }

    function startGlobalWebSocket() {
        handleJwtToken().then(() => {
            const ws = new WebSocket(`wss://${window.location.host}/ws/global_tournament_counter/`);
            if (!ws) {
                console.error("WebSocket not available");
                return;
            }
            console.log("WebSocket global connection opened");
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("WebSocket message:", data);
                const tournament = document.querySelector(`#tournament-${data.tournament_id}`);
                if (tournament) {
                    const userCountContainer = tournament.querySelector('.badge');
                    if (userCountContainer) {
                        userCountContainer.textContent = `Usuarios conectados: ${data.user_count}`;
                    }
                }
            };

            ws.onerror = (error) => console.error("WebSocket Error:", error);
            ws.onclose = () => {
                console.log("WebSocket closed. Reconnecting in 5 seconds...");
                setTimeout(startGlobalWebSocket, 5000);
            };
            return ws;
        });
    }

    window.toggleFullscreen = function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }


    // --- EVENT LISTENERS ---

    gameLists.forEach(gameList => {
        let isMouseDown = false;
        let startX;
        let scrollLeft;

        window.eventManager.addEventListener(gameList, 'mousedown', (e) => {
            isMouseDown = true;
            startX = e.pageX - gameList.offsetLeft;
            scrollLeft = gameList.scrollLeft;
            gameList.style.cursor = 'grabbing';
        });

        window.eventManager.addEventListener(gameList, 'mouseleave', () => {
            isMouseDown = false;
            gameList.style.cursor = 'grab';
        });

        window.eventManager.addEventListener(gameList, 'mouseup', () => {
            isMouseDown = false;
            gameList.style.cursor = 'grab';
        });

        window.eventManager.addEventListener(gameList, 'mousemove', (e) => {
            if (!isMouseDown) return;
            e.preventDefault();
            const x = e.pageX - gameList.offsetLeft;
            const walk = (x - startX) * 3; // Controlar la velocidad del desplazamiento
            gameList.scrollLeft = scrollLeft - walk;
        });
    });

    window.eventManager.addEventListener(title, 'mouseenter', () => {
        title.classList.add('glitch');
        title.style.transform = 'translateY(-5px)';
    });

    window.eventManager.addEventListener(title, 'mouseleave', () => {
        title.classList.remove('glitch');
        title.style.transform = 'translateY(0)';
    });

    // --- INITIALIZATION ---
    loadTournaments();
    // displayGames();
}


