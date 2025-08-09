"""
Setup script for Trading Bot
"""
import os
import sys
import subprocess
from pathlib import Path


def create_virtual_environment():
    """Create a virtual environment for the project"""
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install project dependencies"""
    print("Installing dependencies...")
    
    # Determine the correct pip path
    if sys.platform == "win32":
        pip_path = "venv/Scripts/pip"
        python_path = "venv/Scripts/python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    try:
        # Upgrade pip first
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping creation")
        return True
    
    if not env_template.exists():
        print("❌ .env.template file not found")
        return False
    
    try:
        # Copy template to .env
        with open(env_template, 'r') as template:
            content = template.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print("✅ .env file created from template")
        print("⚠️  Please edit .env file with your API keys and configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        "logs",
        "data",
        "models",
        "notebooks",
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        print("✅ Directories created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False


def run_tests():
    """Run basic tests to verify setup"""
    print("Running basic tests...")
    
    # Determine the correct python path
    if sys.platform == "win32":
        python_path = "venv/Scripts/python"
    else:
        python_path = "venv/bin/python"
    
    try:
        # Run the configuration tests
        result = subprocess.run([
            python_path, "-m", "pytest", 
            "trade_bot/tests/test_config.py", 
            "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Trading Bot Development Environment")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Setup steps
    steps = [
        ("Create virtual environment", create_virtual_environment),
        ("Install dependencies", install_dependencies),
        ("Create .env file", create_env_file),
        ("Create directories", create_directories),
        ("Run tests", run_tests),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix the errors and run setup again.")
        sys.exit(1)
    else:
        print("✅ Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Activate virtual environment:")
        if sys.platform == "win32":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("3. Run the application:")
        print("   python main.py")


if __name__ == "__main__":
    main()
