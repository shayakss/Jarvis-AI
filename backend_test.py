import requests
import unittest
import json
import sys
import os
from datetime import datetime

class JarvisAPITester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(JarvisAPITester, self).__init__(*args, **kwargs)
        # Use the public endpoint from frontend/.env
        self.base_url = "https://32203e6d-a4c0-4e5c-81cd-5c7941d5e294.preview.emergentagent.com"
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

    def run_all_tests(self):
        """Run all API tests and report results"""
        test_methods = [
            self.test_01_health_check,
            self.test_02_safe_commands,
            self.test_03_command_execution,
            self.test_04_unsafe_command_execution,
            self.test_05_command_interpretation,
            self.test_06_voice_command_pipeline,
            self.test_07_command_history
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