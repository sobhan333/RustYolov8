import time
import pyautogui

def take_screenshots(interval):
    count = 16
    try:
        while True:
            screenshot = pyautogui.screenshot()
            screenshot.save(f'screenshot_{count}.png')
            print(f'Screenshot {count} taken.')
            count += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped taking screenshots.")

if __name__ == "__main__":
    try:
        interval = float(input("Enter the interval in seconds between screenshots: "))
        print("Taking screenshots... Press Ctrl+C to stop.")
        take_screenshots(interval)
    except ValueError:
        print("Please enter a valid number for the interval.")
