import fetch from "node-fetch";
import fs from "fs";

async function fetchPlayers() {
  const res = await fetch("https://api.balldontlie.io/v1/players");
  const data = await res.json();

  fs.writeFileSync("./data/players.json", JSON.stringify(data, null, 2));
  console.log("Players saved to file");
}

fetchPlayers();
