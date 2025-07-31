import subprocess
import os

def run_streamlit_app():
    main_script = "main.py"  # Your Streamlit app filename

    try:
        subprocess.run(["streamlit", "run", main_script], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit exited with error: {e}")

if __name__ == "__main__":
    run_streamlit_app()
