import axios from "axios";

const BACKEND_URL = "http://localhost:8000/api";

// --- Fórmula de fantasy ---
function calcFantasy(stats) {
    return (
        stats.points * 1 +
        stats.totReb * 1.2 +
        stats.assists * 1.5 +
        stats.steals * 3 +
        stats.blocks * 3 +
        stats.turnovers * -1
    );
}


async function getTodayDate() {
    const today = await axios.get("https://data.nba.net/prod/v1/today.json");
    return today.data.today; // formato YYYYMMDD
}


async function getGames(date) {
    const url = `https://data.nba.net/prod/v1/${date}/scoreboard.json`;
    const scoreboard = await axios.get(url);
    return scoreboard.data.games || [];
}


async function getBoxscore(date, gameId) {
    const url = `https://data.nba.net/prod/v1/${date}/${gameId}_boxscore.json`;
    const box = await axios.get(url);
    return box.data.stats?.activePlayers || [];
}

async function updateBackend(playerName, points) {
    try {
        await axios.post(`${BACKEND_URL}/update-player-points/`, {
            name: playerName,
            fantasy_points: points
        });
    } catch (err) {
        console.log("❌ Erro ao atualizar", playerName);
    }
}

async function run() {
    const date = await getTodayDate();
    console.log(" Data da NBA:", date);

    const games = await getGames(date);
    console.log(` ${games.length} jogos encontrados.`);

    const updated = [];

    for (const game of games) {
        const players = await getBoxscore(date, game.gameId);

        for (const p of players) {
            const playerName =
                `${p.firstName} ${p.lastName}`.trim();

            const playerStats = {
                points: p.points || 0,
                totReb: p.totReb || 0,
                assists: p.assists || 0,
                steals: p.steals || 0,
                blocks: p.blocks || 0,
                turnovers: p.turnovers || 0,
            };

            const fantasy = calcFantasy(playerStats);

            console.log(`→ ${playerName}: ${fantasy.toFixed(2)}`);

            await updateBackend(playerName, fantasy);

            updated.push({ name: playerName, fantasy_points: fantasy });
        }
    }


    console.log(JSON.stringify({ updated }, null, 2));
}

run();
