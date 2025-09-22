#!/usr/bin/env python3
"""Setup script for CGSRef development environment."""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def check_dependencies():
    """Check if required system dependencies are available."""
    dependencies = ["git", "curl"]

    for dep in dependencies:
        if not shutil.which(dep):
            print(f"Error: {dep} is required but not found")
            sys.exit(1)
        print(f"✓ {dep} found")


def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path("venv")

    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return

    print("Creating virtual environment...")
    if not run_command(f"{sys.executable} -m venv venv"):
        print("Error: Failed to create virtual environment")
        sys.exit(1)

    print("✓ Virtual environment created")


def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")

    # Determine pip path based on OS
    if os.name == "nt":  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix-like
        pip_path = "venv/bin/pip"

    commands = [
        f"{pip_path} install --upgrade pip",
        f"{pip_path} install -r requirements.txt",
        f"{pip_path} install -e .",  # Install in development mode
    ]

    for cmd in commands:
        if not run_command(cmd):
            print(f"Error: Failed to run {cmd}")
            sys.exit(1)

    print("✓ Python dependencies installed")


def setup_environment_file():
    """Set up environment configuration file."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✓ .env file already exists")
        return

    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from .env.example")
        print("⚠️  Please edit .env file and add your API keys")
    else:
        print("Warning: .env.example not found")


def create_directories():
    """Create necessary directories."""
    directories = [
        "data/output",
        "data/profiles",
        "data/workflows",
        "data/knowledge_base",
        "data/cache",
        "data/chroma",
        "logs",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✓ Created necessary directories")


def setup_git_hooks():
    """Set up Git pre-commit hooks."""
    if not Path(".git").exists():
        print("⚠️  Not a Git repository, skipping Git hooks setup")
        return

    print("Setting up Git pre-commit hooks...")

    # Determine python path based on OS
    if os.name == "nt":  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        python_path = "venv/bin/python"

    if not run_command(f"{python_path} -m pip install pre-commit"):
        print("Warning: Failed to install pre-commit")
        return

    if not run_command(f"{python_path} -m pre_commit install"):
        print("Warning: Failed to install pre-commit hooks")
        return

    print("✓ Git pre-commit hooks installed")


def run_tests():
    """Run basic tests to verify setup."""
    print("Running basic tests...")

    # Determine python path based on OS
    if os.name == "nt":  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        python_path = "venv/bin/python"

    if not run_command(f"{python_path} -m pytest tests/unit/ -v", check=False):
        print("⚠️  Some tests failed, but setup can continue")
    else:
        print("✓ Basic tests passed")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - OPENAI_API_KEY=your-key-here")
    print("   - ANTHROPIC_API_KEY=your-key-here")
    print("   - DEEPSEEK_API_KEY=your-key-here")
    print("\n2. Activate the virtual environment:")

    if os.name == "nt":  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix-like
        print("   source venv/bin/activate")

    print("\n3. Start the API server:")
    print("   python -m api.rest.main")
    print("\n4. Or use the CLI:")
    print('   python -m api.cli.main generate "AI in Finance"')
    print("\n5. Run tests:")
    print("   pytest")
    print("\n6. View documentation:")
    print("   Open docs/architecture/README.md")


def main():
    """Main setup function."""
    print("CGSRef Development Environment Setup")
    print("=" * 40)

    try:
        check_python_version()
        check_dependencies()
        setup_virtual_environment()
        install_dependencies()
        setup_environment_file()
        create_directories()
        setup_git_hooks()
        run_tests()
        print_next_steps()

    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
