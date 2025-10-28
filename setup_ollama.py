#!/usr/bin/env python3
"""
Script to help setup Ollama and download required models for MindLink.
"""

import subprocess
import sys
import os
import time

def check_ollama_installed():
    """Check if Ollama is installed and accessible."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ Ollama is not installed or not accessible")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Ollama is not installed or not accessible")
        return False

def install_ollama():
    """Provide instructions for installing Ollama."""
    print("\nInstalling Ollama:")
    print("1. Visit https://ollama.ai/download")
    print("2. Download the installer for your operating system")
    print("3. Run the installer and follow the setup instructions")
    print("4. Restart your terminal/command prompt after installation")
    print("\nAfter installation, run this script again to download models.")

def download_models():
    """Download the required models for MindLink."""
    models = [
        ("phi3:3.8b", "Therapeutic Specialist (3.8B parameters)"),
        ("mistral:7b", "Medical Context Sentinel (7B parameters)")
    ]
    
    print("\nDownloading required models...")
    print("This may take 10-30 minutes depending on your internet connection.")
    
    for model_name, description in models:
        print(f"\nDownloading {description}...")
        print(f"Model: {model_name}")
        
        try:
            # Show progress during download
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Print output in real-time
            if process.stdout is not None:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(f"  {output.strip()}")
            else:
                # Wait for process to complete without live output
                process.wait()
            
            rc = process.poll()
            if rc == 0:
                print(f"✓ Successfully downloaded {model_name}")
            else:
                print(f"✗ Failed to download {model_name}")
                
        except Exception as e:
            print(f"✗ Error downloading {model_name}: {e}")

def verify_models():
    """Verify that models are available."""
    models = ["phi3:3.8b", "mistral:7b"]
    
    print("\nVerifying models...")
    for model in models:
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if model in result.stdout:
                print(f"✓ {model} is available")
            else:
                print(f"✗ {model} is not available")
        except Exception as e:
            print(f"✗ Error verifying {model}: {e}")

def main():
    """Main setup function."""
    print("MindLink Ollama Setup Script")
    print("=" * 40)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        install_ollama()
        return 1
    
    # Download required models
    download_models()
    
    # Verify models
    verify_models()
    
    print("\n" + "=" * 40)
    print("Setup Complete!")
    print("\nTo run MindLink:")
    print("1. Ensure Ollama service is running")
    print("2. Execute: python main.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())