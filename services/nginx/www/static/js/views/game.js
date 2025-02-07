import { handleJwtToken } from './jwtValidator.js';
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

    // let userLoginData = decodeJWT(getCookie("accessToken"));
    await handleJwtToken();
    let socket = new WebSocket(`wss://${window.location.host}/ws/game/`);

    const canvas = document.getElementById('pong-canvas');
    const maxCanvasHeightToWindow = 0.6;
    const maxCanvasWidthToWindow = 0.6;
    const context = canvas.getContext('2d');
    const leftUsernameSpan = document.getElementById('left-username');
    const rightUsernameSpan = document.getElementById('right-username');
    const leftScoreSpan = document.getElementById('left-score');
    const rightScoreSpan = document.getElementById('right-score');

    let fieldHeightProportion;
    let fieldWidthProportion;
    let ballRadiusProportion;
    let paddleRadiusProportion;
    let paddleOffsetProportion;

    let fieldHeight;
    let fieldWidth;
    let ballRadius;
    let paddleRadius;
    let paddleOffset;

    let angleInRadians;
    let fps;

    let ball = { x: canvas.height / 2, y: canvas.height / 2 }
    let leftPaddleY;
    let rightPaddleY;

    // Conectar al WebSocket
    socket.onopen = function(event) {
        console.log("Conectado al WebSocket.");
    };

    // Manejar mensajes entrantes del servidor
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'game_state_update') {
            leftPaddleY = data.game_state.left.paddle_y * fieldHeight;
            rightPaddleY = data.game_state.right.paddle_y * fieldHeight;
            ball.x = data.game_state.ball.x * fieldHeight;
            ball.y = data.game_state.ball.y * fieldHeight;
            leftScoreSpan.innerText = data.game_state.left.score;
            rightScoreSpan.innerText = data.game_state.right.score;
            drawEverything();

        } else if (data.type === 'initial_information') {
            leftUsernameSpan.innerText = data.left_player_username;
            rightUsernameSpan.innerText = data.right_player_username;

            fieldHeightProportion = data.field_height;
            fieldWidthProportion = data.field_width;
            ballRadiusProportion = data.ball_radius;
            paddleRadiusProportion = data.paddle_radius;
            paddleOffsetProportion = data.paddle_offset;

            fieldHeight = fieldHeightProportion * maxCanvasHeightToWindow * window.innerHeight;
            fieldWidth = fieldWidthProportion * fieldHeight;
            if (fieldWidth > maxCanvasWidthToWindow * window.innerWidth) {
                fieldWidth = maxCanvasWidthToWindow * window.innerWidth;
                fieldHeight = fieldWidth / fieldWidthProportion;
            }

            ballRadius = ballRadiusProportion * fieldHeight;
            paddleOffset = paddleOffsetProportion * fieldHeight;
            paddleRadius = paddleRadiusProportion * fieldHeight;
            fps = data.fps;
            angleInRadians = data.paddle_edge_angle_radians;

            canvas.setAttribute('height', fieldHeight);
            canvas.setAttribute('width', fieldWidth);

            gameLoop();
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

        // Draw the left paddle as an arc
        context.fillStyle = 'white';
        context.beginPath();
        context.arc(-paddleOffset, leftPaddleY, paddleRadius, angleInRadians, -angleInRadians, true);
        context.fill();

        // Draw the right paddle as an arc
        context.beginPath();
        context.arc(canvas.width + paddleOffset, rightPaddleY, paddleRadius, Math.PI + angleInRadians , Math.PI - angleInRadians, true);
        context.fill();
        

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

    window.addEventListener('blur', () => {
        keys.w = false;
        keys.s = false;
        keys.arrowUp = false;
        keys.arrowDown = false;
    });

    window.addEventListener('resize', () => {
        fieldHeight = fieldHeightProportion * maxCanvasHeightToWindow * window.innerHeight;
        fieldWidth = fieldWidthProportion * fieldHeight;
        if (fieldWidth > maxCanvasWidthToWindow * window.innerWidth) {
            fieldWidth = maxCanvasWidthToWindow * window.innerWidth;
            fieldHeight = fieldWidth / fieldWidthProportion;
        }

        ballRadius = ballRadiusProportion * fieldHeight;
        paddleOffset = paddleOffsetProportion * fieldHeight;
        paddleRadius = paddleRadiusProportion * fieldHeight;

        canvas.setAttribute('height', fieldHeight);
        canvas.setAttribute('width', fieldWidth);
        drawEverything();
    })

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
    
        // Call gameLoop again after a short delay
        setTimeout(gameLoop, 1000 / fps); // Approximately 60 frames per second
    }

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