import os
import shutil
import hashlib
import urllib.request
import time
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image, ImageDraw
from plyer import notification
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from win10toast import ToastNotifier
from playsound import playsound
from tkinter import ttk
import ctypes
import json

def update_setting(key):
    settings[key] = settings_vars[key].get()
    save_settings()

# Settings JSON handling
SETTINGS_FILE = "settings.json"

default_settings = {
    "realtime_scan": True,
    "auto_update": True,
    "alerts": True,
    "sound": True
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return default_settings

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# Tooltip class from above
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", "9", "normal"))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# Main GUI
root = tk.Tk()
# Load initial settings
settings = load_settings()
root.title("Antivirus Settings")
root.geometry("350x360")

switches = {
    "Realtime Scanning": ("realtime_scan", "Scan files automatically in real-time."),
    "Auto-update Definitions": ("auto_update", "Automatically update virus definitions."),
    "Notification Alerts": ("alerts", "Show notifications when threats are detected."),
    "Sound Effects": ("sound", "Play sound alerts on virus detection.")
}
switch_vars = {}

# Apply initial background color at startup
root.configure(bg=settings.get("background_color", "white"))
# === Integrated Settings Section ===
integrated_settings_frame = tk.LabelFrame(root, text="⚙ Integrated Settings", padx=10, pady=10, font=("Arial", 11, "bold"))
integrated_settings_frame.pack(fill="x", padx=15, pady=10)

# Settings Variables
settings_vars = {
    "background_color": tk.StringVar(value="white"),
    "auto_update": tk.BooleanVar(value=settings.get("auto_update", True)),
    "alerts": tk.BooleanVar(value=settings.get("alerts", True)),
    "sound": tk.BooleanVar(value=settings.get("sound", True))
}

# Background Color setting
tk.Label(integrated_settings_frame, text="Background Color:", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=5)
bg_color_menu = ttk.Combobox(integrated_settings_frame, values=["white", "lightgray", "skyblue", "black", "orange", "tomato"], textvariable=settings_vars["background_color"])
bg_color_menu.grid(row=0, column=1, pady=5, padx=5)

def apply_bg_color(event):
    selected_color = settings_vars["background_color"].get()
    root.configure(bg=selected_color)
    settings["background_color"] = selected_color
    save_settings()

bg_color_menu.bind("<<ComboboxSelected>>", apply_bg_color)

# Auto-update Definitions
auto_update_chk = tk.Checkbutton(
    integrated_settings_frame,
    text="Auto-update Definitions",
    variable=settings_vars["auto_update"],
    command=lambda: update_setting("auto_update"),
    font=("Arial", 10),
)
auto_update_chk.grid(row=1, column=0, columnspan=2, sticky='w', pady=2)

# Notification Alerts
alerts_chk = tk.Checkbutton(
    integrated_settings_frame,
    text="Notification Alerts",
    variable=settings_vars["alerts"],
    command=lambda: update_setting("alerts"),
    font=("Arial", 10),
)
alerts_chk.grid(row=2, column=0, columnspan=2, sticky='w', pady=2)

# Sound Effects
sound_chk = tk.Checkbutton(
    integrated_settings_frame,
    text="Sound Effects",
    variable=settings_vars["sound"],
    command=lambda: update_setting("sound"),
    font=("Arial", 10),
)
sound_chk.grid(row=3, column=0, columnspan=2, sticky='w', pady=2)

# Tooltip for new integrated settings
Tooltip(auto_update_chk, "Automatically updates virus definitions periodically.")
Tooltip(alerts_chk, "Displays a notification alert upon detecting threats.")
Tooltip(sound_chk, "Plays an alert sound upon virus detection.")
Tooltip(bg_color_menu, "Changes the background color of the main window.")


def toggle_switch(feature):
    settings[switches[feature][0]] = switch_vars[feature].get()
    save_settings()

# Create switches with tooltips
for feature, (setting_key, tooltip_text) in switches.items():
    var = tk.BooleanVar(value=settings[setting_key])
    chk = ttk.Checkbutton(root, text=feature, variable=var,
                          command=lambda f=feature: toggle_switch(f))
    chk.pack(anchor='w', pady=8, padx=20)
    switch_vars[feature] = var
    Tooltip(chk, tooltip_text)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", "9", "normal"))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    # Default settings
    return {
        "realtime_enabled": True,
        "window_geometry": "850x700+100+100"
    }

def save_config():
    config = {
        "realtime_enabled": realtime_enabled.get(),
        "window_geometry": root.geometry()
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


scan_paused = threading.Event()
scan_stopped = threading.Event()

UPDATE_INTERVAL_MINUTES = 5
def start_auto_update():
    def updater():
        while True:
            fetch_and_update_hashes()
            time.sleep(UPDATE_INTERVAL_MINUTES * 60)
    threading.Thread(target=updater, daemon=True).start()

def show_toast_overlay(message, duration=3, bg="#003366", fg="white"):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(bg=bg)

    x = root.winfo_x() + 20
    y = root.winfo_y() + root.winfo_height() - 100
    toast.geometry(f"+{x}+{y}")

    tk.Label(toast, text=message, bg=bg, fg=fg, font=("Arial", 10, "bold"), padx=20, pady=10).pack()
    toast.after(duration * 1000, toast.destroy)

def custom_popup(title, message, bg="#ffcccc", fg="black", icon="⚠️", auto_close=0):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("350x150")
    popup.resizable(False, False)
    popup.configure(bg=bg)
    popup.attributes("-topmost", True)

    icon_label = tk.Label(popup, text=icon, font=("Arial", 28), bg=bg, fg=fg)
    icon_label.pack(pady=(10, 0))

    msg_label = tk.Label(popup, text=message, font=("Arial", 11), wraplength=300, bg=bg, fg=fg)
    msg_label.pack(pady=5)

    ok_button = tk.Button(popup, text="OK", command=popup.destroy)
    ok_button.pack(pady=(5, 10))

    if auto_close > 0:
        popup.after(auto_close * 1000, popup.destroy)


def alert_with_sound_and_blink(label, message="⚠️ Threat Detected!", sound_path="virus_sd2.wav", times=6):
    def blinker():
        for i in range(times):
            label.config(text=message, bg="red", fg="white")
            try:
                playsound(sound_path)
            except Exception as e:
                print("Sound error:", e)
            time.sleep(0.4)
            label.config(bg="yellow", fg="black")
            time.sleep(0.4)
        label.config(text="", bg=root["bg"])  # Reset
    threading.Thread(target=blinker, daemon=True).start()

def stop_scan():
    scan_stopped.set()
    output_box.insert(tk.END, "🛑 Scan stopped by user.\n")


def toggle_pause():
    if scan_paused.is_set():
        scan_paused.clear()
        pause_button.config(text="⏸ Pause Scan")
        output_box.insert(tk.END, "▶️ Scan Resumed\n")
    else:
        scan_paused.set()
        pause_button.config(text="▶️ Resume Scan")
        output_box.insert(tk.END, "⏸ Scan Paused\n")

AUTO_SCAN_INTERVAL = 10  # minutes
def auto_scan():
    def scanner():
        while True:
            folder = folder_entry.get()
            if folder and os.path.isdir(folder):
                output_box.insert(tk.END, f"\n[Auto Scan] Scanning folder: {folder}\n")
                scan_directory(folder, output_box)
            else:
                output_box.insert(tk.END, "\n[Auto Scan] Skipped (no folder selected).\n")
            time.sleep(AUTO_SCAN_INTERVAL * 60)
    threading.Thread(target=scanner, daemon=True).start()

class CircularProgressDonut:
    def __init__(self, parent, size=120, width=15):
        self.parent = parent
        self.size = size
        self.width = width
        self.canvas = tk.Canvas(parent, width=size, height=size, highlightthickness=0, bg="white")
        self.canvas.pack(pady=10)

        # Outer arc (progress ring)
        self.arc = self.canvas.create_arc(
            width, width, size - width, size - width,
            start=90, extent=0, style="arc", width=width, outline="green"
        )

        # Inner percent label
        self.percent_text = self.canvas.create_text(
            size // 2, size // 2,
            text="0%", font=("Helvetica", 14, "bold"), fill="black"
        )

    def update_progress(self, percent):
        # Color transition: Red → Orange → Yellow → Green
        def get_color(p):
            if p < 25:
                return "#FF3333"  # Red
            elif p < 50:
                return "#FF9933"  # Orange
            elif p < 75:
                return "#FFDD33"  # Yellow
            else:
                return "#33CC33"  # Green

        extent = (percent / 100) * -360  # Negative for clockwise
        color = get_color(percent)

        self.canvas.itemconfig(self.arc, extent=extent, outline=color)
        self.canvas.itemconfig(self.percent_text, text=f"{int(percent)}%")

    def hide(self):
        self.canvas.pack_forget()

    def show(self):
        self.canvas.pack(pady=10)

def play_alert_sound():
    try:
        playsound("./virus_sd2.wav")  # Replace with your sound file path
    except Exception as e:
        print("Sound error:", e)

toaster = ToastNotifier()
def show_notification(title, message):
    try:
        toaster.show_toast(title, message, icon_path=None, duration=5, threaded=True)
    except:
        print("Balloon notification failed, falling back to console log.")
        print(title + ": " + message)

def flash_tray_icon(icon, flash_count=6, interval=0.5):
    def flasher():
        original_image = icon.icon
        blank_image = Image.new('RGB', (64, 64), "white")
        for _ in range(flash_count):
            icon.icon = blank_image
            time.sleep(interval)
            icon.icon = original_image
            time.sleep(interval)
    threading.Thread(target=flasher, daemon=True).start()

def setup_tray():
    global tray_icon_ref
    icon_image = create_image()
    menu = TrayMenu(
        TrayMenuItem("Show Antivirus", on_show),
        TrayMenuItem("Quit", on_quit)
    )
    tray_icon_ref = TrayIcon("Antivirus", icon_image, "Python Antivirus", menu)
    threading.Thread(target=tray_icon_ref.run, daemon=True).start()


# === CONFIG ===
#VIRUS_DB_URL = "https://github.com/Rajapakar/sict/blob/main/mainsict.txt"  # inCorrect Replace with your raw file URL
#VIRUS_DB_URL = "https://raw.githubusercontent.com/Rajapakar/sict/main/mainsict.txt"  # ✅ Correct, Replace with your raw file URL

VIRUS_DB_URL = "https://github.com/Rajapakar/sict/blob/main/virus-signatures.txt"
virus_hashes = set()
last_update_time = ""

def fetch_and_update_hashes():
    global virus_hashes, last_update_time
    try:
        with urllib.request.urlopen(VIRUS_DB_URL) as response:
            data = response.read().decode('utf-8')
            virus_hashes = set(
                line.strip() for line in data.splitlines() if line.strip()
            )
        last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ Virus DB Updated: {last_update_time} | Signatures: {len(virus_hashes)}")
    except Exception as e:
        print(f"⚠️ Error updating Virus DB: {e}")

# Test the function:
fetch_and_update_hashes()

# === CORE FUNCTIONS ===
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5  # seconds
    )


def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        return sha256.hexdigest()
    except Exception as e:
        return None

def fetch_and_update_hashes():
    global virus_hashes, last_update_time
    try:
        response = urllib.request.urlopen(VIRUS_DB_URL)
        data = response.read().decode('utf-8')
        virus_hashes = set(line.strip() for line in data.strip().splitlines() if line.strip())
        last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")
        update_label.config(text=f"✅ AntiVirus Updated: {last_update_time}")
    except Exception as e:
        update_label.config(text=f"⚠️ Error updating DB: {e}")

def scan_directory(directory, output_box, progress_widget=None):
    global infected_files
    infected_files = []
    output_box.insert(tk.END, f"Scanning directory: {directory}\n\n")

    # Count total files first
    all_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            all_files.append(os.path.join(root, filename))

    total = len(all_files)
    if total == 0:
        output_box.insert(tk.END, "No files found to scan.\n")
        return

    for i, filepath in enumerate(all_files):

        # 🟡 Check for pause
        while scan_paused.is_set():
            time.sleep(0.2)  # Wait while paused

        # 🔴 Check for stop (optional if you want stop functionality)
        if scan_stopped.is_set():
            output_box.insert(tk.END, "\n⚠️ Scan Stopped.\n")
            return

        file_hash = calculate_sha256(filepath)
        if file_hash:
            if file_hash in virus_hashes:
                msg = f"[!] Infected: {filepath}\n"
                infected_files.append(filepath)
            else:
                msg = f"[+] Safe: {filepath}\n"
            output_box.insert(tk.END, msg)
            output_box.see(tk.END)

        # Update donut percent
        if progress_widget:
            percent = ((i + 1) / total) * 100
            progress_widget.update_progress(percent)

    output_box.insert(tk.END, "\nScan completed.\n")
    if infected_files:
        output_box.insert(tk.END, "Infected files found:\n")
        for file in infected_files:
            output_box.insert(tk.END, f" - {file}\n")
    else:
        output_box.insert(tk.END, "No infected files detected.\n")
        custom_popup("Scan Completed", "✅ No threats found.", bg="#e6ffe6", fg="darkgreen", icon="✅", auto_close=4)
    output_box.see(tk.END)

def delete_infected_files(output_box):
    if not infected_files:
        messagebox.showinfo("Info", "No infected files to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all infected files?")
    if not confirm:
        return

    deleted = []
    for file in infected_files:
        try:
            os.remove(file)
            deleted.append(file)
        except Exception as e:
            output_box.insert(tk.END, f"❌ Failed to delete {file}: {e}\n")

    output_box.insert(tk.END, "\n🗑️ Deleted files:\n")
    for file in deleted:
        output_box.insert(tk.END, f" - {file}\n")
    infected_files.clear()

def quarantine_files(output_box):
    if not infected_files:
        messagebox.showinfo("Info", "No infected files to quarantine.")
        return

    quarantine_dir = os.path.join(os.getcwd(), "quarantine")
    os.makedirs(quarantine_dir, exist_ok=True)

    moved = []
    for file in infected_files:
        try:
            filename = os.path.basename(file)
            shutil.move(file, os.path.join(quarantine_dir, filename))
            moved.append(file)
        except Exception as e:
            output_box.insert(tk.END, f"❌ Failed to quarantine {file}: {e}\n")

    output_box.insert(tk.END, f"\n📁 Moved {len(moved)} files to quarantine folder.\n")
    infected_files.clear()

# === GUI FUNCTIONS ===
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def start_scan():
    folder = folder_entry.get()
    output_box.delete('1.0', tk.END)
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("Error", "Please select a valid folder or drive to scan.")
        return

    progress_donut.show()
    progress_donut.update_progress(0)

    def run_scan():
        scan_directory(folder, output_box, progress_donut)
        progress_donut.hide()
        progress.stop()
        progress.pack_forget()
    threading.Thread(target=run_scan, daemon=True).start()

    # Start spinner
    progress.pack(pady=5)
    progress.start()

# === GUI SETUP ===
class CircularSpinner:
    def __init__(self, parent, size=20, speed=100):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=size, height=size + 30, highlightthickness=0, bg="white")
        self.arc = self.canvas.create_arc(5, 5, size - 5, size - 5, start=0, extent=40, style='arc', width=5)
        self.glow = self.canvas.create_oval(8, 8, size - 8, size - 8, outline="", fill="", width=0)
        self.label = self.canvas.create_text(size // 2, size + 10, text="🔍 Scanning...", font=("Helvetica", 10),
                                             fill="#000")

        self.angle = 0
        self.speed = speed
        self.running = False
        self.colors = ["red", "orange", "gold", "green", "blue", "purple", "cyan"]
        self.color_index = 0
        self.fade_level = 0
        self.fade_direction = 1

    def start(self):
        self.running = True
        self.canvas.pack(pady=2)
        self.animate()

    def animate(self):
        if self.running:
            # Spinner rotation
            self.angle = (self.angle + 15) % 360
            self.color_index = (self.color_index + 1) % len(self.colors)
            color = self.colors[self.color_index]
            self.canvas.itemconfig(self.arc, start=self.angle, outline=color)

            # Fading glow
            glow_color = self._hex_with_alpha(color, self.fade_level)
            self.canvas.itemconfig(self.glow, fill=glow_color)
            self.fade_level += 10 * self.fade_direction
            if self.fade_level >= 150 or self.fade_level <= 50:
                self.fade_direction *= -1

            # Text fade (optional visual polish)
            text_color = self._hex_with_alpha("#000000", self.fade_level)
            self.canvas.itemconfig(self.label, fill=text_color)

            self.canvas.after(self.speed, self.animate)

    def _hex_with_alpha(self, hex_color, alpha):
        """Convert color and alpha into hex rgba-like value for tkinter-compatible glow"""
        from PIL import ImageColor
        try:
            r, g, b = ImageColor.getrgb(hex_color)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def stop(self):
        self.running = False
        self.canvas.pack_forget()

