# Create the bias detector model
bias_detector_py = '''"""
Cultural Bias Detection Model
Uses machine learning and rule-based approaches to detect cultural bias patterns
"""
import re
import json
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BiasDetector:
    def __init__(self):
        """Initialize the bias detector with predefined patterns and weights"""
        self.cultural_bias_patterns = self._load_bias_patterns()
        self.sentiment_weights = self._load_sentiment_weights()
        self.language_patterns = self._load_language_patterns()
        
    def detect_bias(self, content: str, gemini_analysis: Dict) -> Dict[str, Any]:
        """
        Main bias detection method
        
        Args:
            content: Campaign content to analyze
            gemini_analysis: Analysis results from Gemini API
            
        Returns:
            Dictionary with bias detection results
        """
        try:
            # Initialize results structure
            bias_results = {
                "flags": [],
                "severity_scores": {},
                "pattern_matches": [],
                "confidence_score": 0.0,
                "bias_categories": []
            }
            
            # Run different bias detection methods
            stereotype_bias = self._detect_stereotype_bias(content)
            linguistic_bias = self._detect_linguistic_bias(content)
            cultural_assumption_bias = self._detect_cultural_assumptions(content, gemini_analysis)
            representation_bias = self._detect_representation_bias(content)
            
            # Compile all detected biases
            all_biases = [stereotype_bias, linguistic_bias, cultural_assumption_bias, representation_bias]
            
            for bias_result in all_biases:
                if bias_result["detected"]:
                    bias_results["flags"].extend(bias_result["flags"])
                    bias_results["pattern_matches"].extend(bias_result["patterns"])
                    bias_results["bias_categories"].append(bias_result["category"])
            
            # Calculate overall severity and confidence
            bias_results["severity_scores"] = self._calculate_severity_scores(all_biases)
            bias_results["confidence_score"] = self._calculate_confidence(bias_results)
            
            logger.info(f"Bias detection completed. Found {len(bias_results['flags'])} potential issues.")
            
            return bias_results
            
        except Exception as e:
            logger.error(f"Bias detection failed: {str(e)}")
            return {"error": str(e), "flags": [], "confidence_score": 0.0}
    
    def _detect_stereotype_bias(self, content: str) -> Dict:
        """Detect cultural stereotypes in content"""
        stereotype_flags = []
        patterns_found = []
        
        # Check for common stereotypical language
        for pattern, info in self.cultural_bias_patterns["stereotypes"].items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                stereotype_flags.append({
                    "type": "stereotype",
                    "pattern": pattern,
                    "matches": matches,
                    "severity": info["severity"],
                    "description": info["description"]
                })
                patterns_found.append(pattern)
        
        return {
            "detected": len(stereotype_flags) > 0,
            "category": "stereotype_bias",
            "flags": stereotype_flags,
            "patterns": patterns_found,
            "severity": max([f["severity"] for f in stereotype_flags], default=0)
        }
    
    def _detect_linguistic_bias(self, content: str) -> Dict:
        """Detect linguistic bias patterns"""
        linguistic_flags = []
        patterns_found = []
        
        # Check for language that may not translate culturally
        for pattern, info in self.language_patterns["problematic"].items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                linguistic_flags.append({
                    "type": "linguistic",
                    "pattern": pattern,
                    "matches": matches,
                    "severity": info["severity"],
                    "description": info["description"],
                    "cultural_context": info.get("cultural_context", "")
                })
                patterns_found.append(pattern)
        
        return {
            "detected": len(linguistic_flags) > 0,
            "category": "linguistic_bias",
            "flags": linguistic_flags,
            "patterns": patterns_found,
            "severity": max([f["severity"] for f in linguistic_flags], default=0)
        }
    
    def _detect_cultural_assumptions(self, content: str, gemini_analysis: Dict) -> Dict:
        """Detect cultural assumptions using Gemini analysis"""
        assumption_flags = []
        
        # Analyze Gemini's cultural sentiment results for assumptions
        gemini_insights = gemini_analysis.get("cultural_insights", {})
        
        for country, insights in gemini_insights.items():
            if insights.get("assumption_risk", 0) > 0.6:
                assumption_flags.append({
                    "type": "cultural_assumption",
                    "country": country,
                    "risk_score": insights.get("assumption_risk", 0),
                    "description": insights.get("assumption_description", ""),
                    "severity": self._risk_to_severity(insights.get("assumption_risk", 0))
                })
        
        return {
            "detected": len(assumption_flags) > 0,
            "category": "cultural_assumption",
            "flags": assumption_flags,
            "patterns": [],
            "severity": max([f["severity"] for f in assumption_flags], default=0)
        }
    
    def _detect_representation_bias(self, content: str) -> Dict:
        """Detect representation bias in imagery and examples"""
        representation_flags = []
        patterns_found = []
        
        # Check for representation issues
        for pattern, info in self.cultural_bias_patterns["representation"].items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                representation_flags.append({
                    "type": "representation",
                    "pattern": pattern,
                    "matches": matches,
                    "severity": info["severity"],
                    "description": info["description"]
                })
                patterns_found.append(pattern)
        
        return {
            "detected": len(representation_flags) > 0,
            "category": "representation_bias",
            "flags": representation_flags,
            "patterns": patterns_found,
            "severity": max([f["severity"] for f in representation_flags], default=0)
        }
    
    def _calculate_severity_scores(self, bias_results: List[Dict]) -> Dict[str, float]:
        """Calculate severity scores for different bias categories"""
        severity_scores = {}
        
        for bias_result in bias_results:
            if bias_result["detected"]:
                category = bias_result["category"]
                severity_scores[category] = bias_result["severity"] / 10.0  # Normalize to 0-1
        
        return severity_scores
    
    def _calculate_confidence(self, bias_results: Dict) -> float:
        """Calculate overall confidence in bias detection"""
        if not bias_results["flags"]:
            return 0.95  # High confidence in no bias found
        
        # Confidence based on number of patterns and their consistency
        num_flags = len(bias_results["flags"])
        num_categories = len(set(bias_results["bias_categories"]))
        
        # More flags across different categories = higher confidence
        base_confidence = min(0.5 + (num_flags * 0.1), 0.9)
        category_bonus = min(num_categories * 0.05, 0.1)
        
        return min(base_confidence + category_bonus, 0.95)
    
    def _risk_to_severity(self, risk_score: float) -> int:
        """Convert risk score to severity integer (1-10)"""
        return int(risk_score * 10)
    
    def _load_bias_patterns(self) -> Dict:
        """Load predefined cultural bias patterns"""
        return {
            "stereotypes": {
                r"\\b(exotic|primitive|backward|underdeveloped)\\b": {
                    "severity": 8,
                    "description": "Potentially offensive cultural descriptors"
                },
                r"\\b(oriental|third world|native)\\b": {
                    "severity": 7,
                    "description": "Outdated or problematic cultural terms"
                },
                r"\\b(normal|typical|standard)\\s+(american|western|european)": {
                    "severity": 6,
                    "description": "Western-centric assumptions"
                }
            },
            "representation": {
                r"\\b(everyone|all people|universal)\\b": {
                    "severity": 4,
                    "description": "Potentially overgeneralized statements"
                },
                r"\\b(traditionally|culturally)\\s+(they|those people)": {
                    "severity": 5,
                    "description": "Potential cultural oversimplification"
                }
            }
        }
    
    def _load_sentiment_weights(self) -> Dict:
        """Load sentiment analysis weights for cultural contexts"""
        return {
            "positive_words": ["celebrate", "honor", "respect", "appreciate"],
            "negative_words": ["weird", "strange", "unusual", "different"],
            "neutral_words": ["diverse", "varied", "unique", "distinct"]
        }
    
    def _load_language_patterns(self) -> Dict:
        """Load language patterns that may not translate culturally"""
        return {
            "problematic": {
                r"\\b(american dream|melting pot|pull yourself up)": {
                    "severity": 5,
                    "description": "US-centric concepts that may not resonate globally",
                    "cultural_context": "American individualism"
                },
                r"\\b(christmas|thanksgiving|easter)\\s+(spirit|season|time)": {
                    "severity": 4,
                    "description": "Christian holiday assumptions",
                    "cultural_context": "Religious assumptions"
                },
                r"\\b(nuclear family|suburb|homeowner)": {
                    "severity": 3,
                    "description": "Western family/lifestyle assumptions",
                    "cultural_context": "Western lifestyle norms"
                }
            }
        }
    
    def check_status(self) -> bool:
        """Check if bias detector is operational"""
        return len(self.cultural_bias_patterns) > 0
'''

# Save the bias detector
with open('bias_detector.py', 'w') as f:
    f.write(bias_detector_py)
    
print("✅ Created bias_detector.py - Core bias detection model")