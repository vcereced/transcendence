// static/js/views/rock_paper_scissors.js
import { handleJwtToken } from './jwtValidator.js';
import { deleteCookie, hasAccessToken } from '../utils/auth_management.js';

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderRockPaperScissors() {
    const response = await fetch('static/html/rock_paper_scissors.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export async function initRockPaperScissors() {

    // --- INITIALIZATION ---

    if (!hasAccessToken()) {
        alert("Debes iniciar sesión para jugar");
        window.sessionStorage.setItem("afterLoginRedirect", "#rock_paper_scissors");
        window.location.hash = "#login"
        return;
    }
    await handleJwtToken();

    let socket = new WebSocket(`wss://${window.location.host}/ws/game/rock-paper-scissors/`);


    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();
    let leftPlayer = { id: null, username: null };
    let rightPlayer = { id: null, username: null };
    let requestedChoices = { leftPlayer: null, rightPlayer: null };
    let gameFinished = false;
    let popupShown = false;


    // --- DOM ELEMENTS ---

    const title = document.querySelector('.site-title');
    const timerValue = document.querySelector('#timer span');
    const leftPlayerUsername = document.querySelector('#leftPlayer .username');
    const rightPlayerUsername = document.querySelector('#rightPlayer .username');
    const popup = document.getElementById("result-popup");

    // --- FUNCTIONS ---

    window.choose = function choose(option, player) {
        requestedChoices[`${player}Player`] = option;
        if (requestedChoices.leftPlayer && requestedChoices.rightPlayer) {
            socket.send(JSON.stringify({
                type: 'choice_change',
                choices: requestedChoices,
            }));
        }
    }

    window.showPopup = function showPopup(message) {
        popup.textContent = message;
        popup.style.display = "block";
        popupShown = true;
    }

    window.hidePopup = function hidePopup() {
        popup.style.display = "none";
        popupShown = false;
    }

    window.freezeChoice = function freezeChoice(option, player) {
        document.querySelectorAll(`#${player}Player .choices button`).forEach(button => {
            if (button.getAttribute("data-choice") === option) {
                button.style.backgroundColor = "var(--primary-color)";
            } else {
                button.style.backgroundColor = "var(--btn-bg-color)";
            }
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

    socket.onopen = function (event) {
        console.log("Conectado al WebSocket.");
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === 'game_state_update') {
            timerValue.textContent = data.game_state.time_left;
            gameFinished = data.game_state.is_finished;
            freezeChoice(data.game_state.left_choice, 'left');
            freezeChoice(data.game_state.right_choice, 'right');

            if (data.game_state.is_finished && !popupShown) {
                if (data.game_state.winner_username !== "") {
                    showPopup(`${data.game_state.winner_username} gana!`);
                    setTimeout(() => { window.location.hash = "#game" }, 2000);
                } else {
                    showPopup("Empate!");
                }
            } else if (!data.game_state.is_finished && popupShown) {
                hidePopup();
            }

        } else if (data.type === 'initial_information') {
            timerValue.textContent = data.timer_start;
            leftPlayer.id = data.left_player_id;
            leftPlayer.username = data.left_player_username;
            requestedChoices.leftPlayer = data.left_player_choice;
            rightPlayer.id = data.right_player_id;
            rightPlayer.username = data.right_player_username;
            requestedChoices.rightPlayer = data.right_player_choice;
            leftPlayerUsername.textContent = data.left_player_username;
            rightPlayerUsername.textContent = data.right_player_username;
            freezeChoice(data.left_player_choice, 'left');
            freezeChoice(data.right_player_choice, 'right');
        }

    };

    socket.onclose = function (event) {
        console.log("Desconectado del WebSocket.");
    };

    socket.onerror = function (event) {window.location.hash = "#login"
        deleteCookie("accessToken");
        deleteCookie("refreshToken");
        // Refresh the page
        window.location.reload();
    }


    eventManager.addEventListener(title, 'mouseenter', () => {
        title.classList.add('glitch');
        title.style.transform = 'translateY(-5px)';
    });

    eventManager.addEventListener(title, 'mouseleave', () => {
        title.classList.remove('glitch');
        title.style.transform = 'translateY(0)';
    });

    eventManager.addEventListener(document, 'keydown', (event) => {
        if (gameFinished) return;
        if (event.key === 'a') {
            choose('rock', 'left');
        }
        if (event.key === 's') {
            choose('paper', 'left');
        }
        if (event.key === 'd') {
            choose('scissors', 'left');
        }
        if (event.key === 'ArrowLeft') {
            choose('rock', 'right');
        }
        if (event.key === 'ArrowDown') {
            choose('paper', 'right');
        }
        if (event.key === 'ArrowRight') {
            choose('scissors', 'right');
        }
    });


    return () => eventManager.removeAllEventListeners();
}



