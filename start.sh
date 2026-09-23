# 1. Levantar FastAPI en segundo plano obligatorios en el puerto 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# 2. Levantar Streamlit usando el puerto de Railway
exec streamlit run app/frontend/frontend.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false