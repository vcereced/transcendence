export async function checkActiveGame() {
    // fetch to server to check if a pong or rps game is active and redirect to the correct route
    try {
        const response = await fetch('/api/game/active');
        if (!response.ok) {
            console.error('Error checking active game. Response not ok:', response.status);
        }
        const data = await response.json();
        if (data.has_active_rps_game) {
            location.hash = '#rock-paper-scissors';
        } else if (data.has_active_pong_game) {
            location.hash = '#game';
        } else {
            console.log('No active game');
        }
    } catch (error) {
        console.error('Error checking active game. Error in fetch:', error);
    }
}