config = load_config()  # Load config first

root = tk.Tk()
# Apply saved geometry (size & position)
root.iconbitmap('sictimg.ico')
root.geometry(config.get("window_geometry", "850x700"))
# After root = tk.Tk()
root.update_idletasks()
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
style &= ~0x00010000  # WS_MAXIMIZEBOX
ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)

root.title("ANTIVIRUS TOTAL SECURITY [ Powered by SICT ]")
root.iconbitmap('sictimg.ico')
root.geometry("850x700")

# === COLOR BANNER ===
banner_frame = tk.Frame(root, bg="#003366", height=70)
banner_frame.pack(fill=tk.X)
banner_label = tk.Label(banner_frame, text="🛡️ TOTAL SECURITY PROTECTION-ON", fg="white", bg="#003366",
                        font=("Arial", 18, "bold"))
banner_label.pack(pady=10)

# Spinner
spinner = CircularSpinner(root)

# Folder selection
folder_frame = tk.Frame(root)
folder_frame.pack(pady=10)

folder_entry = tk.Entry(folder_frame, width=60)
folder_entry.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(folder_frame, text="📁 Select Drive/ Folder", command=select_folder)
browse_button.pack(side=tk.LEFT)

button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=10)

# Left side buttons frame
left_button_frame = tk.Frame(button_frame)
left_button_frame.pack(side="left")

