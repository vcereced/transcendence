// static/js/views/new_tournament_room.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderNewTournamentRoom() {
    const response = await fetch('static/html/new_tournament_room.html');
    const htmlContent = await response.text();
    return htmlContent;
}

let room_socket = null;
let isHistoryBack = false;
export function initNewTournamentRoom(tournamentId) {
    if (room_socket === null) {
        room_socket = startTournamentWebSocket(tournamentId);
    }
    const startButton = document.getElementById("start-tournament-btn");
    if (startButton) {
        startButton.addEventListener("click", () => {
            sendWebSocketMessage("start_tournament", { tournament_id: tournamentId.id });
        });
    }

    restoreTournamentTree();

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
    const room_socket = new WebSocket(`wss://${window.location.host}/ws/room/${tournamentId.id}/`);

    room_socket.onopen = () => {
        console.log(`Conexión WebSocket para el torneo ${tournamentId.id} abierta`);
    };

    room_socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("Mensaje WebSocket del torneo:", data);
        
        if (data.type === "user_list" ) {
            updateUserList(data.user_list);
        }
        if (data.type === "start_tournament") {
            start_tournament(data);
            setTimeout(() => {
                window.location.hash = '#game'; 
            }, 1000);
        }
        if (data.type === "game_end") {
            // update after a small delay to see the changesk
            // window.history.back();
            setTimeout(() => {
                update_tournament_tree(data);
            }, 0.1);
        }
        //HERE WE CAN ADD MORE CONDITIONS TO UPDATE THE TOURNAMENT TREE
        //OR TO START THE TOURNAMENT.
    };

    room_socket.onclose = function (event) {
        console.log(`Conexión WebSocket para el torneo ${tournamentId.id} cerrada`, event);
    };

    room_socket.onerror = function (error) {
        console.error(`Error en WebSocket para el torneo ${tournamentId.id}:`, error);
    };

    return room_socket;
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
    //guardar en session storage
    sessionStorage.setItem("user_list", JSON.stringify(userList));

    //GARYDD1 TO DO: MANAGE THE START TOURNAMENT BUTTON/EVENT WHEN THE USER LIST IS FULL.
    // if (userList.length >= 8) {
        
    // }
}

