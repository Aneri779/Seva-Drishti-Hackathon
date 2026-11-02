"""
WebSocket endpoint for real-time alerts.
Subscribes to Redis pub/sub channel 'sar_alerts'.
Auth via token query param.
"""
import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_ws, get_redis
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    token: str = "",
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint. Auth: ?token=<access_token>
    Pushes new alert events from Redis pub/sub.
    """
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await websocket.accept()
    logger.info(f"WS connected: user={user.id} role={user.role}")
    
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe("sar_alerts")
    
    try:
        async def listen():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"])
        
        # Ping keepalive every 30s
        async def ping():
            while True:
                await asyncio.sleep(30)
                await websocket.send_json({"type": "ping"})
        
        await asyncio.gather(listen(), ping())
    
    except WebSocketDisconnect:
        logger.info(f"WS disconnected: user={user.id}")
    except Exception as e:
        logger.error(f"WS error: {e}")
    finally:
        await pubsub.unsubscribe("sar_alerts")
        await pubsub.close()

