import numpy as np
from ultralytics import YOLO
import mss
import ctypes
import cv2
import math
import time
from pynput import mouse

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MouseController:
    def __init__(self, sensitivity=1.0):  # Default sensitivity
        self.sensitivity = sensitivity
        self.is_aiming = False  # Track aiming state
        # Load your YOLOv8 model (replace with your path)
        self.model = YOLO(r'C:\Users\sug\Documents\code\runs\detect\train4\weights\best.pt')

        # Define the screen capture region for the full 1920x1080 screen
        self.monitor = {
            "top": 0,
            "left": 0,
            "width": 1920,
            "height": 1080,
        }

        # Initialize screen capture
        self.sct = mss.mss()

        # Get the handle for user32
        self.user32 = ctypes.windll.user32

    def move_mouse(self, pos):
        """Move the mouse cursor to the specified position using mouse_event."""
        current_pos = POINT()
        self.user32.GetCursorPos(ctypes.byref(current_pos))  # Get current mouse position

        # Calculate the delta for movement
        dx = int((pos[0] - current_pos.x) * self.sensitivity)
        dy = int((pos[1] - current_pos.y) * self.sensitivity)
        
        # Move the mouse cursor
        self.user32.mouse_event(0x0001, dx, dy, 0, 0)

    def aim_at_closest_object(self, detections):
        """Aim at the closest detected object to the center of the screen."""
        screen_center = (self.monitor['width'] // 2, self.monitor['height'] // 2)
        closest_object = None
        min_distance = float('inf')

        for result in detections:
            boxes = result.boxes
            
            for box in boxes:
                x, y, w, h = box.xywh[0]
                obj_center = (int(x), int(y))

                # Adjust the aiming point to be very close to the top of the box
                aim_at_point = (obj_center[0], int(obj_center[1] - h / 2.6))  # Aim at the tip of the box

                distance = math.sqrt((screen_center[0] - aim_at_point[0]) ** 2 + (screen_center[1] - aim_at_point[1]) ** 2)

                if distance < min_distance:
                    min_distance = distance
                    closest_object = aim_at_point  # Use the adjusted aim point

        # If a closest object is found, move directly to the aiming position
        if closest_object:
            self.move_mouse(closest_object)

    def run(self):
        """Capture the screen and process detections."""
        while True:
            if self.is_aiming:
                img = self.sct.grab(self.monitor)
                img = np.array(img)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                results = self.model(img, conf=0.55)
                self.aim_at_closest_object(results)

            time.sleep(0.005)  # 5 ms for higher update rate

    def on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if button == mouse.Button.right:
            self.is_aiming = pressed  # Set aiming state based on right button press

if __name__ == "__main__":
    mouse_controller = MouseController(sensitivity=1.5)  # Adjust sensitivity as needed

    # Start mouse listener in a separate thread
    listener = mouse.Listener(on_click=mouse_controller.on_click)
    listener.start()

    mouse_controller.run()

    listener.stop()  # Stop the listener when done
