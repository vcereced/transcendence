//static/js/views/game.js

export function renderGame() {
    return `
    <div id="main-game-container">
        <h1>Pong Online</h1>
        <h2>Bienvenido <span id="username"></span></h2>
        <canvas id="pong-canvas" width="600" height="400" style="border:1px solid #000;"></canvas> 
    </div>
    `;
}

export async function initGame() {

    // game.js
    if (!hasAccessToken()) {
        document.getElementById("main-game-container").innerHTML = "<h2>401</h2><p>UNAUTHORIZED GO TO LOGIN!</p>";
        return;
    }

    let userLoginData = decodeJWT(getCookie("accessToken"));
    document.getElementById("username").innerText = userLoginData.username;

    let socket = new WebSocket(`wss://${window.location.host}/ws/game/`);

    const canvas = document.getElementById('pong-canvas');
    const context = canvas.getContext('2d');

    // Ball properties
    let ball = { x: canvas.width / 2, y: canvas.height / 2 };
    const ballRadius = 10;

    // Paddle properties
    const angle = 45;
    const paddleHeight = canvas.height / 4;
    const angleInRadians = angle * Math.PI / 180;
    const paddleRadius = (paddleHeight / 2) / Math.sin(angleInRadians);
    const paddleOffset = (paddleHeight / 2) / Math.tan(angleInRadians);
    let leftPaddleY;
    let rightPaddleY;

    // Conectar al WebSocket
    socket.onopen = function(event) {
        console.log("Conectado al WebSocket.");
    };

    // Manejar mensajes entrantes del servidor
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        // console.log("Mensaje WebSocket:", data);

        if (data.type === 'game_state_update') {
            // Posiciones iniciales de la bola y palas
            ball.x = data.game_state.ball.x;
            ball.y = data.game_state.ball.y;
            leftPaddleY = data.game_state.left.paddle_y;
            rightPaddleY = data.game_state.right.paddle_y;
            drawEverything();
        }
    };

    socket.onclose = function(event) {
        console.log("Desconectado del WebSocket.");
    };


    // Draw everything on the canvas
    function drawEverything() {
        // Clear the canvas
        context.fillStyle = 'black';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // Draw the ball
        context.fillStyle = 'white';
        context.beginPath();
        context.arc(ball.x, ball.y, ballRadius, 0, Math.PI * 2, true);
        context.fill();

        // Draw the left paddle as an arc
        context.fillStyle = 'white';
        context.beginPath();
        context.arc(0 - paddleOffset, leftPaddleY + paddleRadius, paddleRadius, 0, Math.PI * 2, true);
        context.fill();

        // Draw the right paddle as an arc
        context.fillStyle = 'white';
        context.beginPath();
        context.arc(canvas.width + paddleOffset, rightPaddleY + paddleRadius, paddleRadius, 0, Math.PI * 2, true);
        context.fill();
    }


    // Paddle controller

    let keys = {
        w: false,
        s: false
    };
    
    document.addEventListener('keydown', (event) => {
        if (event.key === 'w') {
            keys.w = true;
        } else if (event.key === 's') {
            keys.s = true;
        }
    });
    
    document.addEventListener('keyup', (event) => {
        if (event.key === 'w') {
            keys.w = false;
        } else if (event.key === 's') {
            keys.s = false;
        }
    });


    // Collision detection

    // Detect collisions
    function detectCollisions() {
        // Ball and left paddle collision
        if (ball.x - ball.radius < paddleWidth && ball.y > leftPaddleY && ball.y < leftPaddleY + paddleHeight) {
            console.log('Collision detected! Ball and left paddle');
        }

        // Ball and right paddle collision
        if (ball.x + ball.radius > canvas.width - paddleWidth && ball.y > rightPaddleY && ball.y < rightPaddleY + paddleHeight) {
            console.log('Collision detected! Ball and right paddle');
        }

        // Ball and top border collision
        if (ball.y - ball.radius < 0) {
            console.log('Collision detected! Ball and top border');
        }

        // Ball and bottom border collision
        if (ball.y + ball.radius > canvas.height) {
            console.log('Collision detected! Ball and bottom border');
        }

        // Ball and left border collision
        if (ball.x - ball.radius < 0) {
            console.log('Collision detected! Ball and left border');
        }

        // Ball and right border collision
        if (ball.x + ball.radius > canvas.width) {
            console.log('Collision detected! Ball and right border');
        }
    }



    // Game loop
    
    function gameLoop() {
        let moveDirection = null;
    
        if (keys.w) {
            moveDirection = 'up';
        } else if (keys.s) {
            moveDirection = 'down';
        }
    
        if (moveDirection && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'paddle_move',
                direction: moveDirection,
            }));
        }

        // Detect collisions
        // detectCollisions();
    
        // Call gameLoop again after a short delay
        setTimeout(gameLoop, 16); // Approximately 60 frames per second
    }
    
    // Start the game loop
    gameLoop();

}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}

function decodeJWT(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

function hasAccessToken() {
    if (getCookie("accessToken") === "") {
        return false;
    }
    return true;
}