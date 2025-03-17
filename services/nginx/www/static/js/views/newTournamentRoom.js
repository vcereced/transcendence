// static/js/views/new_tournament_room.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderNewTournamentRoom() {
    const response = await fetch('static/html/new_tournament_room.html');
    const htmlContent = await response.text();
    return htmlContent;
}
let socket = null;
export function initNewTournamentRoom(tournamentId) {

    if (socket === null) {
        socket = startTournamentWebSocket(tournamentId);
    }
    const startButton = document.getElementById("start-tournament-btn");
    if (startButton) {
        startButton.addEventListener("click", () => {
            sendWebSocketMessage("start_tournament", { tournament_id: tournamentId.id });
        });
    }
    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();
    const BALL_SIZE = 20;
    let obstacles = [];
    let ballX, ballY;
    let velocityX = (Math.random() - 0.5) * 8;
    let velocityY = (Math.random() - 0.5) * 8;
    let mouseX = 0, mouseY = 0;


    // --- DOM ELEMENTS ---

    const ball = document.createElement('div');
    const gameScreen = document.getElementById('gameScreen');
    let screenRect = gameScreen.getBoundingClientRect();
    
    // --- FUNCTIONS ---

    window.createObstacles = function createObstacles(num) {
        const obstacleSize = 40;
        const availableWidth = window.innerWidth;
        const availableHeight = window.innerHeight;
        const totalAvailableArea = availableWidth * availableHeight;
        const totalObstacleArea = num * (obstacleSize * obstacleSize);

        if (totalObstacleArea > totalAvailableArea * 0.5) {
            console.warn("No hay suficiente espacio para generar los obstáculos.");
            return;
        }

        for (let i = 0; i < num; i++) {
            let x, y, overlapping;
            let attempts = 0, maxAttempts = 1000;

            do {
                x = Math.random() * (availableWidth - obstacleSize);
                y = Math.random() * (availableHeight - obstacleSize);
                overlapping = obstacles.some(obs =>
                    x < obs.x + obstacleSize && x + obstacleSize > obs.x &&
                    y < obs.y + obstacleSize && y + obstacleSize > obs.y
                );
                attempts++;
            } while (
                (overlapping ||
                    (x + obstacleSize > screenRect.left && x < screenRect.right &&
                        y + obstacleSize > screenRect.top && y < screenRect.bottom)) &&
                attempts < maxAttempts
            );

            if (attempts >= maxAttempts) {
                console.warn("No se encontraron suficientes espacios libres.");
                break;
            }

            const obstacle = document.createElement('div');
            obstacle.classList.add('obstacle');
            obstacle.style.left = `${x}px`;
            obstacle.style.top = `${y}px`;
            document.body.appendChild(obstacle);
            obstacles.push({ x, y, width: obstacleSize, height: obstacleSize });
        }
    }

    window.placeBall = function placeBall() {
        do {
            ballX = Math.random() * window.innerWidth;
            ballY = Math.random() * window.innerHeight;
        } while (
            (ballX + BALL_SIZE > screenRect.left && ballX < screenRect.right &&
                ballY + BALL_SIZE > screenRect.top && ballY < screenRect.bottom) ||
            obstacles.some(obs => ballX + BALL_SIZE > obs.x && ballX < obs.x + obs.width &&
                ballY + BALL_SIZE > obs.y && ballY < obs.y + obs.height)
        );
        return { ballX, ballY };
    }

    window.moveBall = function moveBall() {
        ballX += velocityX;
        ballY += velocityY;

        if (ballX <= 0 || ballX >= window.innerWidth - BALL_SIZE) velocityX = -velocityX;
        if (ballY <= 0 || ballY >= window.innerHeight - BALL_SIZE) velocityY = -velocityY;

        let dx = ballX - mouseX;
        let dy = ballY - mouseY;
        let distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < BALL_SIZE) {
            let angle = Math.atan2(dy, dx);
            velocityX = Math.cos(angle) * 8;
            velocityY = Math.sin(angle) * 8;
        }

        if (
            ballX + BALL_SIZE > screenRect.left && ballX < screenRect.right &&
            ballY + BALL_SIZE > screenRect.top && ballY < screenRect.bottom
        ) {
            if (ballX < screenRect.left || ballX > screenRect.right - BALL_SIZE) velocityX = -velocityX;
            if (ballY < screenRect.top || ballY > screenRect.bottom - BALL_SIZE) velocityY = -velocityY;
        }

        obstacles.forEach(obs => {
            if (
                ballX + BALL_SIZE > obs.x && ballX < obs.x + obs.width &&
                ballY + BALL_SIZE > obs.y && ballY < obs.y + obs.height
            ) {
                let hitLeft = ballX + BALL_SIZE >= obs.x && ballX < obs.x;
                let hitRight = ballX <= obs.x + obs.width && ballX + BALL_SIZE > obs.x + obs.width;
                let hitTop = ballY + BALL_SIZE >= obs.y && ballY < obs.y;
                let hitBottom = ballY <= obs.y + obs.height && ballY + BALL_SIZE > obs.y + obs.height;

                if ((hitLeft || hitRight) && (hitTop || hitBottom)) {
                    velocityX = -velocityX;
                    velocityY = -velocityY;
                } else if (hitLeft || hitRight) {
                    velocityX = -velocityX;
                } else if (hitTop || hitBottom) {
                    velocityY = -velocityY;
                }
            }
        });
        ball.style.left = ballX + 'px';
        ball.style.top = ballY + 'px';

        if (ballX + BALL_SIZE / 2 > window.innerWidth || ballY + BALL_SIZE / 2 > window.innerHeight || ballX + BALL_SIZE / 2 < 0 || ballY + BALL_SIZE / 2 < 0) {
            placeBall();
            requestAnimationFrame(moveBall);
        } else {
            requestAnimationFrame(moveBall);
        }
    }

    window.exitGame = function exitGame() {
        alert('Si sales perderás tu posición en la cola de espera. ¿Estás seguro de que quieres salir?');
    }

    window.deleteObstacles = function deleteObstacles() {
        document.querySelectorAll('.obstacle').forEach(el => el.remove());
        obstacles = [];
    }

    window.recreateElements = function recreateElements() {
        deleteObstacles();
        screenRect = gameScreen.getBoundingClientRect();
        createObstacles(Math.floor(Math.random() * 30) + 1);
        placeBall();
    }

    window.copyText = function copyText() {
        const text = document.getElementById("text-to-copy").innerText;
        navigator.clipboard.writeText(text).then(() => {
            const message = document.getElementById("copied-message");
            message.style.opacity = "1";
            setTimeout(() => {
                message.style.opacity = "0";
            }, 1500);
        }).catch(err => {
            console.error("Error al copiar: ", err);
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

    eventManager.addEventListener(document, 'mousemove', (event) => {
        mouseX = event.clientX;
        mouseY = event.clientY;
    });

    eventManager.addEventListener(window, 'resize', recreateElements);

    eventManager.addEventListener(document.getElementById("copy-icon"), "click", copyText);

    const title = document.querySelector('.site-title');
    eventManager.addEventListener(title, 'mouseenter', () => {
        title.classList.add('glitch');
        title.style.transform = 'translateY(-5px)';
    });

    eventManager.addEventListener(title, 'mouseleave', () => {
        title.classList.remove('glitch');
        title.style.transform = 'translateY(0)';
    });

    // --- INITIALIZATION ---

    ball.classList.add('ball');
    ball.style.width = `${BALL_SIZE}px`;
    ball.style.height = `${BALL_SIZE}px`;
    document.body.appendChild(ball);

    createObstacles(Math.floor(Math.random() * 30) + 1);
    placeBall();
    moveBall();

    return () => eventManager.removeAllEventListeners();
}

//SOCKET MANAGEMENT

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
        if (data.type === "start_tournament") {
            start_tournament(data);
        }
        if (data.type === "game_end") {
            // update after a small delay to see the changesk
            setTimeout(() => {
                update_tournament_tree(data);
            }, 0.1);
        }
        //HERE WE CAN ADD MORE CONDITIONS TO UPDATE THE TOURNAMENT TREE
        //OR TO START THE TOURNAMENT.
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
        const [name, id] = user.split(":"); 
        userElement.textContent = name;
        userListContainer.appendChild(userElement);
    });
}

