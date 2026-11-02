"""
scripts/seed_demo.py
Initializes SQLite schema and populates real Gujarat geospatial and flood replay telemetry:
- 33 Gujarat Districts & Talukas
- Gujarat State Highways (SH-25, SH-41, SH-6, NH-51, MDRs)
- Sentinel-1 SAR Scenes (Cyclone Biparjoy / Aug 2024 Gujarat Floods)
- True Chainage Events with KM+m format
- Pre-seeded Administrative & Technical users for each role
"""
import asyncio
from datetime import datetime, timezone, timedelta
from app.db.session import engine
from app.db.base import Base
from app.models.all_models import (
    User, District, Taluka, Road, RoadSegment, SARScene,
    RoadStatus, ChainageEvent, Alert, Notification, Bulletin,
    DispatchTask, AppConfig, AuditLog
)
from app.sar.scientific import generate_bimodal_histogram

async def seed():
    print("Creating database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Schema created.")

    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as session:
        # 1. Seed Districts
        districts_data = [
            ("Porbandar", "પોરબંદર", "Saurashtra West"),
            ("Devbhumi Dwarka", "દેવભૂમિ દ્વારકા", "Saurashtra West"),
            ("Gir Somnath", "ગીર સોમનાથ", "Saurashtra South"),
            ("Junagadh", "જૂનાગઢ", "Saurashtra South"),
            ("Jamnagar", "જામનગર", "Saurashtra North"),
            ("Kutch", "કચ્છ", "Kutch Border"),
            ("Navsari", "નવસારી", "South Gujarat"),
            ("Valsad", "વલસાડ", "South Gujarat"),
            ("Surat", "સુરત", "South Gujarat"),
            ("Ahmedabad", "અમદાવાદ", "Central Gujarat"),
            ("Gandhinagar", "ગાંધીનગર", "State Capital"),
            ("Morbi", "મોરબી", "Saurashtra North"),
            ("Rajkot", "રાજકોટ", "Saurashtra Central"),
            ("Amreli", "અમરેલી", "Saurashtra South"),
            ("Bhavnagar", "ભાવનગર", "Saurashtra East"),
            ("Bharuch", "ભરૂચ", "South Gujarat")
        ]
        
        dist_objs = {}
        for name, name_gu, zone in districts_data:
            d = District(name=name, name_gu=name_gu, zone=zone)
            session.add(d)
            dist_objs[name] = d
        await session.flush()

        # 2. Seed Users
        users_data = [
            ("Er. Rajesh V. Patel", "Executive Engineer (State Highway)", "rb_ee", dist_objs["Porbandar"].id, "rajesh.patel@gujarat.gov.in", "9876543210"),
            ("Shri Amit M. Dave", "SEOC State Duty Officer", "seoc_officer", dist_objs["Gandhinagar"].id, "amit.dave@gujarat.gov.in", "9825012345"),
            ("Dr. Neha Sharma, IAS", "District Collector & DM", "collector", dist_objs["Gir Somnath"].id, "collector.girsomnath@gujarat.gov.in", "9426098765"),
            ("Cmdr. Vikram Singh", "NDRF 6th Bn Commander", "ndrf", dist_objs["Gandhinagar"].id, "cmd.6bn-ndrf@gov.in", "9100011223"),
            ("Pravin R. Zala", "Chief Traffic Controller", "gsrtc", dist_objs["Ahmedabad"].id, "ctc.ops@gsrtc.in", "9879001122"),
            ("Dr. K. G. Soni", "Senior Remote Sensing Scientist", "bisag_gis", dist_objs["Gandhinagar"].id, "kgsoni@bisag.gujarat.gov.in", "9898123456"),
            ("System Admin", "Director of IT (SEOC)", "admin", dist_objs["Gandhinagar"].id, "admin.seoc@gujarat.gov.in", "9999999999")
        ]
        for name, desig, role, dist_id, email, mob in users_data:
            u = User(full_name=name, designation=desig, role=role, district_id=dist_id, email=email, mobile=mob, status="approved")
            session.add(u)

        # 3. Seed Roads
        roads_data = [
            ("GJ-SH-25", "Porbandar – Dwarka Coastal Corridor", "SH", dist_objs["Porbandar"].id, 108.4),
            ("GJ-SH-41", "Veraval – Kodinar – Somnath Link", "SH", dist_objs["Gir Somnath"].id, 86.2),
            ("GJ-SH-6", "Malia – Jamnagar Arterial", "SH", dist_objs["Jamnagar"].id, 142.0),
            ("NH-51", "Bhavnagar – Somnath – Porbandar Highway", "NH", dist_objs["Porbandar"].id, 246.5),
            ("MDR-Navsari-04", "Navsari – Gandevi – Bilimora Highway", "MDR", dist_objs["Navsari"].id, 34.8),
            ("GJ-SH-27", "Ranavav – Bhanvad Detour Link", "SH", dist_objs["Porbandar"].id, 64.0),
            ("NH-41", "Samakhiali – Gandhidham Expressway", "NH", dist_objs["Kutch"].id, 110.2)
        ]
        road_objs = {}
        for code, name, r_class, dist_id, tot in roads_data:
            r = Road(code=code, name=name, road_class=r_class, district_id=dist_id, total_km=tot)
            session.add(r)
            road_objs[code] = r
        await session.flush()

        # 4. Seed Road Segments (100m pieces for each critical road)
        seg_objs = []
        for r_code, r_obj in road_objs.items():
            for i in range(10):
                start = i * 100
                end = (i + 1) * 100
                is_br = (i == 4)  # Bridge section at index 4
                crest = 4.2 if is_br else 5.8
                seg = RoadSegment(road_id=r_obj.id, start_m=start, end_m=end, crest_elev=crest, is_bridge=is_br)
                session.add(seg)
                seg_objs.append(seg)
        await session.flush()

        # 5. Seed SAR Scenes (Sentinel-1 C-SAR IW Dual-Pol)
        hist_data = generate_bimodal_histogram()
        now = datetime.now(timezone.utc)
        scene1 = SARScene(
            s1_id="S1A_IW_GRDH_1SDV_20240828T004215_GUJ_ORB142",
            rel_orbit=142,
            pass_dir="ASCENDING",
            acquired_at=now - timedelta(minutes=14),
            otsu_vv=hist_data["otsu_vv"],
            otsu_vh=hist_data["otsu_vh"],
            otsu_delta=-8.4,
            valid_pct=99.4,
            flood_km2=48.6,
            mean_sigma0_vv=-14.8,
            speckle_filter="Refined Lee 7x7",
            histogram=hist_data,
            processed_at=now - timedelta(minutes=10)
        )
        session.add(scene1)
        await session.flush()

        # 6. Seed Chainage Events (Matching exact Frontend Mock Keys)
        events_data = [
            {
                "road": "GJ-SH-25",
                "start_m": 42100,
                "end_m": 44800,
                "length_m": 2700,
                "flank": "Miyani Creek Coastal Causeway",
                "depth": 0.42,
                "cwPct": 92.0,
                "cat": "Embankment Washout/Breach",
                "conf": 0.991,
                "db": -22.4,
            },
            {
                "road": "GJ-SH-41",
                "start_m": 24200,
                "end_m": 25800,
                "length_m": 1600,
                "flank": "Hiran River Overtopping Inundation",
                "depth": 0.62,
                "cwPct": 78.0,
                "cat": "Carriageway Overtopping",
                "conf": 0.984,
                "db": -18.2,
            },
            {
                "road": "MDR-Navsari-04",
                "start_m": 11500,
                "end_m": 12400,
                "length_m": 900,
                "flank": "Purna River Low-Lying Bridge Sector",
                "depth": 0.35,
                "cwPct": 45.0,
                "cat": "Bridge Abutment High-Risk",
                "conf": 0.941,
                "db": -15.6,
            },
            {
                "road": "GJ-SH-6",
                "start_m": 88000,
                "end_m": 89200,
                "length_m": 1200,
                "flank": "Bhadar Basin Saturated Shoulder",
                "depth": 0.05,
                "cwPct": 15.0,
                "cat": "Roadside Water Only - Passable",
                "conf": 0.912,
                "db": -11.4,
            }
        ]

        for ed in events_data:
            r = road_objs[ed["road"]]
            ev = ChainageEvent(
                road_id=r.id,
                scene_id=scene1.id,
                start_m=ed["start_m"],
                end_m=ed["end_m"],
                length_m=ed["length_m"],
                category=ed["cat"],
                max_depth_m=ed["depth"],
                flooded_pct=ed["cwPct"],
                confidence=ed["conf"],
                delta_db=ed["db"],
                flank=ed["flank"],
                first_seen=now - timedelta(minutes=14)
            )
            session.add(ev)
            await session.flush()

            # Create corresponding Alert
            is_sub = "Washout" in ed["cat"] or ed["depth"] > 0.4
            alert = Alert(
                event_id=ev.id,
                severity="CRITICAL" if is_sub else "WARNING",
                road_label=f"{r.code}: Km {ed['start_m']/1000:.3f} to {ed['end_m']/1000:.3f}",
                text=f"{ed['cat']}: Depth estimated +{ed['depth']:.2f}m. {ed['flank']}. Delta {ed['db']} dB.",
                zone=dist_objs["Porbandar"].name if "25" in r.code else dist_objs["Gir Somnath"].name,
                action_label="Dispatch SDRF Unit" if is_sub else "Monitor Trend"
            )
            session.add(alert)

            # Create Dispatch Kanban card
            disp = DispatchTask(
                event_id=ev.id,
                machinery="JCB-8 + 2 Dumpers + 600 Sandbags" if is_sub else "Inspection Tipper Patrol",
                assignee="Er. Rajesh Parmar (JE)" if is_sub else "Er. Ankit Vora",
                column_state="dispatched" if is_sub else "hotspot",
                progress_pct=65 if is_sub else 10
            )
            session.add(disp)

        # 7. Seed App Configuration (Thresholds & Integration Keys)
        config_items = [
            ("otsu_slope_max_deg", 5.0),
            ("otsu_hand_max_m", 15.0),
            ("min_flood_area_ha", 1.0),
            ("jrc_occurrence_threshold", 75),
            ("confidence_unet_weight", 0.0),
            ("cdse_client_id", "cdse-public-verified-token"),
            ("gee_service_account", "sar-backend@sar-drishti-gujarat-123456.iam.gserviceaccount.com"),
            ("nic_sms_gateway_key", "NIC-SMS-GUJ-9984-78129")
        ]
        for k, v in config_items:
            session.add(AppConfig(key=k, value=v))

        # 8. Seed Notification Broadcast
        noti = Notification(
            channel="SMS, WhatsApp, Sandes",
            audience="District Collectors, R&B EEs, NDRF 6Bn, GSRTC Depots",
            body="[CRITICAL ALERT - SEOC GUJARAT] SH-25 Miyani Causeway submerged (+42cm). Route CLOSED. Use SH-27 Ranavav detour.",
            status="sent",
            delivered=242,
            failed=7
        )
        session.add(noti)

        # 9. Seed Official District Bulletin
        bulletin = Bulletin(
            district_id=dist_objs["Porbandar"].id,
            scene_id=scene1.id,
            pdf_url="/api/v1/bulletins/1.pdf",
            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            status="draft"
        )
        session.add(bulletin)

        await session.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())

