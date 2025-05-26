import math
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import re
from datetime import datetime


class TranslationModel:
    def __init__(self, csv_path='clean_2.csv'):
        self.data = pd.read_csv(csv_path)
        self._preprocess_data()
        self._build_dictionaries()
    
    def _preprocess_data(self):
        """Preprocess the translation data"""
        def lower_case_words(word):
            return str(word).strip().lower()

        def remove_spaces(word):
            return str(word).strip()

        self.data['English'] = self.data['English'].apply(lower_case_words)
        self.data['Igala'] = self.data['Igala'].apply(remove_spaces)
        
        # Remove duplicates and empty entries
        self.data = self.data.dropna()
        self.data = self.data.drop_duplicates()
    
    def _build_dictionaries(self):
        """Build translation dictionaries"""
        self.english_to_igala = self.data.set_index('English')['Igala'].to_dict()
        self.igala_to_english = {v: k for k, v in self.english_to_igala.items()}
    
    def calculate_confidence(self, text: str, translated_text: str, direction: str) -> float:
        """Calculate translation confidence score based on word coverage"""
        words = text.lower().split()
        dictionary = self.english_to_igala if direction == 'en_to_ig' else self.igala_to_english
        
        found_words = sum(1 for word in words if word in dictionary)
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        confidence = (found_words / total_words) * 100
        return round(confidence, 2)
    
    def calculate_back_translation_score(self, original: str, back_translated: str) -> Dict:
        """Calculate similarity score between original and back-translated text"""
        original_words = set(original.lower().split())
        back_words = set(back_translated.lower().split())
        
        if not original_words:
            return {
                'similarity_score': 0.0,
                'word_overlap': 0,
                'total_original_words': 0,
                'preservation_rate': 0.0
            }
        
        # Calculate word overlap
        overlap = original_words.intersection(back_words)
        similarity_score = (len(overlap) / len(original_words)) * 100
        
        # Calculate preservation rate (how many original words are preserved)
        preservation_rate = (len(overlap) / len(original_words)) * 100
        
        return {
            'similarity_score': round(similarity_score, 2),
            'word_overlap': len(overlap),
            'total_original_words': len(original_words),
            'preservation_rate': round(preservation_rate, 2),
            'overlapping_words': list(overlap)
        }
    
    def translate_single(self, text: str, direction: str = 'en_to_ig') -> Dict:
        """Translate a single text with confidence score"""
        if not text or not text.strip():
            return {
                'original': text,
                'translated': '',
                'confidence': 0.0,
                'direction': direction,
                'timestamp': datetime.now().isoformat()
            }
        
        dictionary = self.english_to_igala if direction == 'en_to_ig' else self.igala_to_english
        words = text.lower().split()
        translated_words = [dictionary.get(word, word) for word in words]
        translated_text = ' '.join(translated_words)
        
        confidence = self.calculate_confidence(text, translated_text, direction)
        
        return {
            'original': text,
            'translated': translated_text,
            'confidence': confidence,
            'direction': direction,
            'timestamp': datetime.now().isoformat()
        }
    
    def back_translate(self, text: str, source_direction: str = 'en_to_ig') -> Dict:
        """Perform back translation for quality assessment"""
        if not text or not text.strip():
            return {
                'original_text': text,
                'forward_translation': '',
                'back_translation': '',
                'forward_confidence': 0.0,
                'back_confidence': 0.0,
                'quality_metrics': {
                    'similarity_score': 0.0,
                    'word_overlap': 0,
                    'total_original_words': 0,
                    'preservation_rate': 0.0
                },
                'source_direction': source_direction,
                'timestamp': datetime.now().isoformat()
            }
        
        # Step 1: Forward translation
        forward_result = self.translate_single(text, source_direction)
        forward_translation = forward_result['translated']
        forward_confidence = forward_result['confidence']
        
        # Step 2: Back translation (reverse direction)
        back_direction = 'ig_to_en' if source_direction == 'en_to_ig' else 'en_to_ig'
        back_result = self.translate_single(forward_translation, back_direction)
        back_translation = back_result['translated']
        back_confidence = back_result['confidence']
        
        # Step 3: Calculate quality metrics
        quality_metrics = self.calculate_back_translation_score(text, back_translation)
        
        # Step 4: Overall quality assessment
        overall_quality = self._assess_translation_quality(
            forward_confidence, back_confidence, quality_metrics['similarity_score']
        )
        
        return {
            'original_text': text,
            'forward_translation': forward_translation,
            'back_translation': back_translation,
            'forward_confidence': forward_confidence,
            'back_confidence': back_confidence,
            'quality_metrics': quality_metrics,
            'overall_quality': overall_quality,
            'source_direction': source_direction,
            'timestamp': datetime.now().isoformat()
        }
    
    def _assess_translation_quality(self, forward_conf: float, back_conf: float, similarity: float) -> Dict:
        """Assess overall translation quality based on multiple metrics"""
        # Weighted average of different quality indicators
        confidence_weight = 0.4
        back_confidence_weight = 0.3
        similarity_weight = 0.3
        
        overall_score = (
            forward_conf * confidence_weight +
            back_conf * back_confidence_weight +
            similarity * similarity_weight
        )
        
        # Quality categories
        if overall_score >= 80:
            quality_level = "Excellent"
            quality_description = "High-quality translation with good preservation of meaning"
        elif overall_score >= 60:
            quality_level = "Good"
            quality_description = "Acceptable translation with minor meaning loss"
        elif overall_score >= 40:
            quality_level = "Fair"
            quality_description = "Translation may have some meaning distortion"
        else:
            quality_level = "Poor"
            quality_description = "Translation quality is low, manual review recommended"
        
        return {
            'overall_score': round(overall_score, 2),
            'quality_level': quality_level,
            'quality_description': quality_description,
            'recommendations': self._get_quality_recommendations(overall_score, forward_conf, back_conf, similarity)
        }
    
    def _get_quality_recommendations(self, overall: float, forward: float, back: float, similarity: float) -> List[str]:
        """Generate recommendations based on quality metrics"""
        recommendations = []
        
        if forward < 70:
            recommendations.append("Consider reviewing the forward translation - low dictionary coverage")
        
        if back < 70:
            recommendations.append("Back translation has low confidence - may indicate translation issues")
        
        if similarity < 50:
            recommendations.append("Low similarity between original and back-translated text - meaning may be lost")
        
        if overall < 60:
            recommendations.append("Overall quality is below acceptable threshold - manual review recommended")
        
        if not recommendations:
            recommendations.append("Translation quality is good - no immediate concerns")
        
        return recommendations
    
    def batch_back_translate(self, texts: List[str], source_direction: str = 'en_to_ig') -> Dict:
        """Perform back translation on multiple texts"""
        results = []
        total_quality_score = 0
        
        for text in texts:
            result = self.back_translate(text, source_direction)
            results.append(result)
            total_quality_score += result['overall_quality']['overall_score']
        
        average_quality = total_quality_score / len(texts) if texts else 0
        
        # Aggregate statistics
        quality_distribution = {
            'Excellent': sum(1 for r in results if r['overall_quality']['quality_level'] == 'Excellent'),
            'Good': sum(1 for r in results if r['overall_quality']['quality_level'] == 'Good'),
            'Fair': sum(1 for r in results if r['overall_quality']['quality_level'] == 'Fair'),
            'Poor': sum(1 for r in results if r['overall_quality']['quality_level'] == 'Poor')
        }
        
        return {
            'results': results,
            'summary': {
                'total_texts': len(texts),
                'average_quality_score': round(average_quality, 2),
                'quality_distribution': quality_distribution,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def translate_batch(self, texts: List[str], direction: str = 'en_to_ig') -> List[Dict]:
        """Translate multiple texts at once"""
        results = []
        for text in texts:
            result = self.translate_single(text, direction)
            results.append(result)
        return results
    
    def auto_detect_language(self, text: str) -> str:
        """Simple language detection based on dictionary coverage"""
        if not text or not text.strip():
            return 'unknown'
        
        words = text.lower().split()
        english_matches = sum(1 for word in words if word in self.english_to_igala)
        igala_matches = sum(1 for word in words if word in self.igala_to_english)
        
        if english_matches > igala_matches:
            return 'english'
        elif igala_matches > english_matches:
            return 'igala'
        else:
            return 'unknown'
    
    def get_word_suggestions(self, partial_word: str, language: str = 'english', limit: int = 5) -> List[str]:
        """Get word suggestions for autocomplete"""
        dictionary = self.english_to_igala.keys() if language == 'english' else self.igala_to_english.keys()
        suggestions = [word for word in dictionary if word.startswith(partial_word.lower())]
        return sorted(suggestions)[:limit]


# Global model instance
_model_instance = None

def get_model():
    """Get or create model instance (singleton pattern)"""
    global _model_instance
    if _model_instance is None:
        _model_instance = TranslationModel()
    return _model_instance

def translate_model(english_text):
    """Legacy function for backward compatibility"""
    model = get_model()
    result = model.translate_single(english_text, 'en_to_ig')
    return result['translated']
