#!/usr/bin/env bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
exec streamlit run app/frontend/frontend.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false