function sendWebSocketMessage(type, data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("Enviando mensaje WebSocket:", { type, ...data });
        socket.send(JSON.stringify({ type, ...data }));
    } else {
        console.error("WebSocket no está conectado.");
    }
}

function start_tournament(data) {
    alert("¡El torneo ha comenzado!");
    
    
    const parsedTournamentTree = {};
    for (const key in data.tournament_tree) {
        parsedTournamentTree[key] = JSON.parse(data.tournament_tree[key]);
    }

    console.log("Árbol del torneo:", parsedTournamentTree);

    parsedTournamentTree.round_1.forEach((match) => {
        const matchElement = document.querySelector(`.match[data-match="${match.tree_id}"]`);
        if (matchElement) {
            const players = matchElement.querySelectorAll(".player");
            if (players.length >= 2) {
                players[0].textContent = match.players.left.username;
                players[1].textContent = match.players.right.username;
            }
        }
    });
}

function update_tournament_tree(data) {
    const { match_id, winner, loser } = data;
    console.log("updating tournament tree with:", data);
    console.log('match_id>', match_id);
    // Encontrar el partido actual
    const currentMatch = document.querySelector(`.match[data-match="${match_id}"]`);
    if (!currentMatch) {
        console.error(`No se encontró el partido con ID ${match_id}`);
        return;
    }

    // Marcar al ganador y perdedor
    const players = currentMatch.querySelectorAll(".player");
    players.forEach(player => {
        console.log('player>', player);
        console.log('player.textContent>', player.textContent);
        if (player.textContent === winner) {
            player.classList.add("winner");
        } else if (player.textContent === loser) {
            player.classList.add("loser");
        }
    });

    // Determinar el siguiente partido
    const nextMatchId = Math.floor((match_id - 1) / 2) + 5;
    console.log('nextMatchId>', nextMatchId);
    const nextMatch = document.querySelector(`.match[data-match="${nextMatchId}"]`);
    
    if (nextMatch) {
        console.log('entered to if nextMatch>', nextMatch);
        // Encontrar un espacio disponible en el siguiente partido
        const nextPlayers = nextMatch.querySelectorAll(".player");
        for (let i = 0; i < nextPlayers.length; i++) {
            if (nextPlayers[i].textContent.includes("Winner")) {
                nextPlayers[i].textContent = winner;
                break;
            }
        }
    }

    // Actualizar campeón si es la final
    if (Number(match_id) === 7) {
        console.log("The champion is:", winner);
        const champion = document.querySelector(".champion .player");
        if (champion) {
            champion.textContent = winner;
        }
    }
}