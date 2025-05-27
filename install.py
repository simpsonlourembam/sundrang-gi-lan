import subprocess
import sys
import os

def install_requirements():
    print("Installing required packages...")
    try:
        # First upgrade pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install pygame using pre-built wheel
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame==2.5.2", "--only-binary", ":all:"])
        
        # Install numpy
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
        
        print("Installation completed successfully!")
        print("\nTo run the game:")
        print("1. On desktop: python main.py")
        print("2. On mobile: Use a Python IDE app that supports pygame")
        print("   (e.g., Pydroid 3 for Android)")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have Python 3.8+ installed")
        print("2. Try running the command prompt as administrator")
        print("3. If using mobile, make sure you have a compatible Python IDE installed")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements() 