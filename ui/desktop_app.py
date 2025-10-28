#!/usr/bin/env python3
"""
Desktop application interface for the MindLink tri-model therapy system.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import logging
from datetime import datetime

from core.orchestrator import TriModelOrchestrator
from utils.logger import SessionLogger
from utils.safety import get_global_safety_manager
from core.context_engine import ContextEngine

class TherapyApp:
    """Main desktop application for the MindLink therapy system."""
    
    def __init__(self, root):
        """Initialize the therapy application."""
        self.root = root
        self.root.title("MindLink - Tri-Model Therapy Assistant")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg="#f0f0f0")
        
        # Initialize components
        self.orchestrator = TriModelOrchestrator()
        self.session_logger = SessionLogger()
        self.safety_manager = get_global_safety_manager()
        self.context_engine = ContextEngine()
        
        # State variables
        self.is_processing = False
        self.session_start_time = datetime.now()
        
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
        # Create main frame with styling
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nesw")
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header with enhanced styling
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        title_label = tk.Label(
            header_frame,
            text="MindLink Therapy Assistant",
            font=("Arial", 20, "bold"),
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Status indicator with enhanced styling
        self.status_var = tk.StringVar(value="Ready")
        status_frame = tk.Frame(header_frame, bg="#f0f0f0")
        status_frame.grid(row=0, column=1, sticky="e")
        
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            fg="#7f8c8d",
            bg="#ecf0f1",
            padx=10,
            pady=5,
            relief="raised",
            borderwidth=1
        )
        status_label.pack()
        
        # Conversation display with enhanced styling
        conv_frame = tk.LabelFrame(
            main_frame,
            text="Conversation",
            padx=10,
            pady=10,
            font=("Arial", 12, "bold"),
            fg="#34495e",
            bg="#f0f0f0"
        )
        conv_frame.grid(row=1, column=0, columnspan=2, sticky="nesw", pady=(0, 15))
        conv_frame.columnconfigure(0, weight=1)
        conv_frame.rowconfigure(0, weight=1)
        
        self.conversation_display = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#2c3e50",
            padx=10,
            pady=10,
            relief="flat",
            borderwidth=1
        )
        self.conversation_display.grid(row=0, column=0, sticky="nesw")
        
        # Input area with enhanced styling
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        
        input_label = tk.Label(
            input_frame,
            text="Your message:",
            font=("Arial", 12),
            fg="#34495e",
            bg="#f0f0f0"
        )
        input_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.user_input = tk.Entry(
            input_frame,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#2c3e50",
            relief="solid",
            borderwidth=1
        )
        self.user_input.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)
        
        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        send_button.grid(row=0, column=2)
        
        # Control buttons with enhanced styling
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        button_frame.columnconfigure(1, weight=1)
        
        clear_button = tk.Button(
            button_frame,
            text="Clear Conversation",
            command=self.clear_conversation,
            font=("Arial", 10),
            bg="#e74c3c",
            fg="#ffffff",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        clear_button.grid(row=0, column=0, padx=(0, 10))
        
        disclaimer_button = tk.Button(
            button_frame,
            text="Show Disclaimer",
            command=self.show_disclaimer,
            font=("Arial", 10),
            bg="#f39c12",
            fg="#ffffff",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        disclaimer_button.grid(row=0, column=1, padx=(0, 10))
        
        # Add session info button
        session_button = tk.Button(
            button_frame,
            text="Session Info",
            command=self.show_session_info,
            font=("Arial", 10),
            bg="#9b59b6",
            fg="#ffffff",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        session_button.grid(row=0, column=2, padx=(0, 10))
        
        quit_button = tk.Button(
            button_frame,
            text="Quit",
            command=self.root.quit,
            font=("Arial", 10),
            bg="#95a5a6",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        quit_button.grid(row=0, column=3, sticky="e")
        
        # Focus on input field
        self.user_input.focus()
    
    def show_disclaimer(self):
        """Display the medical disclaimer."""
        disclaimer = self.safety_manager.get_disclaimer()
        self.display_message("System", disclaimer, "info")
        self.safety_manager.record_disclaimer_shown()
    
    def show_session_info(self):
        """Display session information."""
        duration = datetime.now() - self.session_start_time
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        
        info = f"Session Duration: {minutes} minutes, {seconds} seconds\n"
        info += f"Interactions: {len(self.context_engine.get_full_history())} messages\n"
        info += f"Status: Active"
        
        self.display_message("Session Info", info, "info")
    
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
        
        # Format message based on type with modern LLM style
        if msg_type == "info":
            # Format info messages with bullet points and better structure
            formatted_msg = f"[{timestamp}] {sender}:\n"
            # Split message into lines and format as bullet points if it contains multiple lines
            lines = message.strip().split('\n')
            if len(lines) > 1:
                formatted_msg += "  • " + "\n  • ".join(lines) + "\n"
            else:
                formatted_msg += "  • " + message + "\n"
            self.conversation_display.insert(tk.END, formatted_msg, "info")
        elif msg_type == "warning":
            # Format warning messages with clear heading
            formatted_msg = f"[{timestamp}] ⚠️  {sender}:\n"
            formatted_msg += "  " + message.replace('\n', '\n  ') + "\n"
            self.conversation_display.insert(tk.END, formatted_msg, "warning")
        elif msg_type == "error":
            # Format error messages with clear heading
            formatted_msg = f"[{timestamp}] ❌ {sender}:\n"
            formatted_msg += "  " + message.replace('\n', '\n  ') + "\n"
            self.conversation_display.insert(tk.END, formatted_msg, "error")
        else:
            # Format regular messages (user and MindLink responses) with better structure
            formatted_msg = f"[{timestamp}] {sender}:\n"
            # Format as paragraphs with proper indentation
            paragraphs = message.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    formatted_msg += "  " + paragraph.replace('\n', '\n  ') + "\n\n"
            self.conversation_display.insert(tk.END, formatted_msg)
        
        # Apply formatting tags with enhanced styling
        self.conversation_display.tag_config("info", foreground="#3498db", font=("Arial", 11))
        self.conversation_display.tag_config("warning", foreground="#f39c12", font=("Arial", 11, "bold"))
        self.conversation_display.tag_config("error", foreground="#e74c3c", font=("Arial", 11, "bold"))
        
        # Add spacing between messages
        self.conversation_display.insert(tk.END, "\n")
        
        # Scroll to bottom
        self.conversation_display.see(tk.END)
        self.conversation_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Handle sending a user message."""
        if self.is_processing:
            return
            
        user_message = self.user_input.get().strip()
        if not user_message:
            # Visual feedback for empty message
            self.user_input.config(bg="#ffebee")
            self.root.after(500, lambda: self.user_input.config(bg="#ffffff"))
            return
            
        # Clear input field
        self.user_input.delete(0, tk.END)
        # Reset background color
        self.user_input.config(bg="#ffffff")
        
        # Add to conversation history
        self.context_engine.add_exchange(user_message, "")
        
        # Display user message
        self.display_message("You", user_message)
        
        # Process in separate thread to prevent UI freezing
        self.is_processing = True
        self.status_var.set("Processing...")
        # Visual feedback for processing
        self.root.config(cursor="watch")
        
        # Start processing thread
        processing_thread = threading.Thread(
            target=self.process_user_message,
            args=(user_message,),
            daemon=True
        )
        processing_thread.start()
    
    def process_user_message(self, user_message: str):
        """
        Process user message through the tri-model system.
        
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
        # Get the original user message from the context engine
        history = self.context_engine.get_full_history()
        user_message = history[-1]["user"] if history else ""
        
        # Display safety intervention if needed
        if risk_assessment.get("is_emergency", False):
            safety_message = self.safety_manager.get_safety_intervention(risk_assessment)
            self.display_message("Safety Alert", safety_message, "warning")
        
        # Synthesize final response
        final_response = self.orchestrator.synthesize_response(therapeutic_response, medical_analysis, user_message, self.context_engine)
        
        # Display system response
        self.display_message("MindLink", final_response)
        
        # Update the last exchange with the MindLink response
        history = self.context_engine.get_full_history()
        if history and history[-1]["mindlink"] == "":
            # Update the last exchange with the MindLink response
            # Since we can't directly modify the exchange, we'll clear the last entry and add a new one
            self.context_engine.clear_history()
            # Re-add all previous exchanges
            for exchange in history[:-1]:
                self.context_engine.add_exchange(exchange["user"], exchange["mindlink"])
            # Add the last exchange with the updated response
            self.context_engine.add_exchange(history[-1]["user"], final_response)
        
        # Reset status
        self.reset_status()
    
    def reset_status(self):
        """Reset processing status."""
        self.is_processing = False
        self.status_var.set("Ready")
        # Reset cursor
        self.root.config(cursor="")
    
    def clear_conversation(self):
        """Clear the conversation history."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the conversation?"):
            self.conversation_display.config(state=tk.NORMAL)
            self.conversation_display.delete(1.0, tk.END)
            self.conversation_display.config(state=tk.DISABLED)
            self.context_engine.clear_history()
            self.display_message("System", "Conversation cleared. How can I help you today?", "info")

if __name__ == "__main__":
    # Example usage
    root = tk.Tk()
    app = TherapyApp(root)
    root.mainloop()