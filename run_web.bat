@echo off
set API_PORT=55792
set WEB_PORT=55802
set PYTHON_EXE=C:\Users\KHP2HC\fcde_venvs\onPremDedicated_dac\Scripts\python.exe

echo Starting FastAPI Backend on port %API_PORT%...
start /B "" "%PYTHON_EXE%" -m uvicorn api:app --host 0.0.0.0 --port %API_PORT%
echo Waiting for backend to initialize...
timeout /t 3 /nobreak > NUL
echo Starting Streamlit Frontend on port %WEB_PORT%...
"%PYTHON_EXE%" -m streamlit run web_app.py --server.port %WEB_PORT%
