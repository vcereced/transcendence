// static/js/views/home.js
import { showUsername, showPicture, updateUsername, updatePassword, updatePicture } from './settings.js';
import { checkActiveGame } from '../utils/autoReconnect.js';
import { hasAccessToken } from '../utils/auth_management.js';
import { handleJwtToken } from './jwtValidator.js';

export async function renderHome() {
    const response = await fetch('static/html/home.html');
    const htmlContent = await response.text();
    return htmlContent;
}

export async function initHome() {

    // --- VARIABLES AND CONSTANTS ---

    

    const totalCards = 4;
    const angleStep = 360 / totalCards;
    let currentAngle = 0;
    let isDragging = false;
    let startX = 0;

    const players = [
        { username: "javiersa", avatar: "../../media/2.gif" },
        { username: "f-gomez", avatar: "../../media/3.gif" },
        { username: "vcered", avatar: "../../media/4.gif" },
        { username: "dgarizard", avatar: "../../media/5.gif" },
        { username: "messi", avatar: "../../media/1.gif" },
        { username: "cristiano", avatar: "../../media/3.gif" },
        { username: "neymar123", avatar: "../../media/2.gif" },
        { username: "lewandosk", avatar: "../../media/5.gif" },
        { username: "javiersa", avatar: "../../media/2.gif" },
        { username: "f-gomez", avatar: "../../media/3.gif" },
        { username: "vcered", avatar: "../../media/4.gif" },
        { username: "dgarizard", avatar: "../../media/5.gif" },
        { username: "messi", avatar: "../../media/1.gif" },
        { username: "cristiano", avatar: "../../media/3.gif" },
        { username: "neymar123", avatar: "../../media/2.gif" },
        { username: "lewandosk", avatar: "../../media/5.gif" },
    ];

    // --- DOM ELEMENTS ---

    const carousel = document.getElementById("carousel");
    const title = document.querySelector('.site-title');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const histories = document.querySelectorAll('.history');
    const profilePopup = document.getElementById('profilePopup');
    const settingsPopup = document.getElementById('settingsPopup');
    const homeDiv = document.getElementsByClassName('home')[0];
    // --- FUNCTIONS ---

    window.toggleFullscreen = function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    window.toggleMenu = function toggleMenu(event) {
        event.stopPropagation();
        const dropdownMenu = document.getElementById("dropdownMenu");
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
    }

    window.buttonHold = function buttonHold(button, gameType) {
        button.style.boxShadow = `0 0 30px var(--hover-shadow-color)`;
        button.innerText = `${gameType}`;
    }

    window.buttonRelease = function buttonRelease(button, gameType) {
        button.style.boxShadow = `0 0 20px var(--shadow-color)`;
        button.innerText = `${gameType}`;
    }

    window.toggleSearch = function toggleSearch() {
        const searchIcon = document.querySelector('.search-icon');
        const searchBar = document.getElementById('searchBar');
        const playerList = document.getElementById('playerList');

        searchIcon.style.display = 'none';
        searchBar.classList.add('active');
        searchBar.focus();
        playerList.style.display = 'block';
        updatePlayerList('');
    }

    window.updatePlayerList = function updatePlayerList(query) {
        const playerList = document.getElementById('playerList');
        playerList.innerHTML = '';

        const filteredPlayers = players.filter(player =>
            player.username.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);

        filteredPlayers.forEach(player => {
            const li = document.createElement('li');
            li.classList.add('player-item');
            li.innerHTML = `<img src="${player.avatar}" alt="Avatar"> ${player.username}`;
            playerList.appendChild(li);
        });
    }

    window.openProfilePopup = function openProfilePopup() {
        profilePopup.style.display = 'flex';
    }

    window.closeProfilePopup = function closeProfilePopup() {
        profilePopup.style.display = 'none';
    }

    window.openSettingsPopup =  function openSettingsPopup() {
        let email = sessionStorage.getItem("email");
        showPicture(email);
        showUsername(email);
        
        document.querySelectorAll(".preset-img").forEach(img => {
            img.addEventListener("click", async () => {
                const src = img.src
                document.getElementById("current-profile-pic").src = src;
            });
        })
        document.getElementById("save-btn-images").addEventListener("click", async () => {
            const src =  document.getElementById("current-profile-pic").src;
            updatePicture(email, src);
            window.closeSettingsPopup();
        });


        document.getElementById("save-btn-name").addEventListener("click", () => {
            const newUsername = document.getElementById("username").value;
            const email = sessionStorage.getItem("email");

            updateUsername(email, newUsername);
        });

        document.getElementById("save-btn-password").addEventListener("click", () => {
            const oldPass = document.getElementById("old-password").value;
            const newPass1 = document.getElementById("new-password1").value;
            const newPass2 = document.getElementById("new-password2").value;
            const email = sessionStorage.getItem("email");

            updatePassword(email, oldPass, newPass1, newPass2);
        });

        document.getElementById('settingsPopup').style.display = 'flex';
    }

    window.closeSettingsPopup = function closeSettingsPopup() {
        settingsPopup.style.display = 'none';
    }

    window.toggleSettingsFields = function toggleSettingsFields() {
        let selectedOption = document.getElementById("settings-option").value;
        let fields = ["profile-pic-field", "username-field", "password-field"];

        fields.forEach(field => {
            document.getElementById(field).style.display = "none";
        });

        if (selectedOption !== "none") {
            document.getElementById(selectedOption + "-field").style.display = "block";
        }
    }

    window.createLocalGame = function createLocalGame(type) {
        checkActiveGame(document, homeDiv);
        // Check active games, if active, show popup explaining and redirect
        // Make POST call to /api/game/create/ with type of game to be created (player, computer)
        fetch('/api/game/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "type": type })
        })
            .then(response => {
                if (!response.ok) {
                    console.error(response);
                    return;
                }
                window.location.hash = "#rock-paper-scissors";
            })
            .catch(error => {
                console.error(error);
            });

        // If success, show popup of redirecting to created game
    }


