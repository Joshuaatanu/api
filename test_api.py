#!/usr/bin/env python3
"""
Test script for the Enhanced English-Igala Translation API
Run this script to test all the new features and endpoints.
"""

import requests
import json
import time
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:10000"
TEST_USER_ID = "test_user_123"
TEST_SESSION_ID = "test_session_abc"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_single_translation(self):
        """Test single translation with confidence scoring"""
        try:
            payload = {
                "english-text": "Hello world",
                "direction": "en_to_ig",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID
            }
            response = self.session.post(f"{self.base_url}/translate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['original', 'translated', 'confidence', 'direction', 'timestamp']
                if all(field in data for field in required_fields):
                    self.log_test("Single Translation", True, 
                                f"Translated: '{data['original']}' -> '{data['translated']}' (Confidence: {data['confidence']}%)")
                    return True
                else:
                    self.log_test("Single Translation", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Single Translation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Single Translation", False, str(e))
            return False
    
    def test_back_translation(self):
        """Test back translation for quality assessment"""
        try:
            payload = {
                "text": "Hello world",
                "source_direction": "en_to_ig",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID
            }
            response = self.session.post(f"{self.base_url}/back-translate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['original_text', 'forward_translation', 'back_translation', 
                                 'forward_confidence', 'back_confidence', 'quality_metrics', 'overall_quality']
                if all(field in data for field in required_fields):
                    quality_score = data['overall_quality']['overall_score']
                    quality_level = data['overall_quality']['quality_level']
                    similarity = data['quality_metrics']['similarity_score']
                    self.log_test("Back Translation", True, 
                                f"Quality: {quality_level} ({quality_score}%), Similarity: {similarity}%")
                    return True
                else:
                    self.log_test("Back Translation", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Back Translation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Back Translation", False, str(e))
            return False
    
    def test_batch_back_translation(self):
        """Test batch back translation"""
        try:
            payload = {
                "texts": ["Hello", "Good morning", "Thank you"],
                "source_direction": "en_to_ig",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID
            }
            response = self.session.post(f"{self.base_url}/back-translate/batch", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and 'summary' in data:
                    results_count = len(data['results'])
                    avg_quality = data['summary']['average_quality_score']
                    quality_dist = data['summary']['quality_distribution']
                    self.log_test("Batch Back Translation", True, 
                                f"Processed {results_count} texts, avg quality: {avg_quality}%")
                    return True
                else:
                    self.log_test("Batch Back Translation", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Batch Back Translation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Batch Back Translation", False, str(e))
            return False
    
    def test_translation_quality_assessment(self):
        """Test translation quality assessment"""
        try:
            payload = {
                "original_text": "Hello world",
                "translated_text": "náàgò àná",
                "direction": "en_to_ig"
            }
            response = self.session.post(f"{self.base_url}/translation-quality", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['original_text', 'provided_translation', 'back_translation', 
                                 'quality_metrics', 'overall_quality']
                if all(field in data for field in required_fields):
                    quality_score = data['overall_quality']['overall_score']
                    quality_level = data['overall_quality']['quality_level']
                    self.log_test("Translation Quality Assessment", True, 
                                f"Quality: {quality_level} ({quality_score}%)")
                    return True
                else:
                    self.log_test("Translation Quality Assessment", False, "Missing required fields")
                    return False
            else:
                self.log_test("Translation Quality Assessment", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Translation Quality Assessment", False, str(e))
            return False
    
    def test_quality_report(self):
        """Test quality report generation"""
        try:
            response = self.session.get(f"{self.base_url}/quality-report/{TEST_USER_ID}")
            
            if response.status_code == 200:
                data = response.json()
                if 'user_id' in data:
                    total_back_translations = data.get('total_back_translations', 0)
                    avg_quality = data.get('average_quality_score', 0)
                    self.log_test("Quality Report", True, 
                                f"Generated report: {total_back_translations} back translations, avg quality: {avg_quality}%")
                    return True
                else:
                    self.log_test("Quality Report", False, "Invalid response format")
                    return False
            else:
                self.log_test("Quality Report", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Quality Report", False, str(e))
            return False
    
    def test_batch_translation(self):
        """Test batch translation"""
        try:
            payload = {
                "texts": ["Hello", "Good morning", "Thank you"],
                "direction": "en_to_ig",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID
            }
            response = self.session.post(f"{self.base_url}/translate/batch", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) == 3:
                    avg_confidence = data.get('average_confidence', 0)
                    self.log_test("Batch Translation", True, 
                                f"Translated {len(data['results'])} texts, avg confidence: {avg_confidence}%")
                    return True
                else:
                    self.log_test("Batch Translation", False, "Incorrect number of results")
                    return False
            else:
                self.log_test("Batch Translation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Batch Translation", False, str(e))
            return False
    
    def test_language_detection(self):
        """Test language auto-detection"""
        try:
            test_cases = [
                {"text": "Hello world", "expected": "english"},
                {"text": "good morning", "expected": "english"}
            ]
            
            for case in test_cases:
                payload = {"text": case["text"]}
                response = self.session.post(f"{self.base_url}/detect-language", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    detected = data.get('detected_language')
                    self.log_test(f"Language Detection - '{case['text']}'", True, 
                                f"Detected: {detected}")
                else:
                    self.log_test("Language Detection", False, f"Status code: {response.status_code}")
                    return False
            return True
        except Exception as e:
            self.log_test("Language Detection", False, str(e))
            return False
    
    def test_word_suggestions(self):
        """Test word suggestions/autocomplete"""
        try:
            payload = {
                "partial_word": "hel",
                "language": "english",
                "limit": 5
            }
            response = self.session.post(f"{self.base_url}/suggestions", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                self.log_test("Word Suggestions", True, 
                            f"Found {len(suggestions)} suggestions for 'hel': {suggestions[:3]}")
                return True
            else:
                self.log_test("Word Suggestions", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Word Suggestions", False, str(e))
            return False
    
    def test_pos_analysis(self):
        """Test POS tagging"""
        try:
            payload = {"translation_text": "The quick brown fox"}
            response = self.session.post(f"{self.base_url}/submit_translation", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                pos_tags = data.get('pos_tags', '')
                self.log_test("POS Analysis", True, f"POS tags: {pos_tags}")
                return True
            else:
                self.log_test("POS Analysis", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("POS Analysis", False, str(e))
            return False
    
    def test_favorites(self):
        """Test favorites management"""
        try:
            # Add to favorites
            add_payload = {
                "user_id": TEST_USER_ID,
                "original_text": "Hello",
                "translated_text": "Sannu",
                "direction": "en_to_ig"
            }
            response = self.session.post(f"{self.base_url}/favorites", json=add_payload)
            
            if response.status_code == 200:
                # Get favorites
                response = self.session.get(f"{self.base_url}/favorites/{TEST_USER_ID}")
                if response.status_code == 200:
                    data = response.json()
                    favorites = data.get('favorites', [])
                    self.log_test("Favorites Management", True, 
                                f"Added and retrieved {len(favorites)} favorites")
                    return True
                else:
                    self.log_test("Favorites Management", False, "Failed to retrieve favorites")
                    return False
            else:
                self.log_test("Favorites Management", False, f"Failed to add favorite: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Favorites Management", False, str(e))
            return False
    
    def test_translation_history(self):
        """Test translation history retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/history/{TEST_USER_ID}?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                history = data.get('history', [])
                self.log_test("Translation History", True, 
                            f"Retrieved {len(history)} history entries")
                return True
            else:
                self.log_test("Translation History", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Translation History", False, str(e))
            return False
    
    def test_analytics(self):
        """Test user analytics"""
        try:
            response = self.session.get(f"{self.base_url}/analytics/{TEST_USER_ID}")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_translations', 0)
                avg_confidence = data.get('average_confidence', 0)
                self.log_test("User Analytics", True, 
                            f"Total translations: {total}, Avg confidence: {avg_confidence}%")
                return True
            else:
                self.log_test("User Analytics", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Analytics", False, str(e))
            return False
    
    def test_data_export(self):
        """Test data export functionality"""
        try:
            # Test JSON export
            response = self.session.get(f"{self.base_url}/export/{TEST_USER_ID}?format=json")
            
            if response.status_code == 200:
                data = response.json()
                translations = data.get('translations', [])
                favorites = data.get('favorites', [])
                self.log_test("Data Export (JSON)", True, 
                            f"Exported {len(translations)} translations, {len(favorites)} favorites")
                return True
            else:
                self.log_test("Data Export", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Data Export", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting API Tests for Enhanced English-Igala Translation API with Back Translation")
        print("=" * 80)
        
        # Wait a moment for server to be ready
        time.sleep(1)
        
        tests = [
            self.test_health_check,
            self.test_single_translation,
            self.test_batch_translation,
            self.test_back_translation,
            self.test_batch_back_translation,
            self.test_translation_quality_assessment,
            self.test_quality_report,
            self.test_language_detection,
            self.test_word_suggestions,
            self.test_pos_analysis,
            self.test_favorites,
            self.test_translation_history,
            self.test_analytics,
            self.test_data_export
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your API with back translation is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed == total

def main():
    """Main function to run tests"""
    print("Enhanced English-Igala Translation API Test Suite with Back Translation")
    print("Make sure your Flask server is running on http://localhost:10000")
    
    # Wait for user confirmation
    input("Press Enter to start testing...")
    
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    if success:
        print("\n✨ Ready to use your enhanced translation API with back translation!")
        print("\n📚 Check API_DOCUMENTATION.md for detailed usage instructions.")
        print("\n🔄 Back translation features:")
        print("   • Quality assessment through round-trip translation")
        print("   • Similarity scoring and confidence metrics")
        print("   • Batch back translation processing")
        print("   • Quality reports and recommendations")
    else:
        print("\n🔧 Please fix the failing tests before proceeding.")

if __name__ == "__main__":
    main() 