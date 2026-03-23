import subprocess
import os
import sys

if __name__ == '__main__':
    script = os.path.join(os.getcwd(), 'Home.py')
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', script])
