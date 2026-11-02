import urllib.request
import json

def test_full_flow():
    # 1. Send OTP
    data = json.dumps({'mobile': '9876543210'}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/otp/send',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)

    # 2. Get OTP from Dev SMS Outbox
    sms_res = urllib.request.urlopen('http://127.0.0.1:8000/api/v1/auth/dev/sms-outbox')
    latest = json.loads(sms_res.read().decode())[0]
    otp = latest['body'].split('is ')[1].split('.')[0].strip()
    print('[1] OTP SENT & FETCHED:', otp)

    # 3. Verify OTP
    data2 = json.dumps({'mobile': '9876543210', 'otp': otp}).encode()
    req2 = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/otp/verify',
        data=data2,
        headers={'Content-Type': 'application/json'}
    )
    res2 = urllib.request.urlopen(req2)
    login_data = json.loads(res2.read().decode())
    print('[2] LOGIN SUCCESS:', login_data['user']['name'], '| Role:', login_data['user']['role'])
    token = login_data['token']

    # 4. Convoy Routing
    req3 = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/routes',
        data=json.dumps({
            'origin': 'Porbandar R&B Circle',
            'destination': 'Dwarka NDRF Station',
            'vehicle_class': 'TRUCK_HEAVY'
        }).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    res3 = urllib.request.urlopen(req3)
    route_json = json.loads(res3.read().decode())
    print('[3] CONVOY ROUTE CALCULATION SUCCESS: Safe via', route_json['safe_route']['via'], f"({route_json['safe_route']['distance_km']} km)")

    # 5. Generate Bulletin PDF
    req4 = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/bulletins',
        data=json.dumps({'district': 'Gir Somnath'}).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    res4 = urllib.request.urlopen(req4)
    bulletin = json.loads(res4.read().decode())
    print('[4] FLOOD BULLETIN PDF GENERATED: ID', bulletin['id'], '| SHA256:', bulletin['sha256'][:16])

    # 6. Digitally Sign Bulletin
    b_id = bulletin['id']
    req5 = urllib.request.Request(
        f'http://127.0.0.1:8000/api/v1/bulletins/{b_id}/sign',
        data=b'{}',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    res5 = urllib.request.urlopen(req5)
    sign_json = json.loads(res5.read().decode())
    print('[5] BULLETIN DIGITALLY SIGNED:', sign_json['status'], '| Signer:', sign_json['signed_by'])

    # 7. Mass Broadcast Notification
    req6 = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/notifications',
        data=json.dumps({
            'message': 'EMERGENCY: SH-25 submerged. Detour active.',
            'audience': 'All Emergency Teams',
            'confirmed': True
        }).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    res6 = urllib.request.urlopen(req6)
    notif_json = json.loads(res6.read().decode())
    print('[6] MASS NOTIFICATION BROADCAST:', notif_json['status'], '| Recipients:', notif_json.get('recipient_count'))

    # 8. Field Dispatch Task Update
    tasks_res = urllib.request.urlopen(
        urllib.request.Request(
            'http://127.0.0.1:8000/api/v1/dispatch-tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
    )
    tasks = json.loads(tasks_res.read().decode())
    if tasks:
        t_id = tasks[0]['id']
        req7 = urllib.request.Request(
            f'http://127.0.0.1:8000/api/v1/dispatch-tasks/{t_id}',
            data=json.dumps({'progress_pct': 50, 'verdict': 'CONFIRMED'}).encode(),
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        )
        req7.get_method = lambda: 'PATCH'
        res7 = urllib.request.urlopen(req7)
        print('[7] FIELD DISPATCH UPDATE:', json.loads(res7.read().decode())['status'])

    # 9. Admin Config Save
    req8 = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/admin/config',
        data=json.dumps({'otsu_slope_max_deg': 6.0, 'otsu_hand_max_m': 14.5}).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    req8.get_method = lambda: 'PUT'
    res8 = urllib.request.urlopen(req8)
    print('[8] ADMIN CONFIG UPDATED: Keys', json.loads(res8.read().decode())['updated'])

    print('\n>>> ALL 8 CORE OPERATIONAL WORKFLOWS VALIDATED 100% PASS! <<<')

if __name__ == '__main__':
    test_full_flow()
