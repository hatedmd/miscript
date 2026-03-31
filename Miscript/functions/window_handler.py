#!/usr/bin/env python3
"""Handle window creation with Tkinter."""

import tkinter as tk
import threading

# Named color mapping
NAMED_COLORS = {
    'red': '#FF0000',
    'green': '#00FF00',
    'blue': '#0000FF',
    'black': '#000000',
    'white': '#FFFFFF',
    'yellow': '#FFFF00',
    'cyan': '#00FFFF',
    'magenta': '#FF00FF',
    'gray': '#808080',
    'grey': '#808080',
    'orange': '#FFA500',
    'purple': '#800080',
    'pink': '#FFC0CB',
    'brown': '#A52A2A',
    'navy': '#000080',
    'lime': '#00FF00',
    'teal': '#008080',
    'maroon': '#800000',
    'olive': '#808000',
    'silver': '#C0C0C0',
    'lightgray': '#D3D3D3',
    'darkgray': '#A9A9A9',
}

def get_color_hex(color_value):
    """Convert color name or hex to hex value."""
    if color_value.startswith('#'):
        return color_value
    color_name = color_value.lower()
    return NAMED_COLORS.get(color_name, 'lightgray')

class Window:
    """Represents a MIS window object."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.window = None
        self.widgets = []
        self.entries = {}
        self.labels = {}
        self.buttons = {}
        self.variables = {}
    
    def create(self):
        """Create the actual Tkinter window."""
        try:
            self.window = tk.Tk()
            self.window.geometry(f"{self.width}x{self.height}")
            self.window.title("MIS Window")
            return True
        except Exception as e:
            print(f"Error creating window: {e}")
            return False
    
    def add_text(self, text, x, y, label_name=None):
        """Add text label to window at coordinates."""
        if self.window:
            try:
                label = tk.Label(
                    self.window, 
                    text=text, 
                    font=("Arial", 16), 
                    bg=self.window['bg'],
                    fg='white'
                )
                label.place(x=x, y=y)
                self.widgets.append(label)
                
                if label_name:
                    self.labels[label_name] = label
                
                return True
            except Exception as e:
                print(f"Error adding text: {e}")
                return False
        return False
    
    def update_label(self, label_name, new_text):
        """Update an existing label's text."""
        if label_name in self.labels and self.window:
            try:
                self.labels[label_name].config(text=new_text)
                self.window.update()
                return True
            except Exception as e:
                print(f"Error updating label: {e}")
                return False
        return False
    
    def add_input(self, var_name, x, y, width_chars=10, max_length=20, variables=None):
        """Add text input field to window."""
        if self.window:
            try:
                entry = tk.Entry(
                    self.window, 
                    font=("Arial", 14), 
                    width=width_chars,
                    bg='white',
                    fg='black'
                )
                entry.place(x=x, y=y)
                
                if max_length:
                    entry.config(validate="key", validatecommand=(entry.register(self._validate_length), f'%P', max_length))
                
                self.entries[var_name] = entry
                
                if variables is not None:
                    self.variables = variables
                    self.entries[var_name + '_var'] = variables
                
                self.widgets.append(entry)
                return True
            except Exception as e:
                print(f"Error adding input: {e}")
                return False
        return False
    
    def _validate_length(self, new_value, max_length):
        """Validate entry length."""
        if len(new_value) <= int(max_length):
            return True
        return False
    
    def get_input_value(self, var_name):
        """Get the current value from an input field."""
        if var_name in self.entries:
            return self.entries[var_name].get()
        return None
    
    def add_button(self, x, y, text="Click", on_click_callback=None, width=10, length=1, colour='lightgray'):
        """Add button to window with onClick callback and colour support."""
        if self.window:
            try:
                # Convert colour name to hex
                bg_hex = get_color_hex(colour)
                
                # Determine text color based on background brightness
                fg_hex = 'black' if colour.lower() in ['white', 'yellow', 'lightgray', 'pink', 'cyan'] else 'white'
                
                button = tk.Button(
                    self.window, 
                    text=text, 
                    font=("Arial", 12, "bold"),
                    width=width,
                    height=length,
                    command=on_click_callback,
                    bg=bg_hex,
                    fg=fg_hex,
                    activebackground='white',
                    activeforeground='black',
                    relief='raised',
                    bd=3
                )
                button.place(x=x, y=y)
                self.widgets.append(button)
                self.buttons[text] = button
                return True
            except Exception as e:
                print(f"Error adding button: {e}")
                print(f"Colour was: {colour}")
                return False
        return False
    
    def set_background(self, color_type, color_value):
        """Set window background color."""
        if self.window:
            try:
                hex_color = None
                
                if color_type == 'rgb_color':
                    r, g, b = color_value
                    hex_color = f'#{r:02X}{g:02X}{b:02X}'
                elif color_type == 'hex_color':
                    hex_color = color_value
                elif color_type == 'named_color':
                    color_name = color_value.lower()
                    if color_name in NAMED_COLORS:
                        hex_color = NAMED_COLORS[color_name]
                    else:
                        print(f"Unknown color name: {color_name}")
                        return False
                
                if hex_color:
                    self.window.configure(bg=hex_color)
                    for label in self.labels.values():
                        label.config(bg=hex_color)
                    return True
            except Exception as e:
                print(f"Error setting background: {e}")
                return False
        return False
    
    def pack(self):
        """Refresh/update the window display."""
        if self.window:
            try:
                self.window.update()
                return True
            except Exception as e:
                print(f"Error packing window: {e}")
                return False
        return False
    
    def show(self):
        """Display the window."""
        if self.window:
            self.window.mainloop()

# Store all created windows
_windows = {}

def create_window(window_name, width, height):
    """Create a window and store it."""
    window = Window(width, height)
    if window.create():
        _windows[window_name] = window
        return window
    return None

def get_window(window_name):
    """Get a stored window by name."""
    return _windows.get(window_name)

def add_text_to_window(window_name, text, x, y, label_name=None):
    """Add text to a stored window."""
    window = get_window(window_name)
    if window:
        return window.add_text(text, x, y, label_name)
    return False

def update_label_in_window(window_name, label_name, new_text):
    """Update a label in a stored window."""
    window = get_window(window_name)
    if window:
        return window.update_label(label_name, new_text)
    return False

def add_input_to_window(window_name, var_name, x, y, width_chars, max_length, variables):
    """Add input field to a stored window."""
    window = get_window(window_name)
    if window:
        return window.add_input(var_name, x, y, width_chars, max_length, variables)
    return False

def get_input_from_window(window_name, var_name):
    """Get input value from a window field."""
    window = get_window(window_name)
    if window:
        return window.get_input_value(var_name)
    return None

def add_button_to_window(window_name, x, y, text, on_click_callback, width, length, colour):
    """Add button to a stored window with colour support."""
    window = get_window(window_name)
    if window:
        return window.add_button(x, y, text, on_click_callback, width, length, colour)
    return False

def pack_window(window_name):
    """Refresh/update a window."""
    window = get_window(window_name)
    if window:
        return window.pack()
    return False

def set_window_background(window_name, color_type, color_value):
    """Set background color of a stored window."""
    window = get_window(window_name)
    if window:
        return window.set_background(color_type, color_value)
    return False

def show_all_windows():
    """Show all windows."""
    if _windows:
        first_window = list(_windows.values())[0]
        first_window.show()

def wait_for_windows():
    """Wait for all windows to close."""
    show_all_windows()