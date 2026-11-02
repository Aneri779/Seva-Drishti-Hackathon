# SAR-Drishti | Satellite Highway Submergence & Washout Analytics System

> **Roads & Buildings (R&B) Department, Government of Gujarat**  
> Integrated with State Emergency Operation Centre (SEOC), Gandhinagar & BISAG-N Remote Sensing Engine.

---

## 🌟 Overview

**SAR-Drishti** is an operational, cloud-penetrating synthetic aperture radar (SAR) monitoring platform designed to detect highway submergence, causeway overtopping, and embankment washouts during heavy monsoon downpours and cyclonic events (e.g., Cyclone Biparjoy, Cyclone Tauktae) across Gujarat's highway network.

Powered by European Space Agency (ESA) **Copernicus Sentinel-1 C-Band SAR (5.405 GHz)**, SAR-Drishti operates completely uninhibited by cloud cover, torrential rainfall, or darkness, delivering near-real-time actionable intelligence to R&B Executive Engineers, District Collectors, NDRF/SDRF commanders, and GSRTC route controllers.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Data Sources
        S1[Sentinel-1 GRD SAR VV+VH]
        DEM[Copernicus GLO-30 DEM]
        GEE[Google Earth Engine API]
        CDSE[Copernicus Data Space Ecosystem]
    end

    subgraph Backend Engine (FastAPI + Async Python)
        API[FastAPI Server :8000]
        OTS[Otsu Bimodal Inundation Segmenter]
        HYD[DEM Crest Depth Hydraulic Slicer]
        ROUT[Safe Convoy Corridor Solver]
        PDF[ReportLab PAdES Bulletin Generator]
    end

    subgraph Database & Persistence
        PG[(PostgreSQL 15 Local Native)]
        AUDIT[Immutable Audit Log]
        OUTBOX[SMS / Telemetry Outbox]
    end

    subgraph Frontend Workstation (React 19 + Vite 8)
        CLIENT[Vite Dev Server :5173]
        HUD[Dark Military / Govt Telemetry HUD]
        KANBAN[Field Machinery Kanban]
        ROUTING_UI[Convoy Route GIS Planner]
    end

    S1 --> GEE
    DEM --> GEE
    GEE --> API
    CDSE --> API
    API --> PG
    PG --> AUDIT
    PG --> OUTBOX
    PG --> API
    API <-->|REST + Bearer JWT| CLIENT
    CLIENT --> HUD
    CLIENT --> KANBAN
    CLIENT --> ROUTING_UI
