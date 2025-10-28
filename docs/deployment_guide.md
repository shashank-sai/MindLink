# MindLink Deployment Guide

## System Overview

MindLink is a dual-model AI therapy system that addresses the "somatic blind spot" in mental health AI by simultaneously evaluating both psychological and potential medical factors.

## Prerequisites

### Hardware Requirements
- **Minimum**: 16GB RAM, 4GB VRAM, 20GB free storage
- **Recommended**: 24GB RAM, 6GB VRAM, SSD storage
- **Supported GPUs**: NVIDIA with CUDA support (1650 Ti or better)

### Software Requirements
- **Operating Systems**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: Version 3.8 or higher
- **Ollama**: For local LLM inference

## Installation Steps

### 1. Install Python
Ensure Python 3.8+ is installed on your system:
```bash
python --version
# or
python3 --version
```

If not installed, download from [python.org](https://python.org)

### 2. Install Ollama
Visit [ollama.ai](https://ollama.ai) and download the appropriate installer for your OS.

**Windows/macOS**: Run the installer and follow prompts
**Linux**: 
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Verify installation:
```bash
ollama --version
```

### 3. Clone or Download MindLink
```bash
git clone <repository-url>
# or download and extract the ZIP file
```

### 4. Install Python Dependencies
Navigate to the MindLink directory:
```bash
cd MindLink
pip install -r requirements.txt
```

### 5. Download Required Models
```bash
# Therapeutic Specialist (3.8B parameters)
ollama pull phi3:3.8b

# Medical Context Sentinel (7B parameters)
ollama pull mistral:7b
```

This download may take 10-30 minutes depending on internet speed.

## Configuration

### Settings File
Modify `config/settings.py` to customize behavior:

Key settings:
- `THERAPIST_MODEL`: Model for therapeutic responses
- `SENTINEL_MODEL`: Model for medical analysis
- `MEDICAL_CONCERN_THRESHOLD`: Confidence threshold for medical flags
- `WINDOW_WIDTH/WINDOW_HEIGHT`: UI dimensions

### Logging
Logs are stored in `mindlink.log` by default. Adjust `LOG_LEVEL` in settings for more/less detail.

## Running the Application

### Method 1: Batch/Shell Scripts (Recommended)
**Windows**:
```cmd
run_mindlink.bat
```

**Linux/macOS**:
```bash
chmod +x run_mindlink.sh
./run_mindlink.sh
```

### Method 2: Direct Python Execution
```bash
python main.py
```

### Method 3: Development Server
For development/testing:
```bash
python -m core.orchestrator
```

## System Architecture

### Core Components

1. **Therapeutic Specialist (SLM)**
   - Model: Phi-3 3.8B parameters
   - Purpose: Empathetic, clinically-appropriate dialogue
   - Specialization: Therapy techniques and emotional support

2. **Medical Context Sentinel (GLM)**
   - Model: Mistral 7B parameters
   - Purpose: Identify potential medical correlations
   - Specialization: Physical health pattern recognition

3. **Orchestration Layer**
   - Coordinates both models simultaneously
   - Synthesizes responses for safety and context
   - Manages conversation flow and history

### Data Flow
```
User Input → [Orchestrator] → [Therapist SLM] → Therapeutic Response
                    ↓
              [Sentinel GLM] → Medical Analysis
                    ↓
           [Synthesis Engine] → Final Response
```

## Safety Features

### Medical Disclaimer System
- Automatically displayed at session start
- Periodically shown during long sessions
- Cannot be disabled for safety compliance

### Emergency Detection
Monitors for:
- Crisis keywords (suicide, self-harm, emergency)
- High-confidence medical concerns
- Urgent health situations

### Privacy Assurance
- All processing occurs locally
- No internet required for conversations
- No data collection or transmission

## Troubleshooting

### Common Issues

1. **Models Won't Download**
   - Check internet connection
   - Ensure 20GB+ free disk space
   - Restart Ollama service

2. **Import Errors**
   - Verify Python version (3.8+)
   - Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

3. **Performance Issues**
   - Close other memory-intensive applications
   - Ensure adequate RAM (16GB minimum)
   - Check GPU driver updates

4. **UI Problems**
   - Minimum screen resolution: 800x600
   - Font scaling issues: Adjust in settings.py
   - Window sizing: Modify WINDOW_WIDTH/WINDOW_HEIGHT

### Resource Monitoring

During operation:
- **RAM Usage**: 10-12GB typical
- **VRAM Usage**: 3-4GB for GPU acceleration
- **CPU Usage**: Increases during model inference

### Log Analysis
Check `mindlink.log` for:
- Error messages and stack traces
- Performance metrics
- Session statistics

## Maintenance

### Model Updates
To update models to newer versions:
```bash
ollama pull phi3:3.8b
ollama pull mistral:7b
```

### System Updates
Pull latest changes from repository:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Log Management
- Rotate logs monthly for systems in production
- Monitor disk space usage
- Archive old logs for compliance

## Testing

### Unit Tests
Run the test suite:
```bash
python run_tests.py
```

### Integration Tests
Verify system components work together:
```bash
python test_system.py
```

## Customization

### Adding New Features
1. Follow existing code patterns
2. Maintain separation of concerns
3. Add appropriate logging
4. Update documentation

### Model Replacement
To use different models:
1. Update `config/settings.py`
2. Download new models with Ollama
3. Test compatibility thoroughly

### UI Modifications
UI components are in `ui/desktop_app.py`:
- Modify layout in `setup_ui()` method
- Add new widgets following Tkinter conventions
- Update styling in accordance with accessibility guidelines

## Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review logs for error details
3. Submit issues to project repository
4. Contact development team for enterprise deployments

## Compliance

### Medical Device Disclaimer
MindLink is NOT a medical device and should not be used for diagnosis or treatment decisions.

### Data Protection
Complies with general privacy principles:
- No personal data collection
- Local-only processing
- Secure data handling practices

### Accessibility
Follows general accessibility guidelines:
- Keyboard navigation support
- Screen reader compatibility
- Adjustable text sizes