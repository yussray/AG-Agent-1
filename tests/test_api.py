import requests, os, sys
from dotenv import load_dotenv

load_dotenv(r'd:\Antigravity\AG-Agent\.env')

key = os.getenv('ANYTHINGLLM_API_KEY', '')
sys.stdout.write(f'Key loaded: {bool(key)}\n')
sys.stdout.write(f'Key length: {len(key)}\n')
sys.stdout.write(f'Key preview: {key[:8]}...\n')
sys.stdout.flush()

headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

try:
    resp = requests.get('http://localhost:3001/api/v1/workspaces', headers=headers, timeout=10)
    sys.stdout.write(f'HTTP Status: {resp.status_code}\n')
    sys.stdout.write(f'Response: {resp.text[:500]}\n')
except Exception as e:
    sys.stdout.write(f'Error: {e}\n')

sys.stdout.flush()
