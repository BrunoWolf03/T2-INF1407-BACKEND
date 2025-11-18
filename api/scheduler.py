from apscheduler.schedulers.background import BackgroundScheduler
from api.services.player_service import PlayerService

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(PlayerService.update_players, "interval", minutes=10)
    scheduler.start()

@app.on_event("startup")
def startup_event():
    from api.scheduler import start_scheduler

    print("🔄 Atualizando base de jogadores no startup...")
    PlayerService.update_players()
    print("⏱ Iniciando scheduler...")
    start_scheduler()
