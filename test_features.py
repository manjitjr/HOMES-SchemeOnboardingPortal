#!/usr/bin/env python3
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Login as scheme_user
print("=" * 60)
print("1. Testing scheme user login and scheme creation")
print("=" * 60)
r = client.post('/api/auth/login', json={'username': 'moh_user', 'password': 'password'})
print(f"Login: {r.status_code}")
token = r.json().get('token') if r.status_code == 200 else None
h = {'Authorization': f'Bearer {token}'} if token else {}

# 2. Create a new scheme
print("\n2. Creating a new scheme")
scheme_data = {
    'agency': 'Test Agency',
    'scheme_name': 'Test Scheme',
    'scheme_code': 'TA_TS',
    'legislated_or_consent': 'Legislated'
}
r = client.post('/api/schemes', json=scheme_data, headers=h)
print(f"Create Scheme: {r.status_code}")
if r.status_code == 201:
    print(f"✓ Scheme created: {r.json()['scheme_name']}")

# 3. Get onboarding slots
print("\n3. Getting onboarding slots")
r = client.get('/api/scheduling/slots', headers=h)
print(f"Get Slots: {r.status_code}")
if r.status_code == 200:
    slots = r.json()
    print(f"✓ Total slots: {len(slots)}")
    if slots:
        slot = slots[0]
        print(f"First slot: {slot['title']}")
        print(f"  - Year: {slot['year']}, Month: {slot['month_label']}")
        print(f"  - Capacity (admin only): {slot['capacity']}")
        print(f"  - Interested count (admin only): {slot['interested_count']}")

# 4. Book first slot
print("\n4. Testing first slot booking (no justification needed)")
if slots:
    first_slot = slots[0]
    booking = {
        'technical_go_live_date': first_slot['date_min'],
        'business_go_live_date': first_slot['date_max'],
        'justification': None
    }
    r = client.post(f"/api/scheduling/slots/{first_slot['id']}/interest", json=booking, headers=h)
    print(f"First Booking: {r.status_code}")
    if r.status_code == 200:
        print(f"✓ Booking successful")
        print(f"  Approval Status: {r.json()['approval_status']}")
    else:
        print(f"Error: {r.json()['detail']}")

# 5. Try to book second slot in same year
print("\n5. Testing second slot in same year (should require justification)")
slots_by_year = {}
for s in slots:
    year = s['year']
    if year not in slots_by_year:
        slots_by_year[year] = []
    slots_by_year[year].append(s)

first_year = first_slot['year']
if len(slots_by_year[first_year]) > 1:
    second_slot = slots_by_year[first_year][1]
    
    # Try WITHOUT justification
    booking_no_just = {
        'technical_go_live_date': second_slot['date_min'],
        'business_go_live_date': second_slot['date_max'],
        'justification': ''
    }
    r = client.post(f"/api/scheduling/slots/{second_slot['id']}/interest", json=booking_no_just, headers=h)
    print(f"  Second Booking (NO JUSTIFICATION): {r.status_code}")
    if r.status_code != 200:
        print(f"  ✓ Correctly rejected: {r.json()['detail'][:80]}...")
    
    # Try WITH justification
    booking_with_just = {
        'technical_go_live_date': second_slot['date_min'],
        'business_go_live_date': second_slot['date_max'],
        'justification': 'Multiple bookings needed for phased rollout'
    }
    r = client.post(f"/api/scheduling/slots/{second_slot['id']}/interest", json=booking_with_just, headers=h)
    print(f"  Second Booking (WITH JUSTIFICATION): {r.status_code}")
    if r.status_code == 200:
        print(f"  ✓ Correctly approved with approval_status: {r.json()['approval_status']}")

# 6. Check approver notifications
print("\n6. Testing approver notifications and approval workflow")
r = client.post('/api/auth/login', json={'username': 'moh_approver', 'password': 'password'})
approver_token = r.json().get('token') if r.status_code == 200 else None
approver_h = {'Authorization': f'Bearer {approver_token}'} if approver_token else {}

r = client.get('/api/scheduling/notifications', headers=approver_h)
print(f"Get Notifications: {r.status_code}")
if r.status_code == 200:
    notifs = r.json()
    print(f"✓ Total notifications: {len(notifs)}")
    if notifs:
        pending = [n for n in notifs if n['approval_status'] == 'pending']
        print(f"  Pending approvals: {len(pending)}")
        if pending:
            n = pending[0]
            print(f"\n  First pending notification:")
            print(f"    - User: {n['display_name']}")
            print(f"    - Slot: {n['slot_title']}")
            print(f"    - Approval Status: {n['approval_status']}")
            print(f"    - Justification: {n['justification'][:50] if n['justification'] else 'N/A'}...")

            # Test approval
            interest_id = n['interest_id']
            r = client.post(f"/api/scheduling/interests/{interest_id}/approve", headers=approver_h)
            print(f"\n  Approve Interest: {r.status_code}")
            if r.status_code == 200:
                print(f"  ✓ Approval successful")

# 7. Verify capacity is hidden from non-admin
print("\n7. Testing capacity visibility (hidden from non-admin)")
r = client.get('/api/scheduling/slots', headers=h)
if r.status_code == 200:
    user_slots = r.json()
    if user_slots:
        print(f"Regular user - capacity field: {user_slots[0]['capacity']}")
        print(f"Regular user - interested_count field: {user_slots[0]['interested_count']}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
