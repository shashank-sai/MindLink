#!/usr/bin/env python3
"""
Desktop application interface for the MindLink dual-model therapy system.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import logging
from datetime import datetime

from core.orchestrator import DualModelOrchestrator
from utils.logger import SessionLogger
from utils.safety import get_global_safety_manager

class TherapyApp:
    """Main desktop application for the MindLink therapy system."""
    
    def __init__(self, root):
        """Initialize the therapy application."""
        self.root = root
        self.root.title("MindLink - Dual-Model Therapy Assistant")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize components
        self.orchestrator = DualModelOrchestrator()
        self.session_logger = SessionLogger()
        self.safety_manager = get_global_safety_manager()
        
        # State variables
        self.is_processing = False
        self.conversation_history = []
        
        # Setup UI
        self.setup_ui()
        
        # Show initial disclaimer if needed
        if self.safety_manager.should_show_disclaimer():
            self.show_disclaimer()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("TherapyApp initialized")
    
    def setup_ui(self):
        """Setup the user interface components."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nesw")
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="MindLink Therapy Assistant", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(header_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
        # Conversation display
        conv_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        conv_frame.grid(row=1, column=0, columnspan=2, sticky="nesw", pady=(0, 10))
        conv_frame.columnconfigure(0, weight=1)
        conv_frame.rowconfigure(0, weight=1)
        
        self.conversation_display = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20
        )
        self.conversation_display.grid(row=0, column=0, sticky="nesw")
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        input_label = ttk.Label(input_frame, text="Your message:")
        input_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.user_input = ttk.Entry(input_frame)
        self.user_input.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.grid(row=0, column=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        clear_button = ttk.Button(button_frame, text="Clear Conversation", command=self.clear_conversation)
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        disclaimer_button = ttk.Button(button_frame, text="Show Disclaimer", command=self.show_disclaimer)
        disclaimer_button.pack(side=tk.LEFT, padx=(0, 5))
        
        quit_button = ttk.Button(button_frame, text="Quit", command=self.root.quit)
        quit_button.pack(side=tk.RIGHT)
        
        # Focus on input field
        self.user_input.focus()
    
    def show_disclaimer(self):
        """Display the medical disclaimer."""
        disclaimer = self.safety_manager.get_disclaimer()
        self.display_message("System", disclaimer, "info")
        self.safety_manager.record_disclaimer_shown()
    
    def display_message(self, sender: str, message: str, msg_type: str = "normal"):
        """
        Display a message in the conversation area.
        
        Args:
            sender: Who sent the message
            message: Message content
            msg_type: Type of message (normal, info, warning, error)
        """
        self.conversation_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message based on type
        if msg_type == "info":
            formatted_msg = f"[{timestamp}] {sender}: {message}\n"
            self.conversation_display.insert(tk.END, formatted_msg, "info")
        elif msg_type == "warning":
            formatted_msg = f"[{timestamp}] ⚠️  {sender}: {message}\n"
            self.conversation_display.insert(tk.END, formatted_msg, "warning")
        elif msg_type == "error":
            formatted_msg = f"[{timestamp}] ❌ {sender}: {message}\n"
            self.conversation_display.insert(tk.END, formatted_msg, "error")
        else:
            formatted_msg = f"[{timestamp}] {sender}: {message}\n"
            self.conversation_display.insert(tk.END, formatted_msg)
        
        # Apply formatting tags
        self.conversation_display.tag_config("info", foreground="blue")
        self.conversation_display.tag_config("warning", foreground="orange")
        self.conversation_display.tag_config("error", foreground="red")
        
        # Scroll to bottom
        self.conversation_display.see(tk.END)
        self.conversation_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Handle sending a user message."""
        if self.is_processing:
            return
            
        user_message = self.user_input.get().strip()
        if not user_message:
            return
            
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Display user message
        self.display_message("You", user_message)
        
        # Process in separate thread to prevent UI freezing
        self.is_processing = True
        self.status_var.set("Processing...")
        
        # Start processing thread
        processing_thread = threading.Thread(
            target=self.process_user_message,
            args=(user_message,),
            daemon=True
        )
        processing_thread.start()
    
    def process_user_message(self, user_message: str):
        """
        Process user message through the dual-model system.
        
        Args:
            user_message: User's input message
        """
        try:
            # Process through both models
            therapeutic_response, medical_analysis = self.orchestrator.process_user_input(user_message)
            
            # Log interaction
            self.session_logger.log_interaction(user_message, therapeutic_response, medical_analysis)
            
            # Check for safety concerns
            risk_assessment = self.safety_manager.evaluate_emergency_risk(medical_analysis, user_message)
            
            # Schedule UI updates in main thread
            self.root.after(0, self.handle_response, therapeutic_response, medical_analysis, risk_assessment)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.root.after(0, self.display_message, "System", f"Error processing your message: {str(e)}", "error")
            self.root.after(0, self.reset_status)
    
    def handle_response(self, therapeutic_response: str, medical_analysis: dict, risk_assessment: dict):
        """
        Handle the response from the processing thread.
        
        Args:
            therapeutic_response: Response from therapeutic specialist
            medical_analysis: Analysis from medical context sentinel
            risk_assessment: Emergency risk evaluation
        """
        # Display safety intervention if needed
        if risk_assessment.get("is_emergency", False):
            safety_message = self.safety_manager.get_safety_intervention(risk_assessment)
            self.display_message("Safety Alert", safety_message, "warning")
        
        # Synthesize final response
        final_response = self.orchestrator.synthesize_response(therapeutic_response, medical_analysis)
        
        # Display system response
        self.display_message("MindLink", final_response)
        
        # Reset status
        self.reset_status()
    
    def reset_status(self):
        """Reset processing status."""
        self.is_processing = False
        self.status_var.set("Ready")
    
    def clear_conversation(self):
        """Clear the conversation history."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the conversation?"):
            self.conversation_display.config(state=tk.NORMAL)
            self.conversation_display.delete(1.0, tk.END)
            self.conversation_display.config(state=tk.DISABLED)
            self.conversation_history.clear()
            self.display_message("System", "Conversation cleared. How can I help you today?", "info")

if __name__ == "__main__":
    # Example usage
    root = tk.Tk()
    app = TherapyApp(root)
    root.mainloop()