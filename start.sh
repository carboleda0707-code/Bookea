# 1. Levantar FastAPI en segundo plano en el puerto 8000 (usando uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Levantar Streamlit en el puerto asignado por Railway ($PORT)
exec streamlit run app/frontend/frontend.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false