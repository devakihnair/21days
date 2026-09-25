@echo off
title ExamPrep AI - 21 Days Vibecoding
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting ExamPrep AI Web App...
streamlit run app.py
pause
