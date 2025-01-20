//static/js/views/game.js

export function renderGame() {
    return `
    <div id="main-game-container">
        <h1>Pong Online</h1>
        <h2><span id="left-username"></span> <span id="left-score"></span> - <span id="right-score"></span> <span id="right-username"></span></h2>
        <canvas id="pong-canvas" width="600" height="400" style="border:1px solid #000;"></canvas> 
    </div>
    `;
}

export async function initGame() {

    // game.js
    if (!hasAccessToken()) {
        // Redirect to login page
        alert("Debes iniciar sesión para jugar");
        window.sessionStorage.setItem("afterLoginRedirect", "#game");
        window.location.hash = "#login"
        return;
    }

    let userLoginData = decodeJWT(getCookie("accessToken"));

    let socket = new WebSocket(`wss://${window.location.host}/ws/game/`);

    const canvas = document.getElementById('pong-canvas');
    const context = canvas.getContext('2d');
    const leftUsernameSpan = document.getElementById('left-username');
    const rightUsernameSpan = document.getElementById('right-username');
    const leftScoreSpan = document.getElementById('left-score');
    const rightScoreSpan = document.getElementById('right-score');

    // Ball properties
    let ball = { x: canvas.height / 2, y: canvas.height / 2 };
    const ballRadius = canvas.width / 50;

    // Paddle properties
    const paddleHeight = canvas.height / 4;
    const paddleWidth = canvas.width / 50;
    // const angle = 45;
    // const angleInRadians = angle * Math.PI / 180;
    // const paddleRadius = (paddleHeight / 2) / Math.sin(angleInRadians);
    // const paddleOffset = (paddleHeight / 2) / Math.tan(angleInRadians);
    let leftPaddleY;
    let rightPaddleY;

    // Conectar al WebSocket
    socket.onopen = function(event) {
        console.log("Conectado al WebSocket.");
    };

    // Manejar mensajes entrantes del servidor
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'initial_information') {
            leftUsernameSpan.innerText = data.usernames.left_username;
            rightUsernameSpan.innerText = data.usernames.right_username;
            leftPaddleY = data.left_paddle_state;
            rightPaddleY = data.right_paddle_state;
            ball.x = data.ball_state.x;
            ball.y = data.ball_state.y;
            leftScoreSpan.innerText = data.scores.left;
            rightScoreSpan.innerText = data.scores.right;
        } else if (data.type === 'ball_state_update') {
            ball.x = data.ball_state.x;
            ball.y = data.game_state.y;
        } else if (data.type === 'left_paddle_state_update') {
            leftPaddleY = data.paddle_y;
        } else if (data.type === 'right_paddle_state_update') {
            rightPaddleY = data.paddle_y;
        } else if (data.type === 'score_update') {
            leftScoreSpan.innerText = data.scores.left;
            rightScoreSpan.innerText = data.scores.right;
        } else if (data.type === 'game_over') {
            alert("Game Over!");
        }
    };

    socket.onclose = function(event) {
        console.log("Desconectado del WebSocket.");
    };

    socket.onerror = function(event) {
        deleteCookie("accessToken");
        deleteCookie("refreshToken");
        // Refresh the page
        window.location.reload();
    }


    // Draw everything on the canvas
    function drawEverything() {
        // Clear the canvas
        context.fillStyle = 'black';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // Draw the left paddle
        context.fillStyle = 'white';
        context.fillRect(0, leftPaddleY - paddleHeight/2, paddleWidth, paddleHeight);

        // Draw the right paddle
        context.fillStyle = 'white';
        context.fillRect(canvas.width - paddleWidth, rightPaddleY - paddleHeight/2, paddleWidth, paddleHeight);

        // Draw the ball
        context.fillStyle = 'white';
        context.beginPath();
        context.arc(ball.x, ball.y, ballRadius, 0, Math.PI * 2, true);
        context.fill();
    }


    // Paddle controller

    let keys = {
        w: false,
        s: false,
        arrowUp: false,
        arrowDown: false,
    };
    
    document.addEventListener('keydown', (event) => {
        if (event.key === 'w') {
            keys.w = true;
        } else if (event.key === 's') {
            keys.s = true;
        }
        if (event.key === 'ArrowUp') {
            keys.arrowUp = true;
        } else if (event.key === 'ArrowDown') {
            keys.arrowDown = true;
        }
    });
    
    document.addEventListener('keyup', (event) => {
        if (event.key === 'w') {
            keys.w = false;
        } else if (event.key === 's') {
            keys.s = false;
        }
        if (event.key === 'ArrowUp') {
            keys.arrowUp = false;
        } else if (event.key === 'ArrowDown') {
            keys.arrowDown = false;
        }
    });

    // Game loop
    
    function gameLoop() {
        let keysPressed = [];
    
        if (keys.w) {
            keysPressed.push('w');
        } else if (keys.s) {
            keysPressed.push('s');
        }
        if (keys.arrowUp) {
            keysPressed.push('arrowUp');
        } else if (keys.arrowDown) {
            keysPressed.push('arrowDown');
        }
    
        if (keysPressed.length > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'paddle_move',
                keys: keysPressed,
            }));
        }

        drawEverything();
    
        // Call gameLoop again after a short delay
        setTimeout(gameLoop, 16.6666); // Approximately 60 frames per second
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

function deleteCookie(cname) {
    document.cookie = cname + '=;';
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