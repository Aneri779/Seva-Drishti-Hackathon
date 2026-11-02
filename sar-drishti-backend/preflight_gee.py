import ee, json
from datetime import datetime, timedelta

key_file = 'secrets/gee-key.json'
with open(key_file) as f:
    key_data = json.load(f)
email = key_data['client_email']
project = 'sar-drishti-gujarat-123456'

print(f"Service account: {email}")
credentials = ee.ServiceAccountCredentials(email, key_file)
ee.Initialize(credentials, project=project)
print("GEE INIT: OK")

gujarat_aoi = ee.Geometry.Rectangle([68.0, 20.0, 74.5, 24.5])
end = datetime.utcnow()
start = end - timedelta(days=30)

col = (ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(gujarat_aoi)
    .filterDate(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW')))

count = col.size().getInfo()
print(f"S1 IW GRD VV+VH over Gujarat last 30 days: {count} scenes")

if count > 0:
    latest = col.sort('system:time_start', False).first()
    props = latest.getInfo()['properties']
    orbit_pass = props.get('orbitProperties_pass', 'N/A')
    rel_orbit = props.get('relativeOrbitNumber_start', 'N/A')
    s1_id = props.get('PRODUCT_ID', props.get('system:index', 'N/A'))
    acq_ts = props.get('system:time_start', 0)
    acq_date = datetime.utcfromtimestamp(acq_ts / 1000).strftime('%Y-%m-%d %H:%M UTC') if acq_ts else 'N/A'
    print(f"  orbit_pass: {orbit_pass}")
    print(f"  relativeOrbit: {rel_orbit}")
    print(f"  s1_id: {s1_id}")
    print(f"  acq_date: {acq_date}")
else:
    print("WARNING: No scenes found in last 30 days - using last 90 days for test")
    col90 = (ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(gujarat_aoi)
        .filterDate((end - timedelta(days=90)).strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
        .filter(ee.Filter.eq('instrumentMode', 'IW')))
    count90 = col90.size().getInfo()
    print(f"  Last 90 days count: {count90}")
    if count90 > 0:
        latest = col90.sort('system:time_start', False).first()
        props = latest.getInfo()['properties']
        print(f"  orbit_pass: {props.get('orbitProperties_pass', 'N/A')}")
        print(f"  relativeOrbit: {props.get('relativeOrbitNumber_start', 'N/A')}")
        acq_ts = props.get('system:time_start', 0)
        acq_date = datetime.utcfromtimestamp(acq_ts/1000).strftime('%Y-%m-%d') if acq_ts else 'N/A'
        print(f"  acq_date: {acq_date}")

