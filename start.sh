uvicorn app.main:app --host 0.0.0.0 --port 8000 &
streamlit run app/frontend/frontend.py --server.port $PORT --server.address 0.0.0.0