# Right side button frame
right_button_frame = tk.Frame(button_frame)
right_button_frame.pack(side="right")

# Left Buttons
scan_button = tk.Button(
    left_button_frame, text="🚀 Scan for Viruses",
    command=start_scan, bg="darkred", fg="white",
    width=20, font=("Arial", 10, "bold")
)
scan_button.pack(side="left", padx=5)

pause_button = tk.Button(
    left_button_frame, text="⏸ Pause Scan",
    command=toggle_pause, bg="blue", fg="white",
    width=15
)
pause_button.pack(side="left", padx=5)

status_label = tk.Label(root, text="")
status_label.pack()

# Output Box
output_box = scrolledtext.ScrolledText(root, width=100, height=15, font=("Consolas", 8),
                                       bg="#f0f8ff", fg="#000", insertbackground="black", borderwidth=2, relief="sunken")

output_box.pack(padx=10, pady=10)

# Update label
update_label = tk.Label(root, text="Virus DB: Not updated yet", fg="blue")
update_label.pack(pady=5)

# Real-Time scanning toggle (persisted)
realtime_enabled = tk.BooleanVar(value=config.get("realtime_enabled", True))

def toggle_realtime():
    if realtime_enabled.get():
        status_label.config(text="🟢 Real-Time Scanning: ON")
    else:
        status_label.config(text="🔴 Real-Time Scanning: OFF")
    save_config()  # Save immediately on toggle

