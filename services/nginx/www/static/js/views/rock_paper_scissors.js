// static/js/views/rock_paper_scissors.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderRockPaperScissors() {
    const response = await fetch('static/html/rock_paper_scissors.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export function initRockPaperScissors() {

    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();
    let choices = { player1: null, player2: null };
    let timer = 10;
    let interval;

    // --- FUNCTIONS ---

    window.startTimer = function startTimer() {
        interval = setInterval(() => {
            if (timer > 0) {
                document.getElementById("timer").textContent = `Tiempo restante: ${timer}s`;
                timer--;
                highlightRandomChoice(1);
                highlightRandomChoice(2);
            } else {
                clearInterval(interval);
                finalizeChoices();
            }
        }, 1000);
    }

    window.choose = function choose(option, player) {
        choices[`player${player}`] = option;
        document.getElementById(`choice${player}`).textContent = option;
        freezeChoices(player, option);
        checkWinner();
    }

    window.checkWinner = function checkWinner() {
        if (choices.player1 && choices.player2) {
            clearInterval(interval);
            let winner = getWinner(choices.player1, choices.player2);
            showPopup(winner);
            setTimeout(resetGame, 2000);
        }
    }

    window.getWinner = function getWinner(choice1, choice2) {
        if (choice1 === choice2) return "Empate, jueguen de nuevo";
        if (
            (choice1 === "piedra" && choice2 === "tijeras") ||
            (choice1 === "papel" && choice2 === "piedra") ||
            (choice1 === "tijeras" && choice2 === "papel")
        ) {
            return "¡Player1 gana!";
        } else {
            return "¡Player2 gana!";
        }
    }

    window.showPopup = function showPopup(message) {
        let popup = document.getElementById("result-popup");
        popup.textContent = message;
        popup.style.display = "block";
        setTimeout(() => popup.style.display = "none", 2000);
    }

    window.highlightRandomChoice = function highlightRandomChoice(player) {
        if (!choices[`player${player}`]) {
            let buttons = document.querySelectorAll(`#player${player} .choices button`);
            buttons.forEach(btn => btn.style.backgroundColor = "var(--btn-bg-color)");
            let randomButton = buttons[Math.floor(Math.random() * buttons.length)];
            randomButton.style.backgroundColor = "var(--primary-color)";
        }
    }

    window.freezeChoices = function freezeChoices(player, option) {
        document.querySelectorAll(`#player${player} .choices button`).forEach(button => {
            if (button.getAttribute("data-choice") === option) {
                button.style.backgroundColor = "var(--primary-color)";
            } else {
                button.style.backgroundColor = "var(--btn-bg-color)";
            }
        });
    }

    window.finalizeChoices = function finalizeChoices() {
        if (!choices.player1) choose(['piedra', 'papel', 'tijeras'][Math.floor(Math.random() * 3)], 1);
        if (!choices.player2) choose(['piedra', 'papel', 'tijeras'][Math.floor(Math.random() * 3)], 2);
    }

    window.resetGame = function resetGame() {
        choices = { player1: null, player2: null };
        document.getElementById("choice1").textContent = "?";
        document.getElementById("choice2").textContent = "?";
        timer = 10;
        document.getElementById("timer").textContent = "Tiempo restante: 10s";
        startTimer();
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

    startTimer();

    return () => eventManager.removeAllEventListeners();
}
