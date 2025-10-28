# MindLink - Dual-Model AI Therapy System

A local implementation of a dual-model AI therapy system designed to address the "somatic blind spot" in mental health AI.

## System Architecture

### Core Components

1. **Therapeutic Specialist (SLM)**: A 3B parameter model fine-tuned on psychiatric literature for empathetic, clinically appropriate dialogue
2. **Medical Context Sentinel (GLM)**: A medium-scale model with broad medical knowledge to identify potential physical health correlations
3. **Orchestration Layer**: Coordinates both models and synthesizes their outputs into safe, context-aware responses

### Key Features

- **Privacy-Focused**: Runs entirely locally with no data leaving your system
- **Dual Analysis**: Simultaneous psychological and medical context evaluation
- **Safety Measures**: Built-in medical disclaimer system and emergency referral protocols
- **Real-time Monitoring**: Performance metrics and system health tracking

## Installation

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull required models:
   ```bash
   ollama pull phi3:3.8b  # Therapeutic Specialist
   ollama pull mistral:7b  # Medical Context Sentinel
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
MindLink/
├── main.py              # Application entry point
├── core/
│   ├── orchestrator.py  # Model coordination system
│   ├── therapist.py     # Therapeutic Specialist interface
│   └── sentinel.py      # Medical Context Sentinel interface
├── ui/
│   └── desktop_app.py   # Desktop application interface
├── utils/
│   ├── safety.py        # Safety measures and disclaimers
│   └── logger.py        # Logging and monitoring
├── config/
│   └── settings.py      # Configuration management
└── README.md
```

## Hardware Requirements

- Minimum 16GB RAM (24GB recommended)
- GPU with 4GB VRAM (NVIDIA 1650 Ti or equivalent)
- 20GB free storage for models

## Running the Application

### Windows
Double-click `run_mindlink.bat` or run from command prompt:
```cmd
run_mindlink.bat
```

### Linux/macOS
Make the script executable and run:
```bash
chmod +x run_mindlink.sh
./run_mindlink.sh
```

### Manual Execution
Alternatively, run directly with Python:
```bash
python main.py
```

## License

MIT License - See LICENSE file for details