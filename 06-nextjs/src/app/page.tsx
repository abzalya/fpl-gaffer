//Main Page of FPL Gaffer
//Version: 1.0.0

import {getNextGameweek, getPlayers} from "@/lib/api";
import OptimizeForm from "@/components/OptimizeForm";

export default async function Home() {  
  const gameweek = await getNextGameweek();
  
  const players = await getPlayers();


  return (
    <main>
      <div> {gameweek.name} </div>
      <div> {players.length} </div>
      <OptimizeForm players={players} />
    </main>
  );
}
