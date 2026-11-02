import ee, json

key = "secrets/gee_key.json"
email = json.load(open(key))["client_email"]
print(f"Loaded service account: {email}")

try:
    ee.Initialize(ee.ServiceAccountCredentials(email, key), project="sar-drishti-gujarat-123456")
    val = ee.Number(1).getInfo()
    print("GEE CONNECTED SUCCESSFULLY! Test call result:", val)
except Exception as e:
    print("GEE INITIALIZATION FAILED:", e)

