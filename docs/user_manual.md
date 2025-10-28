# MindLink User Manual

## Introduction

MindLink is a revolutionary dual-model AI therapy system designed to address the "somatic blind spot" in traditional mental health AI. Unlike conventional systems that focus solely on psychological patterns, MindLink simultaneously evaluates both therapeutic needs and potential underlying medical factors.

## How It Works

### Dual-Model Architecture

1. **Therapeutic Specialist (SLM)**: A 3.8B parameter model specialized in therapy techniques and empathetic dialogue
2. **Medical Context Sentinel (GLM)**: A 7B parameter model that identifies potential medical correlations with psychological symptoms
3. **Orchestration Layer**: Seamlessly combines both perspectives into safe, context-aware responses

### Key Benefits

- **Enhanced Safety**: Identifies when physical health issues might contribute to psychological symptoms
- **Privacy-Focused**: All processing happens locally on your device
- **Real-time Awareness**: Considers medical context without replacing therapeutic support
- **Emergency Detection**: Recognizes urgent situations requiring immediate intervention

## Getting Started

### First Launch

1. Run the application:
   ```bash
   python main.py
   ```

2. Read and acknowledge the medical disclaimer
3. Begin typing your thoughts or concerns in the input field

### Interface Overview

#### Main Window
- **Conversation Area**: Displays the dialogue history
- **Input Field**: Type your messages here
- **Control Buttons**: 
  - Send: Submit your message
  - Clear Conversation: Start fresh
  - Show Disclaimer: Review safety information
  - Quit: Exit the application

#### Status Indicator
Shows the current system state:
- "Ready": Waiting for input
- "Processing": Generating response

## Using MindLink

### Having a Conversation

1. Type your thoughts or concerns in the input field
2. Press Enter or click "Send"
3. MindLink processes your input through both models simultaneously
4. Receive a response combining therapeutic support with medical context awareness

### Example Interactions

**User**: "I've been feeling really tired and depressed lately, even though I'm getting enough sleep."

**MindLink Response**: 
"[MEDICAL CONTEXT AWARENESS: Potential physical factors (thyroid dysfunction, vitamin D deficiency) may be contributing to your experience. Consider blood tests for thyroid function and vitamin levels]

I hear that you're experiencing fatigue and depression despite adequate sleep, which can be particularly frustrating. This combination of symptoms can significantly impact your daily life. Let's explore what might be happening..."

### Understanding Responses

Responses may include:

1. **Standard Therapeutic Support**: Empathetic dialogue and coping strategies
2. **Medical Context Notes**: When relevant physical factors are identified
3. **Safety Alerts**: Urgent warnings with contact information for emergencies

## Safety Features

### Medical Disclaimer

Displayed at startup and periodically throughout sessions, reminding users that:
- MindLink is NOT a substitute for professional medical care
- Emergency situations require immediate professional intervention
- Medical context awareness supplements, not replaces, therapeutic support

### Emergency Detection

MindLink monitors for:
- Crisis keywords (suicide, self-harm, emergency)
- High-confidence medical concerns
- Urgent health situations

When detected, prominent alerts with emergency contact information appear.

### Privacy Assurance

All conversations remain private:
- No data leaves your device
- No internet connection required for conversations
- Local storage only for session logs

## Advanced Features

### Session Logging

MindLink maintains logs for:
- Interaction count
- Medical flags raised
- System performance metrics

Logs are stored locally in `mindlink.log`.

### Customization Options

Adjust settings in `config/settings.py`:
- Model selection
- Safety thresholds
- UI preferences
- Logging configuration

## Troubleshooting

### Common Issues

1. **Slow Response Times**:
   - Ensure sufficient RAM (16GB+ recommended)
   - Close other memory-intensive applications
   - Check GPU utilization

2. **Connection Errors**:
   - Verify Ollama service is running
   - Check that port 11434 is available
   - Restart the application

3. **Incomplete Responses**:
   - Models may be loading, wait a moment
   - Check system resources
   - Restart if issue persists

### Resource Monitoring

Monitor system performance:
- CPU usage increases during processing
- GPU memory usage peaks at 3-4GB
- RAM usage stabilizes around 10-12GB

## Best Practices

### For Effective Sessions

1. **Be Specific**: Detailed descriptions help identify relevant factors
2. **Include Physical Symptoms**: Note any bodily sensations or changes
3. **Track Patterns**: Mention recurring issues or recent changes
4. **Ask Questions**: Inquire about techniques or clarification as needed

### When to Seek Additional Help

MindLink will indicate when professional consultation is recommended:
- Persistent physical symptoms
- Severe mood changes
- Crisis situations
- Complex medical correlations

## Technical Information

### System Requirements

- **Minimum**: 16GB RAM, 4GB VRAM, 20GB storage
- **Recommended**: 24GB RAM, 6GB VRAM, SSD storage

### Supported Platforms

- Windows 10/11
- macOS 10.14+
- Linux distributions with Python 3.8+

### Model Information

- **Therapeutic Specialist**: Phi-3 3.8B parameters
- **Medical Context Sentinel**: Mistral 7B parameters
- **Total Storage**: Approximately 12GB for both models

## Support and Feedback

For issues, suggestions, or feedback:
1. Check the project repository for updates
2. Review documentation for guidance
3. Submit issues through the official channel

Remember: MindLink enhances therapeutic support but never replaces professional medical care.