realtime_check = tk.Checkbutton(
    root,
    text="Enable Real-Time Scanning",
    variable=realtime_enabled,
    command=toggle_realtime,
    font=("Arial", 10, "bold"),
    anchor="w"
)
realtime_check.pack(pady=2)

# Initial status update
status_label.config(
    text="🟢 Real-Time Scanning: ON" if realtime_enabled.get() else "🔴 Real-Time Scanning: OFF"
)


# Action Buttons
action_frame = tk.Frame(root)
action_frame.pack(pady=5)

delete_button = tk.Button(action_frame, text="❌ Delete Infected Files", command=lambda: delete_infected_files(output_box), bg="maroon", fg="white")
delete_button.pack(side=tk.LEFT, padx=10)

quarantine_button = tk.Button(action_frame, text="📦 Quarantine Infected Files", command=lambda: quarantine_files(output_box), bg="orange", fg="black")
quarantine_button.pack(side=tk.LEFT)

# Progress Donut
progress_donut = CircularProgressDonut(root)
progress_donut.hide()

# === FOOTER ===
footer_frame = tk.Frame(root, bg="#003366", height=30)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
footer_label = tk.Label(footer_frame, text="© 2025 ( ISO 9001-2015 Certified ) SMART INSTITUTE OF COMPUTER TECHNOLOGY – All rights reserved", bg="#003366", fg="white",
                        font=("Arial", 9))
footer_label.pack(pady=6)

def create_image():
    image = Image.new('RGB', (64, 64), "red")
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, 56, 56), fill="white")
    draw.text((18, 18), "AV", fill="black")
    return image

def on_quit(icon, item):
    save_config()  # Save window geometry & settings
    root.destroy()

# Handle manual window close too:
root.protocol("WM_DELETE_WINDOW", lambda: on_quit(tray_icon_ref, None))

def on_show(icon, item):
    root.after(0, root.deiconify)

def setup_tray():
    icon_image = create_image()
    menu = TrayMenu(
        TrayMenuItem("Show Antivirus", on_show),
        TrayMenuItem("Quit", on_quit)
    )
    icon = TrayIcon("Antivirus", icon_image, "Python Antivirus", menu)
    threading.Thread(target=icon.run, daemon=True).start()
# Run GUI
show_toast_overlay("✅ SICT INDIA AntiVirus updated successfully!")
progress = ttk.Progressbar(root, mode='indeterminate', length=200)
footer_label.pack(pady=5)

# Initial setups
tray_icon_ref = None
setup_tray()
start_auto_update()
auto_scan()
root.mainloop()