window.toggleFriendStatus = function toggleFriendStatus() {
    var btn = document.getElementById("add-friend-btn");
    if (btn.innerHTML === "Añadir Amigo") {
        btn.innerHTML = "Amigo";
        btn.style.backgroundColor = "var(--primary-color)";
        btn.style.color = "white";
    } else {
        btn.innerHTML = "Añadir Amigo";
        btn.style.backgroundColor = "#f5f5f5";
        btn.style.color = "#333";
    }
};

    
    window.updateStatus = function updateStatus(isOnline) {
        var statusCircle = document.getElementById("status-circle");
        if (isOnline) {
            statusCircle.style.backgroundColor = "var(--primary-color)";
        } else {
            statusCircle.style.backgroundColor =  "var(--btn-bg-color)";
        }
    }

    // --- EVENT LISTENERS ---

    window.eventManager.addEventListener(carousel, 'mousedown', (e) => {
        isDragging = true;
        startX = e.clientX;
    });

    window.eventManager.addEventListener(window, 'mouseup', () => {
        if (isDragging) {
            const rotation = Math.round(currentAngle / angleStep) * angleStep;
            currentAngle = rotation;
            carousel.style.transform = `rotateY(${currentAngle}deg)`;
        }
        isDragging = false;
    });

    window.eventManager.addEventListener(window, 'mousemove', (e) => {
        if (isDragging) {
            const dx = startX - e.clientX;
            currentAngle -= dx * 0.5;
            carousel.style.transform = `rotateY(${currentAngle}deg)`;
            startX = e.clientX;
        }
    });

    window.eventManager.addEventListener(window, 'keydown', (e) => {
        if (e.key === "ArrowLeft") {
            currentAngle += angleStep;
            carousel.style.transform = `rotateY(${currentAngle}deg)`;
        } else if (e.key === "ArrowRight") {
            currentAngle -= angleStep;
            carousel.style.transform = `rotateY(${currentAngle}deg)`;
        }
    });

    window.eventManager.addEventListener(document, "click", function () {
        const dropdownMenu = document.getElementById("dropdownMenu");
        dropdownMenu.style.display = "none";
    });

    window.eventManager.addEventListener(document.getElementById('searchBar'), 'input', function () {
        updatePlayerList(this.value);
    });

    window.eventManager.addEventListener(document, 'click', function (e) {
        const searchBar = document.getElementById('searchBar');
        const searchIcon = document.querySelector('.search-icon');
        const playerList = document.getElementById('playerList');

        if (!searchBar.contains(e.target) && !searchIcon.contains(e.target)) {
            searchBar.classList.remove('active');
            searchIcon.style.display = 'block';
            playerList.style.display = 'none';
        }
    });

    window.eventManager.addEventListener(document, 'keydown', function (e) {
        if (e.key === 'Escape') {
            const searchBar = document.getElementById('searchBar');
            const searchIcon = document.querySelector('.search-icon');
            const playerList = document.getElementById('playerList');

            searchBar.classList.remove('active');
            searchIcon.style.display = 'block';
            playerList.style.display = 'none';
        }
    });

    window.eventManager.addEventListener(document.getElementById('profilePopup'), 'click', function (event) {
        if (!event.target.closest('.profile-container')) {
            closeProfilePopup();
        }
    });

    window.eventManager.addEventListener(document.getElementById('settingsPopup'), 'click', function (event) {
        if (!event.target.closest('.settings-container')) {
            closeSettingsPopup();
        }
    });

    

    window.eventManager.addEventListener(title, 'mouseenter', () => {
        title.classList.add('glitch');
        title.style.transform = 'translateY(-5px)';
    });

    window.eventManager.addEventListener(title, 'mouseleave', () => {
        title.classList.remove('glitch');
        title.style.transform = 'translateY(0)';
    });

    

    tabButtons.forEach(button => {
        window.eventManager.addEventListener(button, 'click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            histories.forEach(history => history.style.display = 'none');
            const target = button.getAttribute('data-tab');
            document.getElementById(target).style.display = 'block';
        });
    });


    // --- INITIALIZATION ---

    if (!hasAccessToken()) {
        window.sessionStorage.setItem("afterLoginRedirect", "#");
        window.location.hash = "#new-login"
    }
    handleJwtToken();

    await checkActiveGame(document, homeDiv);
}