```

---

## 🗄️ Database Architecture (PostgreSQL 15)

The application runs against local native **PostgreSQL 15** on port `5432` with database name `sardrishti`.

### Core Database Tables:
1. **`users`**: Official authenticated personnel with canonical roles (`admin`, `rb_ee`, `seoc_officer`, `collector`, `ndrf`, `gsrtc`, `bisag_gis`), approval status, and mobile credentials.
2. **`districts`**: All 33 Gujarat administrative districts with authentic Unicode Gujarati script (`name_gu`) and official LGD codes.
3. **`roads`**: National Highways (NH), State Highways (SH), Major District Roads (MDR), and Other District Roads (ODR) across Gujarat.
4. **`road_segments`**: 500+ chainage-indexed road segments (100 m resolution) with crest elevation data.
5. **`road_status`**: Real-time per-segment inundation classifications (`CLEAR`, `ADVISORY`, `OVERTOPPING`, `WASHOUT`), flooded percentage, and backscatter delta ($\Delta \text{ dB}$).
6. **`chainage_events`**: Active radar-detected flood breaches with start/end chainage, estimated DEM depth, and confidence metrics.
7. **`sar_scenes`**: Ingested Sentinel-1 overpasses with orbit parameters, VV/VH histogram bins, Otsu threshold values, and valid pixel percentages.
8. **`dispatch_tasks`**: 3-column field machinery deployment tracker (`queued` $\rightarrow$ `en_route`/`on_site` $\rightarrow$ `resolved`) with submitted ground-truth verification reports.
9. **`bulletins`**: Official district flood bulletins generated as downloadable PDFs with SHA-256 integrity hashes and PAdES digital signatures.
10. **`notifications` & `notification_deliveries`**: Multi-channel emergency mass broadcast tracking (target, sent, delivered, read/ack, fallback).
11. **`sms_outbox`**: Full audit log of all 6-digit OTP codes and emergency advisories dispatched.
12. **`audit_log`**: Tamper-evident logging of every sensitive operational mutation (login, route calculation, field reports, digital signing, broadcast).
13. **`app_config`**: Dynamic system tuning parameters (Otsu slope masks, HAND cutoff, permanent water thresholds).

---

## 🔑 Complete Guide: Google Earth Engine (GEE) API Setup

The SAR pipeline uses Google Earth Engine (GEE) Python API (`ee`) to pull real Sentinel-1 Level-1 GRD (Ground Range Detected) dual-polarization data (`COPERNICUS/S1_GRD`) and the Copernicus 30 m Digital Elevation Model (`COPERNICUS/DEM/GLO30`).

Follow these exact steps to generate and configure your GEE Service Account credentials:

### Step 1: Create or Select a Google Cloud Project
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google account.
3. In the top navigation bar, click the Project dropdown and select **"New Project"**.
4. Set the **Project Name** (e.g. `sar-drishti-gujarat`).
5. Note down the **Project ID** (e.g. `sar-drishti-gujarat-451200`).

### Step 2: Register the Project for Earth Engine
1. Navigate to [Google Earth Engine Registration](https://code.earthengine.google.com/register).
2. Choose **"Register a Cloud Project"**.
3. Select **"Use an existing Cloud project"** and select the Project ID created in Step 1.
4. Choose the plan type:
   - For educational, hackathon, government disaster, or research use, select **"Unpaid / Non-commercial"** $\rightarrow$ **"Disaster Response / Research"**.
5. Complete registration and accept the terms of service.

### Step 3: Enable the Earth Engine API
1. Back in Google Cloud Console, navigate to **APIs & Services** $\rightarrow$ **Library**.
2. Search for: **`Google Earth Engine API`**.
3. Click on it and press **"Enable"**.

### Step 4: Create a Dedicated Service Account
1. In Cloud Console, go to **IAM & Admin** $\rightarrow$ **Service Accounts**.
2. Click **"+ CREATE SERVICE ACCOUNT"** at the top.
3. Fill in details:
   - **Service account name**: `sar-backend-engine`
   - **Service account ID**: `sar-backend-engine`
4. Click **Create and Continue**.
5. In **Grant this service account access to project**, assign the following role:
   - **Earth Engine Resource Admin** (or **Earth Engine Resource Viewer**)
6. Click **Done**.

### Step 5: Generate and Download the JSON Key File
1. In the Service Accounts list, click on the newly created service account email:  
   `sar-backend-engine@<your-project-id>.iam.gserviceaccount.com`.
2. Navigate to the **Keys** tab.
3. Click **Add Key** $\rightarrow$ **Create new key**.
4. Choose **JSON** format and click **Create**.
5. The JSON file will download automatically to your machine.
6. Rename this file to **`gee-key.json`** and move it into the backend secrets folder:
   ```
   sar-drishti-backend/secrets/gee-key.json
   ```
   > ⚠️ **IMPORTANT SECURITY RULE:** Never commit `gee-key.json` to version control. It is strictly excluded by `.gitignore`.

### Step 6: Verify GEE Credentials from the Command Line
You can test that GEE initializes and pulls real Sentinel-1 scenes over Gujarat:
```bash
python -c "import ee; credentials = ee.ServiceAccountCredentials('sar-backend-engine@<your-project-id>.iam.gserviceaccount.com', 'secrets/gee-key.json'); ee.Initialize(credentials); print('GEE INITIALIZED! S1 scenes over Gujarat:', ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(ee.Geometry.Rectangle([68.0, 20.0, 74.5, 24.5])).filterDate('2024-08-01', '2024-09-01').size().getInfo())"
```

---

## ⚙️ Environment Configuration (`.env`)

### 1. Backend Environment: `sar-drishti-backend/.env`
Create or update `sar-drishti-backend/.env` with the following variables:

```env
# Application Environment
ENV=development
APP_NAME="SAR-Drishti State Highway Submergence Engine"
PORT=8000
HOST=127.0.0.1

# Database Configuration (PostgreSQL 15 Local Native)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sardrishti
DB_SYNC_URL=postgresql://postgres:postgres@localhost:5432/sardrishti

# Redis Configuration (Optional / Local Cache Fallback Active)
REDIS_URL=redis://localhost:6379/0

