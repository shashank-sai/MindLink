# MindLink Installation Guide

## Prerequisites

Before installing MindLink, ensure your system meets these requirements:

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **RAM**: Minimum 16GB (24GB recommended)
- **GPU**: NVIDIA GPU with 4GB+ VRAM (1650 Ti or better recommended)
- **Storage**: 20GB free space for models
- **Python**: Version 3.8 or higher

## Step 1: Install Ollama

MindLink uses Ollama to run large language models locally.

### Windows
1. Download the Ollama installer from [ollama.ai](https://ollama.ai)
2. Run the installer and follow the setup wizard
3. Verify installation by opening a terminal and running:
   ```bash
   ollama --version
   ```

### macOS
1. Download the Ollama app from [ollama.ai](https://ollama.ai)
2. Drag Ollama to your Applications folder
3. Open Ollama from your Applications folder
4. Verify installation in Terminal:
   ```bash
   ollama --version
   ```

### Linux
Install using curl:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Verify installation:
```bash
ollama --version
```

## Step 2: Pull Required Models

MindLink requires two specific models:

1. **Therapeutic Specialist (3.8B parameters)**:
   ```bash
   ollama pull phi3:3.8b
   ```

2. **Medical Context Sentinel (7B parameters)**:
   ```bash
   ollama pull mistral:7b
   ```

These downloads may take 10-30 minutes depending on your internet connection.

## Step 3: Install Python Dependencies

Navigate to your MindLink project directory and install dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- `requests`: For HTTP communication with Ollama
- `ollama`: Python client for Ollama
- `psutil`: System monitoring
- Other utility libraries

## Step 4: Verify Installation

Test that everything works together:

1. Ensure Ollama service is running (check system tray on Windows/macOS)
2. Run the verification script:
   ```bash
   python -m core.orchestrator
   ```

You should see sample output showing both models processing a test input.

## Troubleshooting

### Common Issues

1. **Models won't download**:
   - Check internet connection
   - Ensure sufficient disk space
   - Try restarting Ollama service

2. **Python dependencies fail**:
   - Update pip: `pip install --upgrade pip`
   - Try: `pip install --force-reinstall -r requirements.txt`

3. **Ollama connection errors**:
   - Verify Ollama is running
   - Check that port 11434 is not blocked by firewall
   - Restart Ollama service

### System Resources

Monitor resource usage:
- **RAM**: Models will use 8-12GB combined
- **VRAM**: GPU acceleration requires 3-4GB VRAM
- **CPU**: Multi-threaded processing during conversations

## First Run

Start MindLink:
```bash
python main.py
```

On first run:
1. The disclaimer will appear
2. Enter your message in the input box
3. Responses will show both therapeutic content and medical context awareness

## Updating Models

To update models to newer versions:
```bash
ollama pull phi3:3.8b
ollama pull mistral:7b
```

## Uninstalling

To uninstall MindLink:
1. Delete the project folder
2. Remove Ollama through your system's package manager
3. Delete any installed Python virtual environments

For complete removal of models:
```bash
ollama rm phi3:3.8b
ollama rm mistral:7b