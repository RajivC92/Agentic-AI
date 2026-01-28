NewsGenie — Run & Setup

Quick start (Windows PowerShell)

1. (Optional) Create and activate a virtual environment
   - Create: python -m venv .venv
   - Activate (PowerShell): .\.venv\Scripts\Activate.ps1

2. Install dependencies
   - Using the bundled script (recommended): .\run_app.bat
   - Or manually: .venv\Scripts\python.exe -m pip install -r requirements.txt

3. Provide API keys (optional — required for real results)
   - Create a file named `.env` in the project root with these lines:
     OPENAI_API_KEY=your_openai_key_here
     TAVILY_API_KEY=your_tavily_key_here
     NEWS_API_KEY=your_newsapi_key_here

   - Or set them in your current PowerShell session:
     $env:OPENAI_API_KEY = "your_openai_key_here"; $env:TAVILY_API_KEY = "your_tavily_key_here"; $env:NEWS_API_KEY = "your_newsapi_key_here"

4. Start the app
   - Recommended (installs deps then runs): .\run_app.bat
   - Or directly (once deps installed): .venv\Scripts\python.exe -m streamlit run app.py

Notes & troubleshooting

- The app provides fallback mock behavior when API keys or some libraries are missing; set the environment variables to enable real APIs.
- If imports fail (linter shows unresolved imports), ensure you installed dependencies into the same Python interpreter used to run Streamlit.
- To stop the running Streamlit server press Ctrl+C in the terminal running it or close the terminal.

Files added/changed

- app.py — Streamlit frontend wired to agent helpers and fallbacks
- requirements.txt — project dependencies
- run_app.bat — helper script to install deps and run the app on Windows
- ProjectNewsGenie.ipynb — notebook with the same initialization and defensive code

If you want, I can also generate a minimal .env.example or update app.py to accept alternative NEWSAPI key names.
