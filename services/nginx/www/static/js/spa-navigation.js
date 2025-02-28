// static/js/spa-navigation.js

// Maybe this is not necessary  because the code is already in the SPA? SOLVE LATER
import { renderHome, initHome } from './views/home.js';
// import { renderAbout, initAbout } from './views/about.js';
import { renderRegister, initRegister } from './views/register.js';
import { renderLogin, initLogin } from './views/login.js';
import { renderGame, initGame } from './views/game.js';
import { renderWebsocket, initWebsocket } from './views/websocket.js';
import { renderTournament, initTournament } from './views/tournament.js';
import { renderTournamentRoom, initTournamentRoom } from './views/tournamentRoom.js';
import { renderVersusWait, initVersusWait } from './views/versusWait.js';
import { renderNewTournamentRoom, initNewTournamentRoom } from './views/newTournamentRoom.js';
import { renderTournamentsList, initTournamentsList } from './views/tournamentsList.js';
import { renderNewLogin, initNewLogin } from './views/newLogin.js';
import { renderRockPaperScissors, initRockPaperScissors } from './views/rockPaperScissors.js';
import { render2FA, init2FA } from './views/2FA.js';



/**
 * Container for possible routes of the SPA. Works as a pointer
 * of functions to render and initialize each section.
*/

const routes = {
    "/index": { render: renderHome, init: initHome },
    "/register": { render: renderRegister, init: initRegister },
    "/login": { render: renderLogin, init: initLogin },
    "/game": { render: renderGame, init: initGame },
    "/websocket": { render: renderWebsocket, init: initWebsocket },
    "/tournament": { render: renderTournament, init: initTournament },
    "/tournament/room/:id": { render: renderTournamentRoom, init: initTournamentRoom },
    "/versus-wait": { render: renderVersusWait, init: initVersusWait },
    "/tournaments-list": { render: renderTournamentsList, init: initTournamentsList },
    "/new-tournament-room": { render: renderNewTournamentRoom, init: initNewTournamentRoom },
    "/new-login": { render: renderNewLogin, init: initNewLogin },
    "/rock-paper-scissors": { render: renderRockPaperScissors, init: initRockPaperScissors },
    "/2FA": { render: render2FA, init: init2FA },
};

function parseRoute(path) {
    // Asegurarnos de que el path tiene la barra inicial
    path = path.startsWith("/") ? path : "/" + path;
    
    const routeKeys = Object.keys(routes);
    for (const key of routeKeys) {
        // Buscar rutas con parámetros dinámicos, como ":id"
        const paramMatch = key.match(/:([^\/]+)/);
        if (paramMatch) {
            const paramKey = paramMatch[1];
            const basePath = key.split("/:")[0]; // Base path sin el parámetro dinámico

            if (path.startsWith(basePath)) {
                // Extraer el valor del parámetro de la URL
                const paramValue = path.slice(basePath.length + 1); // El valor después de "/tournament/room/"

                // Aquí tratamos de devolver el objeto de ruta con el parámetro dinámico
                return { route: routes[key], params: { [paramKey]: paramValue } };
            } else {
                console.log("No match for path:", path);
            }
        }
    }
    // Si no es una ruta dinámica, devolver la ruta directamente
    return { route: routes[path], params: {} };
}

async function router() {
    const path = location.hash.slice(1) || "/index";
    const { route, params } = parseRoute(path);
    console.log("Ruta:", route, "Parámetros:", params.id);

    let currentCleanup;

    if (route) {
        // Limpiar la ruta anterior si existe
        if (currentCleanup) {
            currentCleanup();
        }

        // Renderiza e inicializa la ruta, pasando los parámetros si existen
        document.getElementById("main-content").innerHTML = await route.render(params);
        currentCleanup = route.init(params);
    } else {
        document.getElementById("main-content").innerHTML = "<h2>404</h2><p>NOT FOUND</p>";
    }
}

// Escucha cambios en el hash y carga el contenido adecuado
window.addEventListener("hashchange", router);
window.addEventListener("load", router);
