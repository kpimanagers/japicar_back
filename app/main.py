import sys
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi_pagination import add_pagination
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from .API.v1.middlewares.verify_token import verify_token
from .API.v1.services.upload_file import upload_file as upload_file_bucket
from .config.socket_config import ws_manager


from .config import config
from .API.v1 import v1_router

from .cron_jobs import task_12_am

CHILE_TZ = timezone('America/Santiago')

app = FastAPI(tittle="japiCar Backend", description="japiCar Backend", version="1.0.0")


prefix = "/api/v1"


# Configura y programa el cron job
def start_scheduler():
    scheduler = BackgroundScheduler(timezone=CHILE_TZ)
    scheduler.add_job(lambda: asyncio.run(task_12_am()), 'cron', hour=0, minute=0)  # 12:00 AM todos los días
    scheduler.start()

# Iniciar el scheduler al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    start_scheduler()
    print("Scheduler iniciado")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.CLIENT_DOMAIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Main"])

@app.post(f"{prefix}/upload-file", tags=["Main"], dependencies=[Depends(verify_token)])
async def upload_file(files: List[UploadFile] = File(...)):
    
    try:
        results = []
        for file in files:
            file_url = await upload_file_bucket(file, folder_name='japicar-files')
            results.append(file_url)
        

        return results
    except Exception as err:
        print("Error in line:", sys.exc_info()[-1].tb_lineno)
        print("Error message : {0}".format(err))
        raise HTTPException(400, 'Error al agregar las imágenes')

def main():
    return {"message": "japiCar Backend"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('accepted connection')
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("Client disconnected")


app.include_router(v1_router, prefix=prefix)
add_pagination(app)



