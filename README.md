# Royal Clock - Clash of Clans Disconnect Monitor

A Windows application that monitors your Clash of Clans activity and warns you before you get disconnected due to inactivity.

![Alert Popup](alert.png)

## Features

-  **4-minute warning timer** - Alerts you before the 5-minute disconnect
-  **Smart game detection** - Only triggers when Clash of Clans is actually running
-  **Audio alert** - Plays a sound when warning appears
-  **Visual popup** - Shows a character image popup in bottom-right corner
-  **Accurate detection** - Uses window class detection to avoid false positives
-  **Clean GUI** - Simple, modern interface with real-time status updates

## How to Use

1. **Run the application** - Double-click `RoyalClock_Simple.exe`
2. **Start monitoring** - Click the "STOPPED" button to begin monitoring
3. **Play Clash of Clans** - Switch to your game
4. **Alt+Tab away** - The timer starts when you leave the game
5. **Get warned** - After 4 minutes, you'll get a popup and sound alert

## Files

- `RoyalClock_Simple.exe` - The main application (ready to run)
- `royalclock_safe.py` - Source code

## Requirements

- Windows 10/11
- Clash of Clans running on your computer (currently only via emulator)

## Technical Details

- Built with Python and tkinter
- Uses pygame for audio playback
- Monitors active window titles and classes
- Packaged with PyInstaller for easy distribution

## Troubleshooting

- **Timer not starting?** Make sure Clash of Clans is actually running and active
- **False positives?** The app uses advanced detection to avoid triggering on YouTube videos or web searches
- **No sound?** Check your system volume and audio settings

---

*Keep your Clash of Clans sessions active and never get disconnected again!*
