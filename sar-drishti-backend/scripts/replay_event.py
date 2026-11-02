"""
Replay a real historical SAR event end-to-end.
Usage:
  python scripts/replay_event.py --event biparjoy_2023
  python scripts/replay_event.py --event tauktae_2021
  python scripts/replay_event.py --event aug2024_floods

All events use REAL Sentinel-1 scenes from GEE.
Labels them REPLAY with acquisition date.
"""
import sys
import argparse
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EVENTS = {
    "biparjoy_2023": {
        "name": "Cyclone Biparjoy Jun 2023",
        "date_start": "2023-06-13",
        "date_end": "2023-06-20",
        "aoi": [68.0, 20.0, 74.5, 24.5],
        "description": "Severe cyclonic storm made landfall near Mandvi (Kutch) on June 15 2023",
    },
    "tauktae_2021": {
        "name": "Cyclone Tauktae May 2021",
        "date_start": "2021-05-17",
        "date_end": "2021-05-20",
        "aoi": [68.0, 20.0, 74.5, 24.5],
        "description": "Extremely severe cyclonic storm; Gujarat coastline severely affected",
    },
    "aug2024_floods": {
        "name": "Gujarat Monsoon Floods Aug 2024",
        "date_start": "2024-08-25",
        "date_end": "2024-09-05",
        "aoi": [68.0, 20.0, 74.5, 24.5],
        "description": "Heavy monsoon flooding across Saurashtra, South Gujarat districts",
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, choices=list(EVENTS.keys()))
    parser.add_argument("--dry-run", action="store_true", help="Query GEE only, don't write to DB")
    args = parser.parse_args()
    
    event = EVENTS[args.event]
    logger.info(f"Replaying: {event['name']}")
    logger.info(f"Period: {event['date_start']} to {event['date_end']}")
    logger.info(f"Description: {event['description']}")
    
    # Initialize GEE
    import ee
    import json
    import os
    
    key_file = os.environ.get("GEE_KEY_FILE", "secrets/gee-key.json")
    with open(key_file) as f:
        key_data = json.load(f)
    email = key_data["client_email"]
    ee.Initialize(ee.ServiceAccountCredentials(email, key_file),
                  project=os.environ.get("GEE_PROJECT", "sar-drishti-gujarat-123456"))
    
    logger.info("GEE initialized")
    
    # Query scenes for event period
    aoi = ee.Geometry.Rectangle(event["aoi"])
    col = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(event["date_start"], event["date_end"])
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
        .filter(ee.Filter.eq("instrumentMode", "IW"))
    )
    
    count = col.size().getInfo()
    logger.info(f"Found {count} S1 scenes for {event['name']}")
    
    if count == 0:
        logger.error("No scenes found. Check event dates and GEE collection.")
        sys.exit(1)
    
    images = col.sort("system:time_start").toList(count).getInfo()
    
    for img_info in images:
        props = img_info["properties"]
        s1_id = img_info["id"]
        acq_ts = props.get("system:time_start", 0)
        acq_dt = datetime.fromtimestamp(acq_ts / 1000, tz=timezone.utc)
        rel_orbit = props.get("relativeOrbitNumber_start")
        pass_dir = props.get("orbitProperties_pass")
        logger.info(f"  Scene: {s1_id} | {acq_dt.strftime('%Y-%m-%d %H:%M UTC')} | orbit={rel_orbit} {pass_dir}")
    
    if args.dry_run:
        logger.info("DRY RUN — no DB writes.")
        return
    
    # Insert scenes as queued REPLAY entries
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.all_models import SARScene
    
    db_url = os.environ.get("DATABASE_SYNC_URL") or os.environ.get("DATABASE_URL", "").replace(
        "postgresql+asyncpg", "postgresql+psycopg2"
    )
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        new_count = 0
        for img_info in images:
            props = img_info["properties"]
            s1_id = img_info["id"]
            acq_ts = props.get("system:time_start", 0)
            acq_dt = datetime.fromtimestamp(acq_ts / 1000, tz=timezone.utc)
            
            from sqlalchemy import select
            existing = db.query(SARScene).filter_by(s1_id=s1_id).first()
            if not existing:
                scene = SARScene(
                    s1_id=s1_id,
                    rel_orbit=props.get("relativeOrbitNumber_start", 0),
                    pass_dir=props.get("orbitProperties_pass", "ASCENDING"),
                    acquired_at=acq_dt,
                    status="queued",
                    is_replay=True,
                    replay_event_name=event["name"],
                )
                db.add(scene)
                db.flush()
                
                # Trigger Celery processing
                from app.sar.pipeline import process_scene
                process_scene.delay(scene.id)
                new_count += 1
                logger.info(f"  Queued for processing: {s1_id} (scene_id={scene.id})")
        
        db.commit()
        logger.info(f"Replay enqueued: {new_count} new scenes for {event['name']}")
        logger.info("Monitor progress in Celery worker logs or /health/deep")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

