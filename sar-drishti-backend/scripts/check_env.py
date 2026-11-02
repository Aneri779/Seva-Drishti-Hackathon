#!/usr/bin/env python3
"""
scripts/check_env.py
Environment pre-flight check script for SAR-Drishti.
Checks:
- docker
- docker compose
- python >= 3.11
- node >= 20
- git
- gdal (gdalinfo)
- gsutil
- ee.Initialize(project=GEE_PROJECT)
- CDSE token fetch
- free disk >= 40 GB
Prints PASS/FAIL per item with the exact fix command.
If GEE or CDSE fails, flags DEMO_MODE=true and details synthetic data fallbacks.
"""
import sys
import os
import shutil
import subprocess

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)

def check_env():
    print("=" * 60)
    print("      SAR-Drishti Pre-flight Environment Check")
    print("=" * 60)

    results = []
    demo_mode_needed = False
    demo_reasons = []

    # 1. Docker
    ok, out = run_cmd("docker --version")
    if ok:
        results.append(("Docker", "PASS", out, None))
    else:
        results.append(("Docker", "FAIL", "Not installed / not in PATH", "Install Docker Desktop: https://www.docker.com/products/docker-desktop/ and start the engine."))

    # 2. Docker compose
    ok, out = run_cmd("docker compose version")
    if ok:
        results.append(("Docker Compose", "PASS", out, None))
    else:
        results.append(("Docker Compose", "FAIL", "Compose plugin missing or Docker not running", "Ensure Docker Desktop is running with Compose v2 enabled."))

    # 3. Python >= 3.11
    py_ver = sys.version_info
    ver_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    if py_ver.major == 3 and py_ver.minor >= 11:
        results.append(("Python >= 3.11", "PASS", f"Python {ver_str}", None))
    else:
        results.append(("Python >= 3.11", "FAIL", f"Found {ver_str}", "Install Python >= 3.11 via https://www.python.org/downloads/ or winget install Python.Python.3.11"))

    # 4. Node >= 20
    ok, out = run_cmd("node --version")
    if ok and out.startswith("v"):
        try:
            major = int(out.lstrip("v").split(".")[0])
            if major >= 20:
                results.append(("Node.js >= 20", "PASS", out, None))
            else:
                results.append(("Node.js >= 20", "FAIL", f"Found {out}", "Upgrade Node: winget install OpenJS.NodeJS.LTS"))
        except ValueError:
            results.append(("Node.js >= 20", "FAIL", f"Unrecognized version {out}", "Upgrade Node to >= 20"))
    else:
        results.append(("Node.js >= 20", "FAIL", "Not found", "Install Node.js >= 20 via https://nodejs.org/"))

    # 5. Git
    ok, out = run_cmd("git --version")
    if ok:
        results.append(("Git", "PASS", out, None))
    else:
        results.append(("Git", "FAIL", "Git not found", "Install Git: winget install Git.Git"))

    # 6. GDAL (gdalinfo)
    ok, out = run_cmd("gdalinfo --version")
    if ok:
        results.append(("GDAL (gdalinfo)", "PASS", out, None))
    else:
        results.append(("GDAL (gdalinfo)", "FAIL (Notice)", "Not found on host system (Installed inside Docker image)", "Inside Docker: provided by debian gdal-bin. On host: optional or install via OSGeo4W/conda."))

    # 7. gsutil
    ok, out = run_cmd("gsutil version")
    if ok:
        results.append(("gsutil", "PASS", out, None))
    else:
        results.append(("gsutil", "FAIL", "Not installed", "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install or pip install gsutil"))

    # 8. Disk Space >= 40GB
    total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
    free_gb = free / (1024**3)
    if free_gb >= 40:
        results.append(("Free Disk >= 40 GB", "PASS", f"{free_gb:.1f} GB free", None))
    else:
        results.append(("Free Disk >= 40 GB", "FAIL", f"Only {free_gb:.1f} GB free", "Free up at least 40 GB disk space for SAR rasters and Docker images."))

    # 9. GEE Authentication
    gee_project = os.getenv("GEE_PROJECT", "")
    gee_ok = False
    try:
        import ee
        if gee_project:
            ee.Initialize(project=gee_project)
        else:
            ee.Initialize()
        gee_ok = True
        results.append(("Google Earth Engine (GEE)", "PASS", "Initialized successfully", None))
    except Exception as e:
        results.append(("Google Earth Engine (GEE)", "FAIL", str(e), "Run: earthengine authenticate and set GEE_PROJECT=<project_id>"))
        demo_mode_needed = True
        demo_reasons.append("GEE unauthenticated / unconfigured")

    # 10. CDSE token fetch
    cdse_user = os.getenv("CDSE_USERNAME", "")
    cdse_pass = os.getenv("CDSE_PASSWORD", "")
    if cdse_user and cdse_pass:
        try:
            import urllib.request
            import urllib.parse
            import json
            data = urllib.parse.urlencode({
                "client_id": "cdse-public",
                "username": cdse_user,
                "password": cdse_pass,
                "grant_type": "password"
            }).encode('utf-8')
            req = urllib.request.Request("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token", data=data)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    results.append(("Copernicus CDSE Token", "PASS", "Token fetch succeeded", None))
                else:
                    results.append(("Copernicus CDSE Token", "FAIL", f"Status {resp.status}", "Check CDSE credentials in .env"))
                    demo_mode_needed = True
                    demo_reasons.append("CDSE auth failed")
        except Exception as e:
            results.append(("Copernicus CDSE Token", "FAIL", str(e), "Verify credentials at dataspace.copernicus.eu and update .env"))
            demo_mode_needed = True
            demo_reasons.append("CDSE connection/auth failed")
    else:
        results.append(("Copernicus CDSE Token", "FAIL", "CDSE_USERNAME / CDSE_PASSWORD not set in env", "Register free at dataspace.copernicus.eu and set in .env"))
        demo_mode_needed = True
        demo_reasons.append("CDSE credentials absent")

    # Summary Output
    for item, status, detail, fix in results:
        status_colored = f"[{status}]"
        print(f"{status_colored:<12} {item:<28} : {detail}")
        if fix:
            print(f"             --> Fix command: {fix}")

    print("-" * 60)
    if demo_mode_needed:
        print("DEMO_MODE=true ACTIVE:")
        print(f"Triggered by: {', '.join(demo_reasons)}")
        print("The following modules will run on synthetic/sample replay data:")
        print("  - S1 IW GRD Dual-Pol (VV/VH) scene acquisition (synthetic Gujarat corridor)")
        print("  - Otsu bimodal threshold solver and histogram telemetry")
        print("  - DEM cross-section and flood water-level estimation")
        print("  - Hydro-connectivity and chainage breach tagging (KM+m)")
        print("  - SMS, WhatsApp, and Sandes notifications (Console/Sandbox mode)")
        print("  - PAdES PDF signing (Development test certificate)")
    else:
        print("ALL CRITICAL DATA PROVIDERS AUTHENTICATED: Full live Sentinel-1 pipeline enabled.")
    print("=" * 60)

if __name__ == "__main__":
    check_env()

