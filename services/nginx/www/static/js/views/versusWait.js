// static/js/views/versus_wait.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderVersusWait() {
    const response = await fetch('static/html/versus_wait.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export function initVersusWait() {


    let versus_socket = null;
    if (versus_socket === null) {
        versus_socket = startVersusWebSocket(versus_socket);
    }
    // --- VARIABLES AND CONSTANTS ---

    

    const BALL_SIZE = 20;
    let obstacles = [];
    let ballX, ballY;
    let velocityX = (Math.random() - 0.5) * 8;
    let velocityY = (Math.random() - 0.5) * 8;
    let mouseX = 0, mouseY = 0;


    // --- DOM ELEMENTS ---

    const gameScreen = document.getElementById('gameScreen');
    const title = document.querySelector('.site-title');
    let screenRect = gameScreen.getBoundingClientRect();
    const ball = document.createElement('div');

    // --- FUNCTIONS ---

    window.createObstacles = function createObstacles(num) {
        const obstacleSize = 40;
        const availableWidth = window.innerWidth;
        const availableHeight = window.innerHeight;
        totalAvailableArea = availableWidth * availableHeight;
        totalObstacleArea = num * (obstacleSize * obstacleSize);

        // Si no hay suficiente espacio, no crear obstáculos
        if (totalObstacleArea > totalAvailableArea * 0.5) {
            console.warn("No hay suficiente espacio para generar los obstáculos.");
            return;
        }

        for (let i = 0; i < num; i++) {
            let x, y, overlapping;
            let attempts = 0, maxAttempts = 1000; // Evitar bucles infinitos

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
                    // Rebote de esquina: invertir ambos componentes
                    velocityX = -velocityX;
                    velocityY = -velocityY;
                } else if (hitLeft || hitRight) {
                    // Rebote lateral: solo invertir X
                    velocityX = -velocityX;
                } else if (hitTop || hitBottom) {
                    // Rebote superior/inferior: solo invertir Y
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

    
    window.eventManager.addEventListener(document, 'mousemove', (event) => {
        mouseX = event.clientX;
        mouseY = event.clientY;
    });

    window.eventManager.addEventListener(window, 'resize', recreateElements);

    window.eventManager.addEventListener(document.getElementById("copy-icon"), "click", function () {
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

    ball.classList.add('ball');
    ball.style.width = `${BALL_SIZE}px`;
    ball.style.height = `${BALL_SIZE}px`;
    document.body.appendChild(ball);
    createObstacles(Math.floor(Math.random() * 30) + 1);
    placeBall();
    moveBall();
}


function startVersusWebSocket(versus_socket) {

    versus_socket = new WebSocket(`wss://${window.location.host}/ws/versus/`);
    versus_socket.onopen = () => {
        console.log("WebSocket connection established.");
        versus_socket.send(JSON.stringify({ type: "join_queue" }));
    };
    versus_socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Message received:", data);
        console.log("Message type:", data.type);
        if (data.type === "start_game") {
            window.location.hash = "#game";
        }

    };
    versus_socket.onerror = (error) => console.error("WebSocket Error:", error);
    versus_socket.onclose = () => {
        console.log("WebSocket closed. Reconnecting in 5 seconds...");
        setTimeout(startVersusWebSocket, 5000);
    };
    return versus_socket;
}
    