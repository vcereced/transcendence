// static/js/views/HistoryBlockchain.js

import { handleJwtToken } from './jwtValidator.js';

export async function renderHistoryBlockchain() {
    const response = await fetch('static/html/blockchain.html'); // Asegúrate de que el nombre del archivo sea correcto
    const htmlContent = await response.text();
    return htmlContent;
}

export function initHistoryBlockchain() {
    console.log('HistoryBlockchain view initialized');
    loadBlockchainTournaments();
}

async function loadBlockchainTournaments() {
    const tournamentsContainer = document.getElementById('blockchain-tournaments-list'); // Debe coincidir con el ID en history_blockchain.html

    if (!tournamentsContainer) {
        console.error('Error: El contenedor para la lista de torneos de blockchain no se encontró en el DOM.');
        return;
    }

    tournamentsContainer.innerHTML = '<p>Cargando torneos de la blockchain...</p>';

    try {
        await handleJwtToken();

        const responseIds = await fetch('/api/blockchain/get_tournaments_ids');
        if (!responseIds.ok) {
            throw new Error(`Error al obtener los IDs de los torneos: ${responseIds.status}`);
        }
        const dataIds = await responseIds.json();
        const tournamentIds = dataIds.tournament_ids || [];

        if (tournamentIds.length === 0) {
            tournamentsContainer.innerHTML = '<p>No se encontraron torneos registrados en la blockchain.</p>';
            return;
        }

        let tournamentsHTML = '';
        for (const id of tournamentIds) {
            const responseDetails = await fetch(`/api/blockchain/get_tournament/${id}`);
            if (!responseDetails.ok) {
                console.warn(`Error al obtener detalles del torneo con ID ${id}: ${responseDetails.status}`);
                continue;
            }
            const details = await responseDetails.json();
            tournamentsHTML += renderTournamentItem(details);
        }

        tournamentsContainer.innerHTML = tournamentsHTML;

    } catch (error) {
        console.error('Error al cargar los torneos de la blockchain:', error);
        tournamentsContainer.innerHTML = '<p>Error al cargar los torneos de la blockchain. Inténtelo más tarde.</p>';
    }
}

function renderTournamentItem(tournament) {
    return `
        <div class="game-item">
            <div class="game-info">
            <div class="game-name">${tournament.name}</div>
            <div class="game-meta">Id: ${tournament.id}</div>
                <div class="game-meta">Ganador: ${tournament.winner || 'N/A'}</div>
                <div class="game-meta">Hash: ${tournament.treeHash}</div>
                <div class="game-meta">Fecha de registro: ${new Date(tournament.registeredAt * 1000).toLocaleString('es-ES')}</div>
            </div>
            <!-- <button class="btn" >Finalizado</button> -->
            </div>
    `;
}