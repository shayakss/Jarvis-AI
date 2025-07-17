import requests
import unittest
import json
import sys
import os
import base64
from datetime import datetime

class JarvisAPITester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(JarvisAPITester, self).__init__(*args, **kwargs)
        # Use the public endpoint from frontend/.env
        self.base_url = "https://9fa57c9a-db97-4308-9e5a-62a1b1c54384.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def setUp(self):
        print(f"\n🔍 Testing API at {self.api_url}")

    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing Health Check API...")
        try:
            response = requests.get(f"{self.api_url}/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            print(f"✅ Health Check API - Status: {data['status']}")
            print(f"✅ Platform: {data.get('platform')}")
            print(f"✅ Python Version: {data.get('python_version')}")
            return True
        except Exception as e:
            print(f"❌ Health Check API Failed - Error: {str(e)}")
            return False

    def test_02_safe_commands(self):
        """Test the safe commands list endpoint"""
        print("\n🔍 Testing Safe Commands API...")
        try:
            response = requests.get(f"{self.api_url}/safe-commands")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIsInstance(data["safe_commands"], dict)
            self.assertGreater(len(data["safe_commands"]), 0)
            print(f"✅ Safe Commands API - Found {len(data['safe_commands'])} commands")
            print(f"✅ Sample commands: {list(data['safe_commands'].keys())[:5]}")
            return True
        except Exception as e:
            print(f"❌ Safe Commands API Failed - Error: {str(e)}")
            return False

    def test_03_command_execution(self):
        """Test the command execution endpoint with safe commands"""
        print("\n🔍 Testing Command Execution API...")
        
        # Test cases with safe commands
        test_commands = [
            "dir",
            "date",
            "time",
            "whoami"
        ]
        
        success_count = 0
        for cmd in test_commands:
            try:
                print(f"  Testing command: '{cmd}'")
                response = requests.post(
                    f"{self.api_url}/execute-command",
                    json={"command": cmd}
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                if data["success"]:
                    success_count += 1
                    print(f"  ✅ Command '{cmd}' executed successfully")
                    print(f"  ✅ Output: {data['output'][:100]}..." if len(data.get('output', '')) > 100 else f"  ✅ Output: {data.get('output', '')}")
                else:
                    print(f"  ❌ Command '{cmd}' failed: {data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"  ❌ Command '{cmd}' test failed - Error: {str(e)}")
        
        print(f"\n✅ Command Execution API - {success_count}/{len(test_commands)} commands executed successfully")
        return success_count > 0

    def test_04_unsafe_command_execution(self):
        """Test that unsafe commands are blocked"""
        print("\n🔍 Testing Unsafe Command Blocking...")
        
        # Test cases with unsafe commands
        unsafe_commands = [
            "format c:",
            "shutdown /s",
            "del /s /q *.*",
            "net user administrator newpassword"
        ]
        
        block_count = 0
        for cmd in unsafe_commands:
            try:
                print(f"  Testing unsafe command: '{cmd}'")
                response = requests.post(
                    f"{self.api_url}/execute-command",
                    json={"command": cmd}
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                if not data["success"]:
                    block_count += 1
                    print(f"  ✅ Unsafe command '{cmd}' was correctly blocked")
                    print(f"  ✅ Error message: {data.get('error', 'No error message')}")
                else:
                    print(f"  ❌ SECURITY ISSUE: Unsafe command '{cmd}' was NOT blocked!")
            except Exception as e:
                print(f"  ❌ Unsafe command test failed - Error: {str(e)}")
        
        print(f"\n✅ Unsafe Command Blocking - {block_count}/{len(unsafe_commands)} unsafe commands were correctly blocked")
        return block_count == len(unsafe_commands)

    def test_05_command_interpretation(self):
        """Test the natural language to command interpretation"""
        print("\n🔍 Testing Command Interpretation API...")
        
        # Test cases with natural language
        test_phrases = [
            "show me the files in this directory",
            "what time is it",
            "display system information",
            "list running processes"
        ]
        
        expected_commands = [
            "dir",
            "time",
            "systeminfo",
            "tasklist"
        ]
        
        success_count = 0
        for i, phrase in enumerate(test_phrases):
            try:
                print(f"  Testing phrase: '{phrase}'")
                response = requests.post(
                    f"{self.api_url}/interpret-command",
                    json={"natural_language": phrase}
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                if data["success"]:
                    print(f"  ✅ Phrase interpreted successfully")
                    print(f"  ✅ Interpreted as: '{data.get('command', '')}'")
                    
                    # Check if the interpretation is close to what we expect
                    if data.get('command', '').lower().startswith(expected_commands[i].lower()):
                        success_count += 1
                        print(f"  ✅ Interpretation matches expected command: '{expected_commands[i]}'")
                    else:
                        print(f"  ⚠️ Interpretation differs from expected '{expected_commands[i]}', but may still be valid")
                else:
                    print(f"  ❌ Phrase interpretation failed: {data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"  ❌ Phrase interpretation test failed - Error: {str(e)}")
        
        print(f"\n✅ Command Interpretation API - {success_count}/{len(test_phrases)} phrases interpreted as expected")
        return success_count > 0

    def test_06_voice_command_pipeline(self):
        """Test the voice command pipeline (without actual audio)"""
        print("\n🔍 Testing Voice Command Pipeline API...")
        
        # Test cases with simulated transcriptions
        test_transcriptions = [
            "show me the files",
            "what time is it"
        ]
        
        success_count = 0
        for transcription in test_transcriptions:
            try:
                print(f"  Testing transcription: '{transcription}'")
                response = requests.post(
                    f"{self.api_url}/voice-command",
                    json={
                        "natural_language": transcription,
                        "confirm": True
                    }
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                if data["success"]:
                    success_count += 1
                    print(f"  ✅ Voice command processed successfully")
                    print(f"  ✅ Interpreted as: '{data.get('interpreted_command', '')}'")
                    print(f"  ✅ Output: {data['output'][:100]}..." if len(data.get('output', '')) > 100 else f"  ✅ Output: {data.get('output', '')}")
                else:
                    print(f"  ❌ Voice command failed: {data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"  ❌ Voice command test failed - Error: {str(e)}")
        
        print(f"\n✅ Voice Command Pipeline API - {success_count}/{len(test_transcriptions)} voice commands processed successfully")
        return success_count > 0

    def test_07_command_history(self):
        """Test the command history endpoint"""
        print("\n🔍 Testing Command History API...")
        try:
            response = requests.get(f"{self.api_url}/command-history")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Command History API - Found {data.get('count', 0)} history entries")
                if data.get('count', 0) > 0:
                    print(f"✅ Most recent command: '{data['history'][0].get('command', '')}'")
                return True
            else:
                print(f"❌ Command History API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Command History API Failed - Error: {str(e)}")
            return False

    # ============================================
    # AUTOMATION API TESTS
    # ============================================

    def test_08_automation_status(self):
        """Test the automation status endpoint"""
        print("\n🔍 Testing Automation Status API...")
        try:
            response = requests.get(f"{self.api_url}/automation/status")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Automation Status API - Status: {data.get('status', 'unknown')}")
                print(f"✅ Screen Size: {data.get('screen_size', {}).get('width')}x{data.get('screen_size', {}).get('height')}")
                print(f"✅ Available Features:")
                for feature, available in data.get('features', {}).items():
                    print(f"  - {feature}: {'✅' if available else '❌'}")
                return True
            else:
                print(f"❌ Automation Status API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Automation Status API Failed - Error: {str(e)}")
            return False

    def test_09_screenshot_api(self):
        """Test the screenshot endpoint"""
        print("\n🔍 Testing Screenshot API...")
        try:
            response = requests.post(
                f"{self.api_url}/automation/screenshot",
                json={}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Screenshot API - Successfully captured screenshot")
                print(f"✅ Image size: {data.get('size', [0, 0])}")
                
                # Verify base64 image data is present
                self.assertIn('image_base64', data)
                self.assertTrue(data['image_base64'].startswith('iVBORw0KGgo') or 
                               data['image_base64'].startswith('/9j/') or
                               data['image_base64'].startswith('UklGR'))
                
                # Check if we can decode the base64 image
                try:
                    image_data = base64.b64decode(data['image_base64'])
                    print(f"✅ Base64 image decoded successfully ({len(image_data)} bytes)")
                except Exception as decode_error:
                    print(f"⚠️ Base64 image decoding failed: {decode_error}")
                
                return True
            else:
                print(f"❌ Screenshot API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Screenshot API Failed - Error: {str(e)}")
            return False

    def test_10_click_api(self):
        """Test the click endpoint"""
        print("\n🔍 Testing Click API...")
        try:
            # Test with center of screen coordinates
            response = requests.post(
                f"{self.api_url}/automation/status",
                json={}
            )
            status_data = response.json()
            
            # Get screen dimensions from status API
            screen_width = status_data.get('screen_size', {}).get('width', 1024)
            screen_height = status_data.get('screen_size', {}).get('height', 768)
            
            # Click in the center of the screen
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            print(f"  Testing click at center of screen ({center_x}, {center_y})")
            response = requests.post(
                f"{self.api_url}/automation/click",
                json={
                    "x": center_x,
                    "y": center_y,
                    "button": "left",
                    "double_click": False
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Click API - Successfully clicked at ({center_x}, {center_y})")
                print(f"✅ Action: {data.get('action', 'unknown')}")
                print(f"✅ Button: {data.get('button', 'unknown')}")
                return True
            else:
                print(f"❌ Click API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Click API Failed - Error: {str(e)}")
            return False

    def test_11_type_text_api(self):
        """Test the type text endpoint"""
        print("\n🔍 Testing Type Text API...")
        try:
            test_text = "Hello, Jarvis AI!"
            
            response = requests.post(
                f"{self.api_url}/automation/type",
                json={
                    "text": test_text,
                    "interval": 0.05
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Type Text API - Successfully typed: '{test_text}'")
                print(f"✅ Character count: {data.get('character_count', 0)}")
                return True
            else:
                print(f"❌ Type Text API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Type Text API Failed - Error: {str(e)}")
            return False

    def test_12_key_press_api(self):
        """Test the key press endpoint"""
        print("\n🔍 Testing Key Press API...")
        try:
            # Test simple key press
            test_keys = ["enter", "tab", "ctrl+a", "ctrl+c"]
            
            success_count = 0
            for key in test_keys:
                print(f"  Testing key press: '{key}'")
                response = requests.post(
                    f"{self.api_url}/automation/key",
                    json={
                        "key_combination": key
                    }
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                if data["success"]:
                    success_count += 1
                    print(f"  ✅ Successfully pressed key: '{key}'")
                else:
                    print(f"  ❌ Key press failed: {data.get('error', 'Unknown error')}")
            
            print(f"\n✅ Key Press API - {success_count}/{len(test_keys)} key presses successful")
            return success_count > 0
        except Exception as e:
            print(f"❌ Key Press API Failed - Error: {str(e)}")
            return False

    def test_13_scroll_api(self):
        """Test the scroll endpoint"""
        print("\n🔍 Testing Scroll API...")
        try:
            # Test scrolling in different directions
            test_directions = ["up", "down", "left", "right"]
            
            success_count = 0
            for direction in test_directions:
                print(f"  Testing scroll direction: '{direction}'")
                response = requests.post(
                    f"{self.api_url}/automation/scroll",
                    json={
                        "direction": direction,
                        "amount": 3
                    }
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                if data["success"]:
                    success_count += 1
                    print(f"  ✅ Successfully scrolled: '{direction}'")
                    print(f"  ✅ Amount: {data.get('amount', 0)}")
                else:
                    print(f"  ❌ Scroll failed: {data.get('error', 'Unknown error')}")
            
            print(f"\n✅ Scroll API - {success_count}/{len(test_directions)} scroll directions successful")
            return success_count > 0
        except Exception as e:
            print(f"❌ Scroll API Failed - Error: {str(e)}")
            return False

    def test_14_ocr_api(self):
        """Test the OCR endpoint"""
        print("\n🔍 Testing OCR API...")
        try:
            # First take a screenshot to have something to OCR
            screenshot_response = requests.post(
                f"{self.api_url}/automation/screenshot",
                json={}
            )
            self.assertEqual(screenshot_response.status_code, 200)
            
            # Now perform OCR on the screen
            response = requests.post(
                f"{self.api_url}/automation/ocr",
                json={
                    "lang": "eng"
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ OCR API - Successfully extracted text from screen")
                print(f"✅ Word count: {data.get('word_count', 0)}")
                print(f"✅ Text sample: {data.get('text', '')[:100]}..." if len(data.get('text', '')) > 100 else f"✅ Text: {data.get('text', '')}")
                return True
            else:
                print(f"❌ OCR API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ OCR API Failed - Error: {str(e)}")
            return False

    def test_15_windows_api(self):
        """Test the windows list endpoint"""
        print("\n🔍 Testing Windows List API...")
        try:
            response = requests.get(f"{self.api_url}/automation/windows")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Windows List API - Found {data.get('window_count', 0)} windows")
                if data.get('window_count', 0) > 0:
                    for i, window in enumerate(data.get('windows', [])[:3]):  # Show first 3 windows
                        print(f"  {i+1}. '{window.get('title', 'Unknown')}' ({window.get('position', {}).get('width', 0)}x{window.get('position', {}).get('height', 0)})")
                return True
            else:
                print(f"❌ Windows List API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Windows List API Failed - Error: {str(e)}")
            return False

    def test_16_activate_window_api(self):
        """Test the activate window endpoint"""
        print("\n🔍 Testing Activate Window API...")
        try:
            # First get list of windows
            windows_response = requests.get(f"{self.api_url}/automation/windows")
            self.assertEqual(windows_response.status_code, 200)
            windows_data = windows_response.json()
            
            if not windows_data["success"] or windows_data.get('window_count', 0) == 0:
                print("❌ No windows available to test activation")
                return False
            
            # Try to activate the first window
            window_title = windows_data['windows'][0]['title']
            print(f"  Attempting to activate window: '{window_title}'")
            
            response = requests.post(
                f"{self.api_url}/automation/activate-window",
                json={
                    "window_title": window_title
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Activate Window API - Successfully activated window: '{window_title}'")
                return True
            else:
                print(f"❌ Activate Window API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Activate Window API Failed - Error: {str(e)}")
            return False

    def test_17_wake_word_api(self):
        """Test the wake word detection endpoints"""
        print("\n🔍 Testing Wake Word API...")
        try:
            # Start wake word detection
            start_response = requests.post(
                f"{self.api_url}/automation/wake-word/start",
                json={
                    "wake_word": "jarvis"
                }
            )
            self.assertEqual(start_response.status_code, 200)
            start_data = start_response.json()
            
            if start_data["success"]:
                print(f"✅ Wake Word Start API - Successfully started wake word detection")
                print(f"✅ Wake Word: '{start_data.get('wake_word', 'unknown')}'")
                print(f"✅ Status: {start_data.get('status', 'unknown')}")
                
                # Stop wake word detection
                stop_response = requests.post(f"{self.api_url}/automation/wake-word/stop")
                self.assertEqual(stop_response.status_code, 200)
                stop_data = stop_response.json()
                
                if stop_data["success"]:
                    print(f"✅ Wake Word Stop API - Successfully stopped wake word detection")
                    print(f"✅ Status: {stop_data.get('status', 'unknown')}")
                    return True
                else:
                    print(f"❌ Wake Word Stop API failed: {stop_data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Wake Word Start API failed: {start_data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Wake Word API Failed - Error: {str(e)}")
            return False

    def test_18_automation_sequence_api(self):
        """Test the automation sequence endpoint"""
        print("\n🔍 Testing Automation Sequence API...")
        try:
            # Create a simple automation sequence
            test_sequence = [
                {
                    "type": "screenshot",
                    "params": {}
                },
                {
                    "type": "wait",
                    "params": {"seconds": 1}
                },
                {
                    "type": "type",
                    "params": {"text": "Hello from sequence test!"}
                },
                {
                    "type": "key",
                    "params": {"key_combination": "enter"}
                }
            ]
            
            response = requests.post(
                f"{self.api_url}/automation/sequence",
                json={
                    "sequence": test_sequence,
                    "name": "Test Sequence"
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data["success"]:
                print(f"✅ Automation Sequence API - Successfully executed sequence")
                print(f"✅ Total actions: {data.get('total_actions', 0)}")
                print(f"✅ Successful actions: {data.get('successful_actions', 0)}")
                
                # Check individual action results
                for i, action_result in enumerate(data.get('results', [])):
                    action_type = action_result.get('action_type', 'unknown')
                    success = action_result.get('result', {}).get('success', False)
                    print(f"  {i+1}. {action_type}: {'✅' if success else '❌'}")
                
                return data.get('successful_actions', 0) == data.get('total_actions', 0)
            else:
                print(f"❌ Automation Sequence API failed: {data.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Automation Sequence API Failed - Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests and report results"""
        test_methods = [
            self.test_01_health_check,
            self.test_02_safe_commands,
            self.test_03_command_execution,
            self.test_04_unsafe_command_execution,
            self.test_05_command_interpretation,
            self.test_06_voice_command_pipeline,
            self.test_07_command_history,
            # Automation API tests
            self.test_08_automation_status,
            self.test_09_screenshot_api,
            self.test_10_click_api,
            self.test_11_type_text_api,
            self.test_12_key_press_api,
            self.test_13_scroll_api,
            self.test_14_ocr_api,
            self.test_15_windows_api,
            self.test_16_activate_window_api,
            self.test_17_wake_word_api,
            self.test_18_automation_sequence_api
        ]
        
        results = []
        for test_method in test_methods:
            result = test_method()
            results.append(result)
        
        success_count = sum(1 for r in results if r)
        total_count = len(results)
        
        print("\n" + "="*80)
        print(f"📊 JARVIS AI ASSISTANT API TEST RESULTS: {success_count}/{total_count} tests passed")
        print("="*80)
        
        return success_count == total_count

def main():
    tester = JarvisAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())