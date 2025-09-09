import time
import tkinter as tk
from tkinter import ttk, PhotoImage
import pygetwindow as gw
from threading import Thread
import pygame
import os
from PIL import Image, ImageTk
import sys

# SETTINGS
# Game detection settings
GAME_WINDOW_CLASSES = ["UnityWndClass", "UnityWindow", "CoCWindow"]  # Common Clash of Clans window classes
GAME_TITLE_KEYWORDS = ["clash of clans", "coc"]  # Keywords that might appear in game titles
EXCLUDE_WINDOWS = ["Royal Clock", "RoyalClock", "YouTube", "Google Chrome", "Mozilla Firefox", "Microsoft Edge", "Safari", "Opera", "Brave", "Vivaldi", "Chromium", "BlueStacks", "NoxPlayer", "LDPlayer", "MEmu"]
WARNING_MINUTES = 4

# Initialize pygame mixer for audio
pygame.mixer.init()

# Global variables
monitoring = False
countdown_thread = None
countdown_running = False
game_active = False
monitor_thread = None
time_remaining = 0

class RoyalClockGUI:
    def __init__(self, root):
        self.root = root
        self.running = True
        self.monitor_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        # Main window setup
        self.root.title("Royal Clock - Clash of Clans Disconnect Monitor")
        self.root.geometry("400x450")
        self.root.configure(bg='#f5f5f5')
        self.root.resizable(False, False)
        
        # Set app icon
        try:
            # Try ICO file first for better quality
            icon_path = "icon.ico"
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            
            if os.path.exists(icon_path):
                print("Loading app icon from ICO file...")
                self.root.iconbitmap(icon_path)
                print("App icon loaded successfully from ICO")
            else:
                # Fallback to PNG
                icon_path = "icon.png"
                if getattr(sys, 'frozen', False):
                    icon_path = os.path.join(sys._MEIPASS, "icon.png")
                
                if os.path.exists(icon_path):
                    print("Loading app icon from PNG file...")
                    pil_icon = Image.open(icon_path)
                    # Use larger size for better quality
                    pil_icon = pil_icon.resize((32, 32), Image.Resampling.LANCZOS)
                    icon_image = ImageTk.PhotoImage(pil_icon)
                    self.root.iconphoto(False, icon_image)
                    print(f"App icon loaded from PNG: {icon_image.width()}x{icon_image.height()}")
                else:
                    print(f"No icon file found at: {icon_path}")
        except Exception as e:
            print(f"Could not load app icon: {e}")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Keep window in normal Windows system - no title bar modifications
        self.root.overrideredirect(False)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='white', relief='flat', bd=1)
        main_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # No custom title bar - use Windows title bar only
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=15)
        
        # Character icon
        try:
            print("Attempting to load icon.png for header...")
            icon_path = "icon.png"
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, "icon.png")
            print(f"Looking for icon at: {icon_path}")
            pil_image = Image.open(icon_path)
            # Resize to a reasonable size for the header
            pil_image = pil_image.resize((32, 32), Image.Resampling.LANCZOS)
            character_image = ImageTk.PhotoImage(pil_image)
            print(f"Header image loaded successfully: {character_image.width()}x{character_image.height()}")
            character_label = tk.Label(header_frame, image=character_image, bg='white')
            character_label.image = character_image  # Keep a reference
        except Exception as e:
            # Fallback to text if image not found
            print(f"Failed to load icon.png: {e}")
            character_label = tk.Label(header_frame, text="⚔️", font=("Arial", 16), bg='white', fg='#0078d4')
        character_label.pack(side='left')
        
        # Title
        title_label = tk.Label(header_frame, text="Royal Clock - Clash of Clans\nDisconnect Monitor", 
                              font=("Arial", 12, "bold"), bg='white', fg='#333333', justify='left')
        title_label.pack(side='left', padx=(10, 0))
        
        # Status button (clickable) with shadow effect
        self.status_frame = tk.Frame(main_frame, bg='white')
        self.status_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Create shadow effect with a darker frame behind the button
        shadow_frame = tk.Frame(self.status_frame, bg='#d0d0d0', height=2)
        shadow_frame.pack(fill='x', pady=(2, 0))
        
        self.status_badge = tk.Button(self.status_frame, text="STOPPED", 
                                    font=("Segoe UI", 14, "bold"), bg='#f3f3f3', fg='#323130',
                                    relief='raised', bd=1, padx=24, pady=12,
                                    command=self.toggle_monitoring, cursor='hand2',
                                    activebackground='#e1dfdd', activeforeground='#323130',
                                    highlightthickness=0, borderwidth=1)
        self.status_badge.pack(expand=True, fill='x')
        
        # Info text
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill='x', padx=15, pady=(0, 20))
        
        info_text = tk.Label(info_frame, text="Click STOPPED button to start monitoring\nWarning will appear after 4 minutes of inactivity",
                           font=("Arial", 10), bg='white', fg='#666666', justify='left')
        info_text.pack(anchor='w')
        
        # Separator
        separator1 = tk.Frame(main_frame, bg='#e0e0e0', height=1)
        separator1.pack(fill='x', padx=15, pady=5)
        
        # Game status section
        status_section = tk.Frame(main_frame, bg='white')
        status_section.pack(fill='x', padx=15, pady=10)
        
        self.game_status_dot = tk.Label(status_section, text="●", font=("Arial", 12), 
                                      bg='white', fg='#e0e0e0')
        self.game_status_dot.pack(side='left')
        
        self.game_status_text = tk.Label(status_section, text="Game Status: Inactive", 
                                       font=("Arial", 10), bg='white', fg='#333333')
        self.game_status_text.pack(side='left', padx=(5, 0))
        
        # Timer section
        timer_section = tk.Frame(main_frame, bg='white')
        timer_section.pack(fill='x', padx=15, pady=(5, 10))
        
        self.timer_label = tk.Label(timer_section, text="⏰ Timer: Not Running", 
                                   font=("Arial", 10, "bold"), bg='white', fg='#666666')
        self.timer_label.pack(anchor='w')
        
        self.timer_progress = tk.Frame(timer_section, bg='#e0e0e0', height=8, relief='flat')
        self.timer_progress.pack(fill='x', pady=(5, 0))
        
        self.timer_bar = tk.Frame(self.timer_progress, bg='#4CAF50', height=6)
        self.timer_bar.pack(side='left', fill='y')
        
        # Separator
        separator2 = tk.Frame(main_frame, bg='#e0e0e0', height=1)
        separator2.pack(fill='x', padx=15, pady=5)
        
        # Instructions section
        instructions_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='flat', bd=1)
        instructions_frame.pack(fill='x', padx=15, pady=10)
        
        instructions_text = tk.Label(instructions_frame,
                                   text="Instructions:\n1. Click STOPPED button to start monitoring\n2. Switch to Clash of Clans\n3. Alt-tab away to start timer\n4. Warning popup appears before disconnect",
                                   font=("Arial", 9), bg='#f8f9fa', fg='#333333',
                                   justify='left')
        instructions_text.pack(pady=10, padx=10)
        
        # Safety info
        safety_frame = tk.Frame(main_frame, bg='white')
        safety_frame.pack(fill='x', padx=15, pady=(10, 15))
        
        safety_text = tk.Label(safety_frame, text="⚠️ Close this window to stop all monitoring", 
                             font=("Arial", 9), bg='white', fg='#dc2626', justify='center')
        safety_text.pack()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start monitoring thread
        self.start_monitor_thread()
        
    def on_closing(self):
        """Safely close the application"""
        global monitoring, countdown_running
        monitoring = False
        countdown_running = False
        self.running = False
        self.root.destroy()
        
    def minimize_window(self):
        """Minimize the window to taskbar"""
        # Since we're using normal Windows system, we can use normal minimize
        self.root.iconify()
        print("Window minimized to taskbar")
        
    def restore_window(self):
        """Restore the window from minimized state"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        print("Window restored")
        
    # Drag functions removed - using Windows title bar
        
    def toggle_monitoring(self):
        global monitoring
        monitoring = not monitoring
        
        if monitoring:
            self.status_badge.config(text="MONITORING", bg='#3b82f6', fg='white')
            print("🟢 Monitoring started")
        else:
            self.status_badge.config(text="STOPPED", bg='#f3f3f3', fg='#323130')
            print("🔴 Monitoring stopped")
            global countdown_running
            countdown_running = False
    
    def start_monitor_thread(self):
        """Start the monitoring thread"""
        self.monitor_thread = Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        global countdown_running, game_active, monitoring
        coc_was_active = False
        
        print("🔍 Monitoring started - looking for Clash of Clans window...")
        
        while self.running:
            try:
                if monitoring:
                    active = gw.getActiveWindow()
                    coc_is_active = False
                    
                    if active:
                        title = active.title
                        window_class = getattr(active, 'className', '') or ''
                        print(f"📱 Active window: '{title}' (Class: '{window_class}')")
                        
                        # Method 1: Check window class (most reliable for games)
                        is_game_by_class = any(game_class.lower() in window_class.lower() for game_class in GAME_WINDOW_CLASSES)
                        
                        # Method 2: Check if it's excluded (browsers, our app, etc.)
                        is_excluded = any(exclude.lower() in title.lower() for exclude in EXCLUDE_WINDOWS)
                        
                        # Method 3: Check if title contains game keywords but is not excluded
                        has_game_keywords = any(keyword.lower() in title.lower() for keyword in GAME_TITLE_KEYWORDS)
                        is_game_by_title = has_game_keywords and not is_excluded
                        
                        # Final detection: either by class OR by title (but not excluded)
                        is_coc_game = is_game_by_class or is_game_by_title
                        coc_is_active = is_coc_game
                        
                        if is_coc_game:
                            if is_game_by_class:
                                print("✅ Clash of Clans GAME detected by window class!")
                            else:
                                print("✅ Clash of Clans GAME detected by title!")
                        elif is_excluded:
                            if "royal clock" in title.lower():
                                print("📱 Our Royal Clock app - IGNORED")
                            elif any(browser in title.lower() for browser in ["chrome", "firefox", "edge", "safari", "opera", "brave"]):
                                print("🌐 Browser window - IGNORED")
                            elif any(launcher in title.lower() for launcher in ["bluestacks", "nox", "ldplayer", "memu"]):
                                print("🎮 Emulator launcher - IGNORED")
                            elif "youtube" in title.lower():
                                print("📺 YouTube window - IGNORED")
                            else:
                                print("❌ Excluded window - IGNORED")
                        else:
                            print("❌ Not Clash of Clans game")
                    else:
                        print("📱 No active window detected")
                    
                    # Update game status
                    if coc_is_active != game_active:
                        game_active = coc_is_active
                        if game_active:
                            print("🟢 Game Status: ACTIVE")
                        else:
                            print("🔴 Game Status: INACTIVE")
                        self.root.after(0, self.update_game_status)
                    
                    # Start timer when CoC was active but now is not
                    if coc_was_active and not coc_is_active and not countdown_running:
                        print("⏰ Starting 4-minute countdown timer...")
                        countdown_running = True
                        Thread(target=self.countdown_timer, daemon=True).start()
                    
                    # Cancel timer when CoC becomes active again
                    elif coc_is_active and countdown_running:
                        print("⏹️ Timer cancelled - game is active again")
                        countdown_running = False
                    
                    coc_was_active = coc_is_active
                else:
                    print("⏸️ Monitoring paused - toggle ON to start")
                    # Reset when not monitoring
                    if game_active:
                        game_active = False
                        self.root.after(0, self.update_game_status)
                    coc_was_active = False
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
            
            time.sleep(1)
    
    def countdown_timer(self):
        """Countdown timer for warning"""
        global countdown_running
        total_seconds = int(WARNING_MINUTES * 60)
        
        for remaining in range(total_seconds, 0, -1):
            if not countdown_running or not monitoring or not self.running:
                # Reset timer display when cancelled
                self.root.after(0, lambda: self.update_timer_display(0))
                return
            # Update timer display
            self.root.after(0, lambda r=remaining: self.update_timer_display(r))
            time.sleep(1)
        
        # Show popup if countdown wasn't cancelled
        if countdown_running and monitoring and self.running:
            self.root.after(0, self.show_popup)
            countdown_running = False
            # Reset timer display after popup
            self.root.after(0, lambda: self.update_timer_display(0))
    
    def show_popup(self):
        """Show warning popup"""
        popup = tk.Toplevel(self.root)
        popup.title("CoC Alert")
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.attributes('-alpha', 1.0)
        popup.configure(bg='black')
        
        try:
            icon_path = "icon.png"
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                icon_path = os.path.join(sys._MEIPASS, "icon.png")
            if os.path.exists(icon_path):
                pil_img = Image.open(icon_path)
                img = ImageTk.PhotoImage(pil_img)
                img_width = img.width()
                img_height = img.height()
                
                screen_width = popup.winfo_screenwidth()
                screen_height = popup.winfo_screenheight()
                x = screen_width - img_width - 20
                y = screen_height - img_height - 20
                
                popup.geometry(f"{img_width}x{img_height}+{x}+{y}")
                
                img_label = tk.Label(popup, image=img, bg='black', highlightthickness=0, bd=0)
                img_label.image = img
                img_label.pack()
                
                popup.attributes('-transparentcolor', 'black')
            else:
                # Fallback popup
                popup.geometry("200x50")
                screen_width = popup.winfo_screenwidth()
                screen_height = popup.winfo_screenheight()
                x = screen_width - 220
                y = screen_height - 70
                popup.geometry(f"200x50+{x}+{y}")
                
                label = tk.Label(popup, text="⚔️ CoC Alert!", 
                               font=("Arial", 12, "bold"), fg="white", bg="#0078d4")
                label.pack(expand=True)
        except Exception as e:
            print(f"Error loading image: {e}")
        
        # Play sound
        try:
            if os.path.exists("alert.mp3"):
                pygame.mixer.music.load("alert.mp3")
                pygame.mixer.music.play()
        except:
            pass
        
        # Auto-close after 5 seconds
        popup.after(5000, popup.destroy)
        popup.mainloop()
    
    def update_game_status(self):
        """Update game status display"""
        if game_active:
            self.game_status_dot.config(fg='#10b981')
            self.game_status_text.config(text="Game Status: Active", font=("Segoe UI", 11, "bold"))
        else:
            self.game_status_dot.config(fg='#e0e0e0')
            self.game_status_text.config(text="Game Status: Inactive", font=("Segoe UI", 11, "normal"))
    
    def update_timer_display(self, remaining_seconds):
        """Update timer display with countdown and progress bar"""
        global time_remaining
        time_remaining = remaining_seconds
        
        if remaining_seconds > 0:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            self.timer_label.config(text=f"⏰ Timer: {minutes:02d}:{seconds:02d} remaining", fg='#dc2626')
            
            # Update progress bar with royal blue theme
            total_seconds = WARNING_MINUTES * 60
            progress = (total_seconds - remaining_seconds) / total_seconds
            bar_width = int(progress * 200)  # 200px max width
            self.timer_bar.config(width=bar_width, bg='#3b82f6')
        else:
            self.timer_label.config(text="⏰ Timer: Not Running", fg='#1e40af')
            self.timer_bar.config(width=0)

def main():
    root = tk.Tk()
    app = RoyalClockGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
