import os
import time
import json
import base64
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockScreenAutomation:
    """Mock screen automation for testing in headless environments"""
    
    def __init__(self):
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.template_dir = Path("templates")
        self.template_dir.mkdir(exist_ok=True)
        self.last_screenshot = None
        self.wake_word_active = False
        self.hotkey_listeners = []
        
        # Screen dimensions (mock values)
        self.screen_width = 1920
        self.screen_height = 1080
        
        logger.info(f"Mock Screen Automation initialized - Screen size: {self.screen_width}x{self.screen_height}")
    
    def take_screenshot(self, region=None, filename=None) -> Dict:
        """Mock taking a screenshot"""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.screenshot_dir / filename
            
            # Create a mock base64 image (1x1 transparent PNG)
            mock_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            
            self.last_screenshot = filepath
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "image_base64": mock_base64,
                "size": [self.screen_width, self.screen_height],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock screenshot failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def locate_on_screen(self, template_image, confidence=0.8, region=None) -> Dict:
        """Mock finding template image on screen"""
        try:
            # Return mock matches
            matches = [
                {
                    "x": 100,
                    "y": 100,
                    "width": 50,
                    "height": 50,
                    "confidence": 0.95
                }
            ]
            
            return {
                "success": True,
                "matches": matches,
                "match_count": len(matches),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock template matching failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def click_at_position(self, x, y, button='left', double_click=False) -> Dict:
        """Mock clicking at specific coordinates"""
        try:
            # Validate coordinates
            if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                return {
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) are outside screen bounds",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": True,
                "action": "double_click" if double_click else "click",
                "position": {"x": x, "y": y},
                "button": button,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock click failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def click_on_image(self, template_image, confidence=0.8, double_click=False) -> Dict:
        """Mock clicking on template image"""
        try:
            return {
                "success": True,
                "action": "double_click" if double_click else "click",
                "position": {"x": 100, "y": 100},
                "button": "left",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock click on image failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def type_text(self, text, interval=0.01) -> Dict:
        """Mock typing text"""
        try:
            return {
                "success": True,
                "text": text,
                "character_count": len(text),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock type text failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def press_key(self, key_combination) -> Dict:
        """Mock pressing key or key combination"""
        try:
            return {
                "success": True,
                "key_combination": key_combination,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock key press failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def scroll(self, direction, amount=3, x=None, y=None) -> Dict:
        """Mock scrolling in specified direction"""
        try:
            if x is None or y is None:
                x, y = 100, 100
            
            if direction.lower() not in ['up', 'down', 'left', 'right']:
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
            logger.error(f"Mock scroll failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def read_text_from_screen(self, region=None, lang='eng') -> Dict:
        """Mock extracting text from screen using OCR"""
        try:
            # Mock OCR text
            mock_text = "This is mock OCR text for testing purposes."
            
            # Mock words with bounding boxes
            words = [
                {
                    "text": "This",
                    "confidence": 95,
                    "bbox": {"x": 10, "y": 10, "width": 40, "height": 20}
                },
                {
                    "text": "is",
                    "confidence": 98,
                    "bbox": {"x": 60, "y": 10, "width": 20, "height": 20}
                },
                {
                    "text": "mock",
                    "confidence": 90,
                    "bbox": {"x": 90, "y": 10, "width": 50, "height": 20}
                },
                {
                    "text": "OCR",
                    "confidence": 85,
                    "bbox": {"x": 150, "y": 10, "width": 40, "height": 20}
                },
                {
                    "text": "text",
                    "confidence": 92,
                    "bbox": {"x": 200, "y": 10, "width": 40, "height": 20}
                }
            ]
            
            return {
                "success": True,
                "text": mock_text,
                "words": words,
                "word_count": len(words),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_window_list(self) -> Dict:
        """Mock getting list of all open windows"""
        try:
            # Mock window list
            windows = [
                {
                    "title": "Terminal",
                    "pid": 12345,
                    "position": {
                        "x": 0,
                        "y": 0,
                        "width": 800,
                        "height": 600
                    },
                    "is_active": True,
                    "is_maximized": False,
                    "is_minimized": False
                },
                {
                    "title": "Web Browser",
                    "pid": 12346,
                    "position": {
                        "x": 100,
                        "y": 100,
                        "width": 1024,
                        "height": 768
                    },
                    "is_active": False,
                    "is_maximized": True,
                    "is_minimized": False
                },
                {
                    "title": "Text Editor",
                    "pid": 12347,
                    "position": {
                        "x": 200,
                        "y": 200,
                        "width": 600,
                        "height": 400
                    },
                    "is_active": False,
                    "is_maximized": False,
                    "is_minimized": False
                }
            ]
            
            return {
                "success": True,
                "windows": windows,
                "window_count": len(windows),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock get window list failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def activate_window(self, window_title) -> Dict:
        """Mock activating window by title"""
        try:
            # Check if window title is in mock window list
            mock_windows = ["Terminal", "Web Browser", "Text Editor"]
            
            if window_title not in mock_windows:
                return {
                    "success": False,
                    "error": f"Window with title '{window_title}' not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": True,
                "window_title": window_title,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock activate window failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def wait_for_image(self, template_image, timeout=10, confidence=0.8) -> Dict:
        """Mock waiting for image to appear on screen"""
        try:
            # Simulate a short wait
            time.sleep(0.5)
            
            return {
                "success": True,
                "wait_time": 0.5,
                "matches": [
                    {
                        "x": 100,
                        "y": 100,
                        "width": 50,
                        "height": 50,
                        "confidence": 0.95
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock wait for image failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def start_wake_word_detection(self, wake_word="jarvis") -> Dict:
        """Mock starting wake word detection"""
        try:
            self.wake_word_active = True
            
            return {
                "success": True,
                "wake_word": wake_word,
                "status": "listening",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock wake word detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def stop_wake_word_detection(self) -> Dict:
        """Mock stopping wake word detection"""
        try:
            self.wake_word_active = False
            
            return {
                "success": True,
                "status": "stopped",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock stop wake word detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def setup_hotkey(self, key_combination, action) -> Dict:
        """Mock setting up global hotkey"""
        try:
            return {
                "success": True,
                "hotkey": key_combination,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock hotkey setup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_automation_sequence(self, sequence) -> Dict:
        """Mock executing a sequence of automation actions"""
        try:
            results = []
            
            for i, action in enumerate(sequence):
                action_type = action.get('type')
                action_params = action.get('params', {})
                
                logger.info(f"Mock executing action {i+1}: {action_type}")
                
                # Simulate success for all actions
                result = {"success": True, "action": action_type}
                
                results.append({
                    "action_index": i,
                    "action_type": action_type,
                    "result": result
                })
                
                # Small delay between actions
                time.sleep(0.1)
            
            return {
                "success": True,
                "total_actions": len(sequence),
                "successful_actions": len(sequence),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mock automation sequence failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global automation instance
automation = MockScreenAutomation()