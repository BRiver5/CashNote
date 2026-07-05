# CashNote — Pocket Money Log

> Tap, type, and track. No banks required.

Manual pocket-expense tracker: Expo (React Native + TypeScript) frontend + FastAPI (SQLAlchemy + SQLite) backend. Anonymous device-UUID identity — no accounts, no login.

## Structure

```
CashNote/
├── app/      # Expo SDK 54 + TypeScript mobile app
└── server/   # FastAPI + SQLAlchemy + SQLite backend
```

## Run the backend

```bash
cd server
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: `http://<LAN-IP>:8000/docs`. Make sure Windows Firewall allows inbound port 8000 on private networks.

## Run the app

```bash
cd app
# set your machine's LAN IP in .env:
#   EXPO_PUBLIC_API_URL=http://192.168.x.x:8000
npm install
npx expo start
```

Scan the QR with Expo Go (Android). The app generates an anonymous device UUID on first launch and registers it with the backend, which seeds 8 default categories.
