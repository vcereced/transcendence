export async function checkActiveGame(document, reconnectingPopupParent) {
    // fetch to server to check if a pong or rps game is active and redirect to the correct route
    try {
        const response = await fetch('/api/game/active/');
        if (!response.ok) {
            console.error('Error checking active game. Response not ok:', response);
        }
        const data = await response.json();
        let redirectHash;
        if (data.has_active_rps_game) {
            redirectHash = '#rock-paper-scissors';
        } else if (data.has_active_pong_game) {
            redirectHash = '#game';
        } else {
            console.log('No active game');
            return;
        }
        reconnectingPopupParent.appendChild(buildReconnectingPopup(document));
        setTimeout(() => {
            window.location.hash = redirectHash;
        }, 2000);

    } catch (error) {
        console.error('Error checking active game. Error in fetch:', error);
    }
}

function buildReconnectingPopup(document) {
    const popup = document.createElement('div');
    popup.id = 'reconnecting-popup';
    popup.classList.add('reconnecting-popup');
    popup.innerHTML = `
        <div class="reconnecting-container">
            <h2 class="dots">Reconectando</h2>
            <p>Hemos detectado que tienes una partida en curso</p>
        </div>
    `;
    return popup;
}