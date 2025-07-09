import os
import time
import json
import base64
import subprocess
import threading
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
from pathlib import Path

# GUI Automation imports
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import psutil
import pygetwindow as gw

# Input simulation
import keyboard
import mouse
from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse

# Speech recognition for wake word
import speech_recognition as sr
from pydub import AudioSegment

# Configure pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenAutomation:
    """Enhanced screen automation with GUI control, OCR, and image recognition"""
    
    def __init__(self):
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.template_dir = Path("templates")
        self.template_dir.mkdir(exist_ok=True)
        self.last_screenshot = None
        self.wake_word_active = False
        self.hotkey_listeners = []
        
        # Initialize wake word detection
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        logger.info(f"Screen Automation initialized - Screen size: {self.screen_width}x{self.screen_height}")
    
    def take_screenshot(self, region=None, filename=None) -> Dict:
        """Take a screenshot of the screen or specific region"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.screenshot_dir / filename
            screenshot.save(filepath)
            
            # Convert to base64 for frontend display
            import io
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            self.last_screenshot = filepath
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "image_base64": img_base64,
                "size": screenshot.size,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def locate_on_screen(self, template_image, confidence=0.8, region=None) -> Dict:
        """Find template image on screen using image recognition"""
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot(region=region)
            
            # Convert to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Load template
            if isinstance(template_image, str):
                template_cv = cv2.imread(template_image)
            else:
                template_cv = cv2.cvtColor(np.array(template_image), cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template_cv, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= confidence)
            
            matches = []
            for pt in zip(*locations[::-1]):
                matches.append({
                    "x": int(pt[0]),
                    "y": int(pt[1]),
                    "width": template_cv.shape[1],
                    "height": template_cv.shape[0],
                    "confidence": float(result[pt[1], pt[0]])
                })
            
            return {
                "success": True,
                "matches": matches,
                "match_count": len(matches),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def click_at_position(self, x, y, button='left', double_click=False) -> Dict:
        """Click at specific coordinates"""
        try:
            # Validate coordinates
            if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                return {
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) are outside screen bounds",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Move to position and click
            pyautogui.moveTo(x, y, duration=0.2)
            
            if double_click:
                pyautogui.doubleClick(x, y, button=button)
            else:
                pyautogui.click(x, y, button=button)
            
            return {
                "success": True,
                "action": "double_click" if double_click else "click",
                "position": {"x": x, "y": y},
                "button": button,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def click_on_image(self, template_image, confidence=0.8, double_click=False) -> Dict:
        """Click on first occurrence of template image"""
        try:
            # Find the image on screen
            locate_result = self.locate_on_screen(template_image, confidence)
            
            if not locate_result["success"]:
                return locate_result
            
            if not locate_result["matches"]:
                return {
                    "success": False,
                    "error": "Template image not found on screen",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Click on first match center
            match = locate_result["matches"][0]
            click_x = match["x"] + match["width"] // 2
            click_y = match["y"] + match["height"] // 2
            
            return self.click_at_position(click_x, click_y, double_click=double_click)
            
        except Exception as e:
            logger.error(f"Click on image failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def type_text(self, text, interval=0.01) -> Dict:
        """Type text with specified interval between characters"""
        try:
            pyautogui.typewrite(text, interval=interval)
            
            return {
                "success": True,
                "text": text,
                "character_count": len(text),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def press_key(self, key_combination) -> Dict:
        """Press key or key combination"""
        try:
            if isinstance(key_combination, str):
                if '+' in key_combination:
                    # Handle key combinations like 'ctrl+c'
                    keys = key_combination.split('+')
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(key_combination)
            else:
                pyautogui.press(key_combination)
            
            return {
                "success": True,
                "key_combination": key_combination,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def scroll(self, direction, amount=3, x=None, y=None) -> Dict:
        """Scroll in specified direction"""
        try:
            if x is None or y is None:
                x, y = pyautogui.position()
            
            if direction.lower() == 'up':
                pyautogui.scroll(amount, x=x, y=y)
            elif direction.lower() == 'down':
                pyautogui.scroll(-amount, x=x, y=y)
            elif direction.lower() == 'left':
                pyautogui.hscroll(-amount, x=x, y=y)
            elif direction.lower() == 'right':
                pyautogui.hscroll(amount, x=x, y=y)
            else:
                return {
                    "success": False,
                    "error": f"Invalid scroll direction: {direction}",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": True,
                "direction": direction,
                "amount": amount,
                "position": {"x": x, "y": y},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def drag_and_drop(self, start_x, start_y, end_x, end_y, duration=0.5) -> Dict:
        """Drag from start position to end position"""
        try:
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, 
                          button='left', mouseDownUp=False)
            
            return {
                "success": True,
                "start_position": {"x": start_x, "y": start_y},
                "end_position": {"x": end_x, "y": end_y},
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Drag and drop failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def read_text_from_screen(self, region=None, lang='eng') -> Dict:
        """Extract text from screen using OCR"""
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot(region=region)
            
            # Convert to format suitable for OCR
            screenshot_np = np.array(screenshot)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(screenshot_np, lang=lang)
            
            # Get text with bounding boxes
            data = pytesseract.image_to_data(screenshot_np, output_type=pytesseract.Output.DICT)
            
            words = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Confidence threshold
                    words.append({
                        "text": data['text'][i],
                        "confidence": int(data['conf'][i]),
                        "bbox": {
                            "x": int(data['left'][i]),
                            "y": int(data['top'][i]),
                            "width": int(data['width'][i]),
                            "height": int(data['height'][i])
                        }
                    })
            
            return {
                "success": True,
                "text": text.strip(),
                "words": words,
                "word_count": len(words),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_window_list(self) -> Dict:
        """Get list of all open windows"""
        try:
            windows = []
            for window in gw.getAllWindows():
                if window.title:  # Only include windows with titles
                    windows.append({
                        "title": window.title,
                        "pid": window._hWnd if hasattr(window, '_hWnd') else None,
                        "position": {
                            "x": window.left,
                            "y": window.top,
                            "width": window.width,
                            "height": window.height
                        },
                        "is_active": window.isActive,
                        "is_maximized": window.isMaximized,
                        "is_minimized": window.isMinimized
                    })
            
            return {
                "success": True,
                "windows": windows,
                "window_count": len(windows),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get window list failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def activate_window(self, window_title) -> Dict:
        """Activate window by title"""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                return {
                    "success": False,
                    "error": f"Window with title '{window_title}' not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            window = windows[0]
            window.activate()
            
            return {
                "success": True,
                "window_title": window_title,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Activate window failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def wait_for_image(self, template_image, timeout=10, confidence=0.8) -> Dict:
        """Wait for image to appear on screen"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                locate_result = self.locate_on_screen(template_image, confidence)
                
                if locate_result["success"] and locate_result["matches"]:
                    return {
                        "success": True,
                        "wait_time": time.time() - start_time,
                        "matches": locate_result["matches"],
                        "timestamp": datetime.now().isoformat()
                    }
                
                time.sleep(0.5)
            
            return {
                "success": False,
                "error": f"Image not found within {timeout} seconds",
                "timeout": timeout,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wait for image failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def start_wake_word_detection(self, wake_word="jarvis") -> Dict:
        """Start wake word detection in background"""
        try:
            def wake_word_listener():
                self.wake_word_active = True
                
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                
                while self.wake_word_active:
                    try:
                        with self.microphone as source:
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                        
                        text = self.recognizer.recognize_google(audio).lower()
                        
                        if wake_word in text:
                            logger.info(f"Wake word '{wake_word}' detected!")
                            # Trigger wake word event (can be extended to call API)
                            
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        logger.error(f"Wake word detection error: {e}")
                        break
            
            # Start wake word detection in background thread
            wake_thread = threading.Thread(target=wake_word_listener, daemon=True)
            wake_thread.start()
            
            return {
                "success": True,
                "wake_word": wake_word,
                "status": "listening",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wake word detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def stop_wake_word_detection(self) -> Dict:
        """Stop wake word detection"""
        try:
            self.wake_word_active = False
            
            return {
                "success": True,
                "status": "stopped",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stop wake word detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def setup_hotkey(self, key_combination, action) -> Dict:
        """Setup global hotkey"""
        try:
            def hotkey_handler():
                logger.info(f"Hotkey {key_combination} triggered")
                # Execute action (can be extended)
                
            keyboard.add_hotkey(key_combination, hotkey_handler)
            
            return {
                "success": True,
                "hotkey": key_combination,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Hotkey setup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_automation_sequence(self, sequence) -> Dict:
        """Execute a sequence of automation actions"""
        try:
            results = []
            
            for i, action in enumerate(sequence):
                action_type = action.get('type')
                action_params = action.get('params', {})
                
                logger.info(f"Executing action {i+1}: {action_type}")
                
                if action_type == 'click':
                    result = self.click_at_position(**action_params)
                elif action_type == 'click_image':
                    result = self.click_on_image(**action_params)
                elif action_type == 'type':
                    result = self.type_text(**action_params)
                elif action_type == 'key':
                    result = self.press_key(**action_params)
                elif action_type == 'scroll':
                    result = self.scroll(**action_params)
                elif action_type == 'wait':
                    time.sleep(action_params.get('seconds', 1))
                    result = {"success": True, "action": "wait"}
                elif action_type == 'screenshot':
                    result = self.take_screenshot(**action_params)
                elif action_type == 'ocr':
                    result = self.read_text_from_screen(**action_params)
                elif action_type == 'wait_for_image':
                    result = self.wait_for_image(**action_params)
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown action type: {action_type}"
                    }
                
                results.append({
                    "action_index": i,
                    "action_type": action_type,
                    "result": result
                })
                
                # Stop sequence if action fails
                if not result.get("success", False):
                    break
                
                # Small delay between actions
                time.sleep(0.1)
            
            successful_actions = sum(1 for r in results if r["result"].get("success", False))
            
            return {
                "success": True,
                "total_actions": len(sequence),
                "successful_actions": successful_actions,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Automation sequence failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global automation instance
automation = ScreenAutomation()