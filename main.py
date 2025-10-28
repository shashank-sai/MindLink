#!/usr/bin/env python3
"""
Main entry point for the MindLink dual-model therapy system.
"""

import tkinter as tk
from ui.desktop_app import TherapyApp
from utils.logger import setup_logging

def main():
    """Initialize and run the MindLink therapy application."""
    # Setup logging
    setup_logging()
    
    # Create the main application window
    root = tk.Tk()
    app = TherapyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()