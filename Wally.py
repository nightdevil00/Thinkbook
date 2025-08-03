#!/usr/bin/env python3
import os
import random
import time
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import sys

CONFIG_FILE = os.path.expanduser("~/.wallpaper_changer_config.json")
LOG_FILE = os.path.expanduser("~/.wallpaper_changer.log")

def log(message):
    """Simple logging function for the background service."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def set_wallpaper(image_path):
    """Sets the wallpaper for the Cinnamon desktop environment."""
    try:
        command = ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{image_path}']
        subprocess.run(command, check=True)
        log(f"Wallpaper set to: {image_path}")
        return True
    except FileNotFoundError:
        log("Error: gsettings command not found. Please ensure it's installed and in your PATH.")
        return False
    except subprocess.CalledProcessError as e:
        log(f"Error: Failed to set wallpaper: {e}")
        return False

def run_service(wallpaper_folder, duration_minutes):
    """The main wallpaper changing loop for the background service."""
    log("Starting wallpaper changer service...")
    while True:
        try:
            wallpapers = [os.path.join(wallpaper_folder, f) for f in os.listdir(wallpaper_folder)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

            if not wallpapers:
                log("Error: No valid image files found in the selected folder.")
                time.sleep(60)  # Wait a bit before checking again
                continue

            random_wallpaper = random.choice(wallpapers)
            set_wallpaper(random_wallpaper)

        except Exception as e:
            log(f"An unexpected error occurred: {e}")

        time.sleep(duration_minutes * 60)

class WallpaperChangerApp:
    def __init__(self, master):
        self.master = master
        master.title("Linux Mint Wallpaper Changer")

        self.config = self.load_config()

        # UI Elements
        self.folder_label = tk.Label(master, text=f"Folder: {self.config.get('wallpaper_folder', 'Not set')}")
        self.folder_label.pack(pady=10)

        self.select_button = tk.Button(master, text="Select Wallpaper Folder", command=self.select_folder)
        self.select_button.pack(pady=5)

        self.duration_label = tk.Label(master, text=f"Duration: {self.config.get('duration_minutes', 10)} minutes")
        self.duration_label.pack(pady=10)

        self.duration_button = tk.Button(master, text="Set Duration (mins)", command=self.set_duration)
        self.duration_button.pack(pady=5)
        
        self.save_button = tk.Button(master, text="Save Settings", command=self.save_config)
        self.save_button.pack(pady=10)

    def load_config(self):
        """Loads configuration from a JSON file."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {"wallpaper_folder": None, "duration_minutes": 10}

    def save_config(self):
        """Saves configuration to a JSON file."""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)
        messagebox.showinfo("Settings Saved", "Configuration has been saved.")
        log("GUI: Settings saved.")
    
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.config["wallpaper_folder"] = folder_path
            self.folder_label.config(text=f"Folder: {os.path.basename(folder_path)}")
            messagebox.showinfo("Folder Selected", f"The wallpaper folder has been set to:\n{self.config['wallpaper_folder']}\n\nRemember to click 'Save Settings'!")

    def set_duration(self):
        try:
            new_duration = simpledialog.askinteger("Set Duration", "Enter duration in minutes:",
                                                  initialvalue=self.config.get('duration_minutes', 10),
                                                  minvalue=1)
            if new_duration is not None:
                self.config["duration_minutes"] = new_duration
                self.duration_label.config(text=f"Duration: {self.config['duration_minutes']} minutes")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

if __name__ == "__main__":
    if "--service" in sys.argv:
        # Run in service mode
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            folder = config.get("wallpaper_folder")
            duration = config.get("duration_minutes")
            if folder and os.path.isdir(folder) and duration:
                run_service(folder, duration)
            else:
                log("Error: Configuration file is invalid or incomplete. Please run the GUI to configure the settings.")
        else:
            log("Error: Configuration file not found. Please run the GUI to configure the settings.")
    else:
        # Run in GUI mode
        root = tk.Tk()
        app = WallpaperChangerApp(root)
        root.mainloop()