# Security & Authentication (JWT + OTP)
JWT_SECRET=super_secret_jwt_key_gujarat_rb_emergency_ops_2026_x7892
JWT_ALGORITHM=HS256
JWT_ACCESS_TTL_MIN=480
JWT_REFRESH_TTL_DAYS=7
OTP_TTL_SEC=300
OTP_MAX_VERIFY_ATTEMPTS=5

# Google Earth Engine (GEE) Service Account Credentials
GEE_PROJECT=sar-drishti-gujarat-451200
GEE_SERVICE_ACCOUNT=sar-backend-engine@sar-drishti-gujarat-451200.iam.gserviceaccount.com
GEE_KEY_FILE=secrets/gee-key.json

# Copernicus Data Space Ecosystem (CDSE) API (Optional Secondary S1 Source)
CDSE_CLIENT_ID=your_cdse_oauth_client_id
CDSE_CLIENT_SECRET=your_cdse_oauth_client_secret

# Government Emergency SMS Gateway
NIC_SMS_API_KEY=NIC-SMS-GUJ-9984-SECURE-KEY
WHATSAPP_GOVT_GATEWAY_URL=https://api.gujarat.gov.in/telemetry/v1/sandes-push

# Gujarat Geospatial AOI (Bounding Box: [min_lon, min_lat, max_lon, max_lat])
GUJARAT_BBOX=[68.1, 20.1, 74.5, 24.7]
```

### 2. Frontend Environment: `seva_first_hackathon/.env`
Create or update `seva_first_hackathon/.env`:

```env
# URL pointing to the FastAPI Backend
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

---

## 🚀 Step-by-Step Installation & Execution Guide

### Prerequisites
- **Python 3.11+ / Python 3.14**
- **Node.js 18+ / 20+** and `npm`
- **PostgreSQL 15** installed and running on port `5432`

---

### Step 1: Initialize PostgreSQL Database

1. Open PowerShell or Command Prompt.
2. Connect to PostgreSQL and create the database:
   ```bash
   psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE sardrishti;"
   ```
3. Run the schema creation and initial seeding:
   ```bash
   cd sar-drishti-backend
   python scripts/init_db.py
   python scripts/seed_all.py
   ```
4. Verify the database tables:
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/sardrishti'); cur = conn.cursor(); cur.execute('SELECT count(*) FROM roads; SELECT count(*) FROM road_segments;'); print('Seeded successfully!')"
   ```

---

### Step 2: Start the FastAPI Backend Server

1. Navigate to the backend directory:
   ```bash
   cd d:\Seva_innovation\sar-drishti-backend
   ```
2. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy asyncpg psycopg2-binary reportlab pyjwt passlib bcrypt earthengine-api pydantic python-multipart
   ```
3. Launch the FastAPI server:
   ```bash
   $env:PYTHONPATH="d:\Seva_innovation\sar-drishti-backend"
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Confirm server health:
   - Open your browser to: **http://127.0.0.1:8000/health/deep**
   - Interactive Swagger API docs: **http://127.0.0.1:8000/docs**

---

### Step 3: Start the React 19 / Vite Frontend Server

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd d:\Seva_innovation\seva_first_hackathon
   ```
