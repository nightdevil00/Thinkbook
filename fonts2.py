import tkinter as tk
from tkinter import messagebox
from tkinter import font
import subprocess
import shlex

class FontSettingsApp:
    """
    A GUI application to change system-wide font settings on Linux
    using the 'gsettings' command, similar to gnome-tweaks.
    This version includes a dynamic search field in the font chooser.
    """

    def __init__(self, root):
        """Initializes the main application window and widgets."""
        self.root = root
        self.root.title("Font Settings GUI")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Set up a dictionary to hold the current font settings
        self.font_settings = {
            'font-name': '',
            'document-font-name': '',
            'monospace-font-name': '',
            'text-scaling-factor': 1.0
        }

        # List of all available fonts on the system
        # We fetch this once at the start to make filtering fast
        self.available_fonts = sorted(font.families())

        # Create a dictionary to hold the selected font for each category
        self.selected_fonts = {
            'font-name': tk.StringVar(value=""),
            'document-font-name': tk.StringVar(value=""),
            'monospace-font-name': tk.StringVar(value="")
        }

        self.scaling_factor = tk.DoubleVar(value=1.0)
        
        self.load_current_settings()
        self.create_widgets()

    def create_widgets(self):
        """Creates and places all the GUI widgets."""
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Application Font Section ---
        app_font_frame = tk.LabelFrame(main_frame, text="Application Font", padx=10, pady=10)
        app_font_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(app_font_frame, textvariable=self.selected_fonts['font-name']).pack(side=tk.LEFT, padx=5)
        tk.Button(app_font_frame, text="Change", command=lambda: self.open_font_chooser('font-name')).pack(side=tk.RIGHT)

        # --- Document Font Section ---
        doc_font_frame = tk.LabelFrame(main_frame, text="Document Font", padx=10, pady=10)
        doc_font_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(doc_font_frame, textvariable=self.selected_fonts['document-font-name']).pack(side=tk.LEFT, padx=5)
        tk.Button(doc_font_frame, text="Change", command=lambda: self.open_font_chooser('document-font-name')).pack(side=tk.RIGHT)

        # --- Monospace Font Section ---
        mono_font_frame = tk.LabelFrame(main_frame, text="Monospace Font", padx=10, pady=10)
        mono_font_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(mono_font_frame, textvariable=self.selected_fonts['monospace-font-name']).pack(side=tk.LEFT, padx=5)
        tk.Button(mono_font_frame, text="Change", command=lambda: self.open_font_chooser('monospace-font-name')).pack(side=tk.RIGHT)

        # --- Scaling Factor Section ---
        scaling_frame = tk.LabelFrame(main_frame, text="Text Scaling Factor", padx=10, pady=10)
        scaling_frame.pack(fill=tk.X, pady=5)
        
        tk.Scale(scaling_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.scaling_factor).pack(fill=tk.X)
        
        # --- Action Buttons ---
        button_frame = tk.Frame(main_frame, pady=20)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Apply", command=self.apply_settings, bg="#4CAF50", fg="white", activebackground="#45a049").pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Reset", command=self.load_current_settings).pack(side=tk.RIGHT, padx=5)

    def load_current_settings(self):
        """Fetches the current font settings from gsettings."""
        try:
            # Get Application Font
            app_font = self.run_gsettings_command('get', 'org.gnome.desktop.interface', 'font-name')
            self.font_settings['font-name'] = app_font.strip().strip("'")
            self.selected_fonts['font-name'].set(self.font_settings['font-name'])
            
            # Get Document Font
            doc_font = self.run_gsettings_command('get', 'org.gnome.desktop.interface', 'document-font-name')
            self.font_settings['document-font-name'] = doc_font.strip().strip("'")
            self.selected_fonts['document-font-name'].set(self.font_settings['document-font-name'])

            # Get Monospace Font
            mono_font = self.run_gsettings_command('get', 'org.gnome.desktop.interface', 'monospace-font-name')
            self.font_settings['monospace-font-name'] = mono_font.strip().strip("'")
            self.selected_fonts['monospace-font-name'].set(self.font_settings['monospace-font-name'])
            
            # Get Scaling Factor
            scaling = self.run_gsettings_command('get', 'org.gnome.desktop.interface', 'text-scaling-factor')
            self.font_settings['text-scaling-factor'] = float(scaling)
            self.scaling_factor.set(self.font_settings['text-scaling-factor'])
            
        except FileNotFoundError:
            messagebox.showerror("Error", "The 'gsettings' command was not found. Please ensure you are on a GNOME or Cinnamon desktop environment.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read gsettings: {e}")

    def open_font_chooser(self, font_type):
        """
        Opens a new Toplevel window to choose a font from the available list.
        This acts as a simple font chooser dialog with dynamic search.
        """
        chooser_window = tk.Toplevel(self.root)
        chooser_window.title(f"Select {font_type.replace('-', ' ').title()}")
        chooser_window.geometry("300x400")

        # --- Search widgets ---
        search_frame = tk.Frame(chooser_window, padx=10, pady=5)
        search_frame.pack(fill=tk.X)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # --- Listbox for fonts ---
        listbox = tk.Listbox(chooser_window)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Function to filter the listbox
        def filter_fonts(event=None):
            search_text = search_entry.get().lower()
            listbox.delete(0, tk.END)
            
            # If the search field is empty, show all fonts
            if not search_text:
                for font_family in self.available_fonts:
                    listbox.insert(tk.END, font_family)
            # Otherwise, show only matching fonts
            else:
                filtered_list = [f for f in self.available_fonts if search_text in f.lower()]
                for font_family in filtered_list:
                    listbox.insert(tk.END, font_family)

        # Bind the filter function to key releases in the search entry
        search_entry.bind('<KeyRelease>', filter_fonts)
        
        # Initially populate the listbox with all fonts
        filter_fonts()
        
        # Pre-select the currently active font
        current_font = self.selected_fonts[font_type].get().split(" ")[0]
        try:
            idx = self.available_fonts.index(current_font)
            # Find the index in the (potentially filtered) listbox
            listbox_items = listbox.get(0, tk.END)
            if current_font in listbox_items:
                current_idx = listbox_items.index(current_font)
                listbox.selection_set(current_idx)
                listbox.see(current_idx)
        except ValueError:
            # Ignore if current font isn't in the list
            pass

        def on_select():
            try:
                selected_font_family = listbox.get(listbox.curselection())
                current_font_string = self.selected_fonts[font_type].get()
                
                # Check if the font string contains a size
                font_parts = current_font_string.split(" ")
                font_size = font_parts[-1] if font_parts[-1].isdigit() else "10" # Default to 10 if size is not found
                
                new_font_string = f"{selected_font_family} {font_size}"
                self.selected_fonts[font_type].set(new_font_string)
                self.font_settings[font_type] = new_font_string
                chooser_window.destroy()
            except tk.TclError:
                messagebox.showerror("Error", "Please select a font from the list.")

        tk.Button(chooser_window, text="Select", command=on_select).pack(pady=10)

    def apply_settings(self):
        """Applies the new settings using gsettings."""
        try:
            # Set Application Font
            self.run_gsettings_command('set', 'org.gnome.desktop.interface', 'font-name', f"'{self.selected_fonts['font-name'].get()}'")
            
            # Set Document Font
            self.run_gsettings_command('set', 'org.gnome.desktop.interface', 'document-font-name', f"'{self.selected_fonts['document-font-name'].get()}'")
            
            # Set Monospace Font
            self.run_gsettings_command('set', 'org.gnome.desktop.interface', 'monospace-font-name', f"'{self.selected_fonts['monospace-font-name'].get()}'")
            
            # Set Scaling Factor
            self.run_gsettings_command('set', 'org.gnome.desktop.interface', 'text-scaling-factor', str(self.scaling_factor.get()))
            
            messagebox.showinfo("Success", "Font settings have been applied. You may need to restart applications to see the changes.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")

    def run_gsettings_command(self, action, schema, key, value=None):
        """
        Runs a gsettings command and returns the output.
        Handles both 'get' and 'set' actions.
        """
        command = ['gsettings', action, schema, key]
        if value:
            # Use shlex.split to handle values with spaces or quotes correctly
            command.extend(shlex.split(value))
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()


if __name__ == "__main__":
    root = tk.Tk()
    app = FontSettingsApp(root)
    root.mainloop()