function sendWebSocketMessage(type, data) {
    if (room_socket && room_socket.readyState === WebSocket.OPEN) {
        console.log("Enviando mensaje WebSocket:", { type, ...data });
        room_socket.send(JSON.stringify({ type, ...data }));
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

    sessionStorage.setItem("tournament_tree", JSON.stringify(data.tournament_tree));

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
    console.log("Updating tournament tree:", data);

    const currentMatch = document.querySelectorAll(`.match[data-match="${match_id}"]`);
    if (!currentMatch) {
        console.error(`No se encontró el partido con ID ${match_id}`);
        return;
    }

    currentMatch.forEach((match) => {
        const players = match.querySelectorAll(".player");
        players.forEach(player => {
            if (player.textContent === winner) {
                player.classList.add("winner");
            } else if (player.textContent === loser) {
                player.classList.add("loser");
            }
        });
    }
    );
   
    const nextMatch = getNextMatch(match_id);
    if (nextMatch) {
        updateNextMatch(nextMatch, winner, match_id);
    }

   
    if (isFinalMatch(match_id)) {
        updateChampion(winner);
    }
    sessionStorage.setItem("tournament_tree", JSON.stringify(data.tournament_tree));
}

function getNextMatch(currentMatchId) {
    const nextMatchId = Math.floor((currentMatchId - 1) / 2) + 5;
    return document.querySelector(`.match[data-match="${nextMatchId}"]`);
}


function updateNextMatch(nextMatch, winner, currentMatchId) {
    console.log("Updating netxtMatch, winner, currentMatchID:", nextMatch, winner, currentMatchId);
    const targetPlayer = document.querySelector(`.player[data-player="winner-${currentMatchId}"]`);
    if (targetPlayer) {
        targetPlayer.textContent = winner;  
    } else {
        console.error(`No se encontró un jugador con data-player="winner-${currentMatchId}" en el siguiente partido.`);
    }
}

function isFinalMatch(matchId) {
    return Number(matchId) === 7;
}

function updateChampion(winner) {
    console.log("El campeón es:", winner);
    const champion = document.querySelector(".champion .player");
    if (champion) {
        champion.classList.add("championship");
        champion.textContent = winner;
    }
}

window.addEventListener('hashchange', function(event) {
    // Verificar si la URL contiene '#tournament' o '#game'
    console.log('URL:', window.location.hash);
    if (!window.location.hash.includes('tournament/room') && !window.location.hash.includes('game')) {
        closeWebSocket();
        clearTournamentTree(); 
    }
});

function closeWebSocket() {
    if (room_socket) {
        console.log('Cerrando WebSocket...');
        room_socket.close();  
        room_socket = null;  
    }
}

function clearTournamentTree() {
    sessionStorage.removeItem('tournament_tree');  // Borra el árbol del torneo guardado en sessionStorage
    console.log('Datos del torneo eliminados de sessionStorage');
}

function restoreTournamentTree() {
    
    const savedTree = sessionStorage.getItem("tournament_tree");

    if (savedTree) {
        const parsedTournamentTree = {};
        const rawTree = JSON.parse(savedTree);
        
        for (const key in rawTree) {
            parsedTournamentTree[key] = JSON.parse(rawTree[key]);
        }

        console.log("Restaurando árbol desde localStorage:", parsedTournamentTree);

        for (const roundKey in parsedTournamentTree) {
            const roundMatches = parsedTournamentTree[roundKey];
        
            roundMatches.forEach((match) => {
                const { tree_id, players, winner, loser } = match;
                const treeIdStr = String(tree_id);
                const participants = Object.values(players).filter(p => p && p.username);
        
                
                if (treeIdStr === "7") {
                    participants.forEach((participant) => {
                        const username = participant.username;
        
                        
                        const isWinner = username === winner;
                        const isLoser = username === loser;
        
                        
                        const originTreeId = Object.keys(players).find(
                            key => players[key]?.username === username
                        );
        
                        let originTree = null;
        
                       
                        if (originTreeId === "left") {
                            originTree = "5";
                        } else if (originTreeId === "right") {
                            originTree = "6";
                        }
        
                        if (originTree) {
                            const playerSlot = document.querySelector(`.player[data-player="winner-${originTree}"]`);
                            if (playerSlot) {
                                playerSlot.textContent = username;
                                playerSlot.classList.remove("winner", "loser");
                                if (isWinner) playerSlot.classList.add("winner");
                                else if (isLoser) playerSlot.classList.add("loser");
                            }
                        }
                        
                        if (isWinner) {
                            const championDiv = document.querySelector('.player[data-player="champion"]');
                            if (championDiv) {
                                championDiv.textContent = username;
                                championDiv.classList.add("championship");
                            }
                        }
                    });
        
                    return; 
                }
        
                
                const matchElements = document.querySelectorAll(`.match[data-match="${treeIdStr}"]`);
        
                matchElements.forEach((matchElement) => {
                    const playerDivs = Array.from(matchElement.querySelectorAll(".player"));
        
                    
                    playerDivs.forEach(div => div.classList.remove("winner", "loser"));
        
                    participants.forEach((participant) => {
                        const username = participant.username;
        
                        const availableDiv = playerDivs.find(div => {
                            const content = div.textContent.trim().toLowerCase();
                            return (
                                content === '' ||
                                content.startsWith('player') ||
                                content.startsWith('winner') ||
                                content === 'champion'
                            );
                        });
        
                        if (availableDiv) {
                            availableDiv.textContent = username;
                            if (username === winner) availableDiv.classList.add("winner");
                            else if (username === loser) availableDiv.classList.add("loser");
        
                            
                            const idx = playerDivs.indexOf(availableDiv);
                            if (idx > -1) playerDivs.splice(idx, 1);
                        }
                    });
                });
            });
        }
        
    }
}
