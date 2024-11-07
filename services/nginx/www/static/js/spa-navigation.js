// static/js/spa-navigation.js

// Maybe this is not necessary  because the code is already in the SPA? SOLVE LATER
import { renderHome, initHome } from './views/home.js';
// import { renderAbout, initAbout } from './views/about.js';
import { renderRegister, initRegister } from './views/register.js';
import { renderLogin, initLogin } from './views/login.js';
import { renderGame, initGame } from './views/game.js';
import { renderWebsocket, initWebsocket } from './views/websocket.js';
// import { renderTorneo, initTorneo } from './views/torneo.js';

/**
 * Container for possible routes of the SPA. Works as a pointer
 * of functions to render and initialize each section.
*/
const routes = {
    "/index": { render: renderHome, init: initHome },
    // "/about": { render: renderAbout, init: initAbout },
    "/register": { render: renderRegister, init: initRegister },
    "/login": { render: renderLogin, init: initLogin },
    "/game": { render: renderGame, init: initGame },
	"/websocket": { render: renderWebsocket, init: initWebsocket },
    // "/torneo": { render: renderTorneo, init: initTorneo },
};

function router() {
    const path = location.hash.slice(1) || "/index";
    const route = routes[path];

    if (route) {
        // Carga el contenido en #main-content
        document.getElementById("main-content").innerHTML = route.render();
        
        // Ejecuta la lógica de inicialización de la sección
        route.init();
    } else {
        document.getElementById("main-content").innerHTML = "<h2>404</h2><p>NOT FOUND 42</p>";
    }
}

// Escucha cambios en el hash y carga el contenido adecuado
window.addEventListener("hashchange", router);
window.addEventListener("load", router);
