import requests

BASE = 'http://127.0.0.1:8000/api/v1'

def test_student(roll, expected_name, expected_roll):
    # 1. Login
    resp = requests.post(f'{BASE}/auth/login', json={'username': roll, 'password': roll})
    assert resp.status_code == 200, f'Login failed for {roll}: {resp.text}'
    token = resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Get /me
    me_resp = requests.get(f'{BASE}/auth/me', headers=headers)
    assert me_resp.status_code == 200, f'Get profile failed: {me_resp.text}'
    me_data = me_resp.json()
    assert expected_roll.lower() in me_data['roll_no'].lower(), f"Expected {expected_roll}, got {me_data['roll_no']}"
    assert expected_name.lower() in me_data['full_name'].lower(), f"Expected {expected_name}, got {me_data['full_name']}"

    # 3. Create conversation & ask for identity
    c_resp = requests.post(f'{BASE}/conversations', json={'title': 'Identity Check'}, headers=headers)
    assert c_resp.status_code == 200
    cid = c_resp.json()['conversation_id']

    m_resp = requests.post(f'{BASE}/conversations/{cid}/messages', json={'content': 'What is my roll number and student id?'}, headers=headers)
    assert m_resp.status_code == 200
    m_content = m_resp.json()['content']
    assert expected_roll in m_content, f'Expected {expected_roll} in message, got {m_content}'
    first_expected = expected_name.split()[0].lower()
    assert first_expected in m_content.lower(), f'Expected {first_expected} in greeting, got {m_content}'

    print(f'PASS: {roll} -> {me_data["full_name"]} ({me_data["roll_no"]}) verified.')

if __name__ == '__main__':
    test_student('24cse001', 'Asha Reddy', '24CSE001')
    test_student('24cse002', 'Rahul Verma', '24CSE002')
    test_student('251fa04131', 'SAHIL SHARAD', '251FA04131')
    test_student('251fa04e13', 'AMAN KUMAR', '251FA04E13')
    test_student('251fa04e96', 'ESHANA RAI', '251FA04E96')
