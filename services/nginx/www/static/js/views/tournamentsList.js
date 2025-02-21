// static/js/views/tournaments_list.js

import EventListenerManager from '../utils/eventListenerManager.js';

export async function renderTournamentsList() {
    const response = await fetch('static/html/tournaments_list.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export function initTournamentsList() {

    // --- VARIABLES AND CONSTANTS ---

    const eventManager = new EventListenerManager();

    const availableGames = [
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 5 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 2 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
        { name: 'TOR-A', date: '01/02/2025 18:42', users: 6 },
    ];

       
    // --- DOM ELEMENTS ---
    
    
    const gameLists = document.querySelectorAll('.game-list');
    const title = document.querySelector('.site-title');
    

    // --- FUNCTIONS ---

    window.createGameItem = function createGameItem(game, type) {
        const gameItem = document.createElement('div');
        gameItem.classList.add('game-item');

        gameItem.innerHTML = `
            <div class="game-info">
                <div class="game-name">${game.name}</div>
                <div class="game-meta">Usuarios conectados: ${game.users}</div>
                <div class="game-meta">Fecha de creación: ${game.date}</div>
            </div>
            <button class="btn">${type === 'available' ? 'Unirse' : 'Visualizar'}</button>
        `;
        return gameItem;
    }

    window.displayGames = function displayGames() {
        const availableContainer = document.getElementById('available-games');

        availableGames.forEach(game => {
            const gameItem = createGameItem(game, 'available');
            availableContainer.appendChild(gameItem);
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

    gameLists.forEach(gameList => {
        let isMouseDown = false;
        let startX;
        let scrollLeft;

        eventManager.addEventListener(gameList, 'mousedown', (e) => {
            isMouseDown = true;
            startX = e.pageX - gameList.offsetLeft;
            scrollLeft = gameList.scrollLeft;
            gameList.style.cursor = 'grabbing';
        });

        eventManager.addEventListener(gameList, 'mouseleave', () => {
            isMouseDown = false;
            gameList.style.cursor = 'grab';
        });

        eventManager.addEventListener(gameList, 'mouseup', () => {
            isMouseDown = false;
            gameList.style.cursor = 'grab';
        });

        eventManager.addEventListener(gameList, 'mousemove', (e) => {
            if (!isMouseDown) return;
            e.preventDefault();
            const x = e.pageX - gameList.offsetLeft;
            const walk = (x - startX) * 3; // Controlar la velocidad del desplazamiento
            gameList.scrollLeft = scrollLeft - walk;
        });
    });

    eventManager.addEventListener(title, 'mouseenter', () => {
        title.classList.add('glitch');
        title.style.transform = 'translateY(-5px)';
    });

    eventManager.addEventListener(title, 'mouseleave', () => {
        title.classList.remove('glitch');
        title.style.transform = 'translateY(0)';
    });

    // --- INITIALIZATION ---

    displayGames();


    return () => eventManager.removeAllEventListeners();
}
