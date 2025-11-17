import fetch from "node-fetch";
import fs from "fs";

async function sendPlayersToAPI() {
  const data = JSON.parse(fs.readFileSync("./data/players.json"));

  for (const p of data.data) {
    await fetch("http://localhost:8000/players", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: p.id,
        first_name: p.first_name,
        last_name: p.last_name,
        position: p.position,
        team: p.team?.full_name,
      }),
    });

    console.log(`Sent player ${p.first_name}`);
  }
}

sendPlayersToAPI();