2. Install node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite local development server:
   ```bash
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
4. Open the web application:
   - Application URL: **http://127.0.0.1:5173/**

---

## 📱 Pre-Configured Test Accounts & Login Instructions

Authentication is secured using **10-digit Indian Mobile Numbers + 6-digit random dynamic OTPs**. In development mode, every sent OTP is logged directly to the Dev SMS Inbox on the login screen.

### Verified Administrative & Field Accounts:

| Role | Officer Name | Mobile Number | Role Code |
|---|---|---|---|
| **Super Admin** | Super Admin R&B | `9876543210` | `admin` |
| **Executive Engineer** | V. K. Patel (EE Veraval) | `9876543211` | `rb_ee` |
| **SEOC Duty Officer** | Rajiv Shah (SEOC Gandhinagar) | `9876543212` | `seoc_officer` |
| **District Collector** | Dr. Harshit Rao (Collector Porbandar) | `9876543213` | `collector` |
| **NDRF Commander** | Commandant Gurmeet Singh (6 Bn) | `9876543214` | `ndrf` |
| **Field Engineer** | Aneri Patel | `8569797901` | `rb_ee` |

### How to Login:
1. Navigate to **http://127.0.0.1:5173/login**.
2. Enter any 10-digit registered mobile number (e.g., `9876543210`).
3. Click **"SEND VERIFICATION OTP"**.
4. The 6-digit code will appear in the **DEV SMS INBOX** card at the bottom of the screen.
5. Click the auto-fill button or enter the 6 digits in the boxes.
6. Click **"AUTHENTICATE & ENTER STATE SEOC"**.

---

## 🗺️ Complete 11 Workstations Directory

| # | Route | Workstation / Module | Key Operational Capabilities |
|---|---|---|---|
| **1** | `/` | **Public Home / Advisory Portal** | Public corridor safety inspection (`/routes/public-verify`), live Sentinel-1 advisories, offline emergency PDF evacuation map download. |
| **2** | `/register` | **Operational Unit Registration** | Departmental registration with strict 10-digit validation, official domains check, and UTF-8 Gujarati district dropdowns. |
| **3** | `/login` | **Emergency Access Portal** | 6-box controlled OTP verification, live database health indicator, dev SMS outbox telemetry. |
| **4** | `/dashboard` | **SEOC Command Center (Advisory GIS Map)** | Real-time radar corridor vector map, 10-second polling, district-specific breach telemetry, and direct district flood bulletin generation. |
| **5** | `/backscatter` | **SAR Backscatter & Hydro-Connectivity** | Dual-polarization VV/VH backscatter density, Otsu bimodal threshold graph, DEM depth slicing. |
| **6** | `/chainage-registry` | **State Highway Submergence Registry** | Comprehensive tabular log of submerged road segments, dynamic category filtering, and direct CSV export with Bearer token authentication. |
| **7** | `/convoy-routing` | **Relief Logistics & Safe Convoy Routing** | Computes safe detour corridors avoiding active submergence breaches (e.g. NH-27 inland ridge bypass vs impassable SH-25 coastal cut-off). |
| **8** | `/notifications` | **SEOC Mass Notification Ops** | Multi-channel broadcast transmission with human confirmation modal and real-time delivery funnel tracking. |
| **9** | `/bulletin` | **Automated District Flood Bulletin Generator** | Python `reportlab` PDF generation, SHA-256 integrity hash verification, PAdES digital signing, and dual English/ગુજરાતી technical toggle. |
| **10** | `/dispatch` | **R&B Field Engineer & Machinery Dispatch** | 3-column Kanban tracker (`SAR HOTSPOTS` $\rightarrow$ `MACHINERY DISPATCHED` $\rightarrow$ `CLEARED & RESTORED`) with ground-truth ML feedback sync. |
| **11** | `/admin` | **Admin Config & Master GIS Asset Repo** | System tuning parameters (Otsu slopes, HAND cutoff, JRC permanent water thresholds), masked credentials view, and audit log inspection. |

---

## 🧪 Comprehensive Automated Validation Suite

An end-to-end Python test suite is provided at `scripts/test_full_suite.py`. It executes all 8 mission-critical operational paths against PostgreSQL and FastAPI:

```bash
python scripts/test_full_suite.py
```

### Expected Output:
```text
[1] OTP SENT & FETCHED: ******
[2] LOGIN SUCCESS: Super Admin R&B | Role: admin
[3] CONVOY ROUTE CALCULATION SUCCESS: Safe via NH-27 Rajkot & Ranavav Ridge Bypass (High Navigability) (426.5 km)
[4] FLOOD BULLETIN PDF GENERATED: ID 15 | SHA256: 3353b7d9eb06cf7c...
[5] BULLETIN DIGITALLY SIGNED: signed | Signer: Super Admin R&B
[6] MASS NOTIFICATION BROADCAST: sent | Recipients: 7
[7] FIELD DISPATCH UPDATE: updated
[8] ADMIN CONFIG UPDATED: Keys ['otsu_slope_max_deg', 'otsu_hand_max_m']

>>> ALL 8 CORE OPERATIONAL WORKFLOWS VALIDATED 100% PASS! <<<
```

---

## 📄 License & Departmental Notice

Developed for the **Roads & Buildings (R&B) Department, Government of Gujarat** under the Gujarat State Disaster Management Authority (GSDMA) framework.  
Satellite data © European Space Agency (ESA) Copernicus Sentinel-1 (2024–2026).

