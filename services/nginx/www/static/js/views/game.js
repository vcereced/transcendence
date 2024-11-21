//static/js/views/game.js

export function renderGame() {
    return `
    <h1>Pong Online</h1>
	<canvas id="pong" width="600" height="400" style="border:1px solid #000;"></canvas> 
    `;
}

export function initGame() {

    // game.js

    const canvas = document.getElementById('pong');
    const context = canvas.getContext('2d');

    // Ball properties
    let ballX = canvas.width / 2;
    let ballY = canvas.height / 2;
    let ballSpeedX = 5;
    let ballSpeedY = 5;
    const ballRadius = 10;
	const speedIncrement = 1.1;

    // Paddle properties
    const paddleWidth = 10;
    const paddleHeight = 100;
    let paddleY = (canvas.height - paddleHeight) / 2;
    const paddleSpeed = 10;
    let paddleDirection = 0;

    // Draw everything on the canvas
    function drawEverything() {
        // Clear the canvas
        context.fillStyle = 'black';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // Draw the ball
        context.fillStyle = 'white';
        context.beginPath();
        context.arc(ballX, ballY, ballRadius, 0, Math.PI * 2, true);
        context.fill();

        // Draw the paddle
        context.fillStyle = 'white';
        context.fillRect(0, paddleY, paddleWidth, paddleHeight);
    }

    // Move the ball and handle collisions
    function moveEverything() {
        ballX += ballSpeedX;
        ballY += ballSpeedY;

        // Ball collision with top and bottom walls
        if (ballY - ballRadius < 0 || ballY + ballRadius > canvas.height) {
            ballSpeedY = -ballSpeedY;
        }

        // Ball collision with left wall (paddle)
        if (ballX - ballRadius < paddleWidth && ballY > paddleY && ballY < paddleY + paddleHeight) {
            ballSpeedX = -ballSpeedX;
            ballX = paddleWidth + ballRadius; // Adjust ball position to avoid "getting inside" the paddle
			ballSpeedX *= speedIncrement;
			ballSpeedY *= speedIncrement;
        } else if (ballX - ballRadius < 0) {
            // Ball missed the paddle
            resetBall();
        }

        // Ball collision with right wall
        if (ballX + ballRadius > canvas.width) {
            ballSpeedX = -ballSpeedX;
        }

        // Move the paddle
        paddleY += paddleDirection * paddleSpeed;
        paddleY = Math.max(Math.min(paddleY, canvas.height - paddleHeight), 0);
    }

    // Reset the ball to the center
    function resetBall() {
        ballX = canvas.width / 2;
        ballY = canvas.height / 2;
        ballSpeedX = 5;
        ballSpeedY = 5;
    }

    // Handle key down events
    function handleKeyDown(event) {
        switch (event.key) {
            case 'ArrowUp':
                paddleDirection = -1;
                break;
            case 'ArrowDown':
                paddleDirection = 1;
                break;
        }
    }

    // Handle key up events
    function handleKeyUp(event) {
        switch (event.key) {
            case 'ArrowUp':
            case 'ArrowDown':
                paddleDirection = 0;
                break;
        }
    }

    // Game loop
    function gameLoop() {
        moveEverything();
        drawEverything();
    }

    // Event listeners for paddle movement
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    // Start the game loop
    setInterval(gameLoop, 1000 / 30); // 30 frames per second

}