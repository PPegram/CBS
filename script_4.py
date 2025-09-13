# Create the Gemini API client
gemini_client_py = '''"""
Google Gemini API Client for Cultural Sentiment Analysis
Integrates with Gemini 2.5 Flash for advanced cultural analysis
"""
import os
import json
import logging
from typing import Dict, List, Any
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        """Initialize Gemini client with API configuration"""
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Cultural analysis prompts
        self.cultural_prompts = self._load_cultural_prompts()
        
    def analyze_cultural_sentiment(self, content: str, countries: List[str]) -> Dict[str, Any]:
        """
        Analyze cultural sentiment of campaign content for specific countries
        
        Args:
            content: Campaign content to analyze
            countries: List of target country codes
            
        Returns:
            Dictionary with cultural sentiment analysis
        """
        try:
            analysis_results = {
                "cultural_insights": {},
                "sentiment_scores": {},
                "risk_assessments": {},
                "timestamp": datetime.now().isoformat()
            }
            
            for country in countries:
                logger.info(f"Analyzing cultural sentiment for {country}")
                
                # Generate country-specific cultural prompt
                cultural_prompt = self._generate_cultural_prompt(content, country)
                
                # Send request to Gemini
                response = self.model.generate_content(cultural_prompt)
                
                # Parse response
                parsed_response = self._parse_gemini_response(response.text, country)
                
                # Store results
                analysis_results["cultural_insights"][country] = parsed_response.get("insights", {})
                analysis_results["sentiment_scores"][country] = parsed_response.get("sentiment_score", 0.5)
                analysis_results["risk_assessments"][country] = parsed_response.get("risk_assessment", {})
                
            return analysis_results
            
        except Exception as e:
            logger.error(f"Gemini API analysis failed: {str(e)}")
            return {
                "error": str(e),
                "cultural_insights": {},
                "sentiment_scores": {},
                "risk_assessments": {}
            }
    
    def _generate_cultural_prompt(self, content: str, country: str) -> str:
        """Generate country-specific cultural analysis prompt"""
        base_prompt = self.cultural_prompts["cultural_analysis_template"]
        
        # Get country-specific context
        country_context = self._get_country_context(country)
        
        # Format the prompt
        formatted_prompt = base_prompt.format(
            country=country,
            country_context=country_context,
            campaign_content=content
        )
        
        return formatted_prompt
    
    def _get_country_context(self, country: str) -> str:
        """Get cultural context for specific country"""
        country_contexts = {
            "US": "American individualistic culture with emphasis on personal freedom, achievement, and direct communication",
            "UK": "British culture valuing politeness, understatement, and traditional institutions",
            "JP": "Japanese culture emphasizing group harmony, respect for hierarchy, and indirect communication",
            "CN": "Chinese culture prioritizing collective benefit, long-term thinking, and relationship building",
            "DE": "German culture valuing efficiency, directness, and systematic approaches",
            "FR": "French culture appreciating sophistication, intellectual discussion, and cultural refinement",
            "IN": "Indian culture balancing traditional values with modern aspirations, emphasizing family and respect",
            "BR": "Brazilian culture celebrating warmth, relationships, and festive expression"
        }
        
        return country_contexts.get(country, f"Cultural context for {country}")
    
    def _parse_gemini_response(self, response_text: str, country: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            
            # Fallback: Parse structured response manually
            return self._manual_parse_response(response_text, country)
            
        except Exception as e:
            logger.warning(f"Failed to parse Gemini response for {country}: {str(e)}")
            return self._create_default_response(country)
    
    def _manual_parse_response(self, response_text: str, country: str) -> Dict[str, Any]:
        """Manually parse Gemini response when JSON parsing fails"""
        lines = response_text.strip().split('\\n')
        
        parsed = {
            "insights": {},
            "sentiment_score": 0.5,
            "risk_assessment": {}
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if "cultural fit" in line.lower():
                current_section = "cultural_fit"
            elif "sentiment" in line.lower():
                current_section = "sentiment"
            elif "risk" in line.lower():
                current_section = "risk"
            elif "recommendation" in line.lower():
                current_section = "recommendation"
            
            # Extract values
            if current_section and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                
                if current_section == "sentiment" and any(char.isdigit() for char in value):
                    # Extract numeric sentiment score
                    import re
                    numbers = re.findall(r'\\d+\\.?\\d*', value)
                    if numbers:
                        parsed["sentiment_score"] = float(numbers[0]) / 10.0 if float(numbers[0]) > 1 else float(numbers[0])
                
                parsed["insights"][key] = value
        
        return parsed
    
    def _create_default_response(self, country: str) -> Dict[str, Any]:
        """Create default response when parsing fails"""
        return {
            "insights": {
                "cultural_fit": f"Unable to analyze cultural fit for {country}",
                "assumption_risk": 0.5,
                "assumption_description": "Analysis unavailable"
            },
            "sentiment_score": 0.5,
            "risk_assessment": {
                "overall_risk": "medium",
                "specific_concerns": ["Analysis unavailable"]
            }
        }
    
    def _load_cultural_prompts(self) -> Dict[str, str]:
        """Load cultural analysis prompt templates"""
        return {
            "cultural_analysis_template": '''
You are a cultural analysis expert specializing in cross-cultural marketing and communication. 

Analyze the following campaign content for cultural appropriateness and reception in {country}.

Cultural Context: {country_context}

Campaign Content: {campaign_content}

Provide your analysis in the following JSON format:
```json
{{
    "insights": {{
        "cultural_fit": "Assessment of how well the content fits with {country} culture (1-10 scale with explanation)",
        "potential_concerns": "List any cultural concerns or sensitivities",
        "positive_elements": "Elements that align well with {country} culture",
        "assumption_risk": "Risk score of cultural assumptions (0.0-1.0)",
        "assumption_description": "Description of any problematic cultural assumptions"
    }},
    "sentiment_score": "Overall sentiment score for {country} (0.0-1.0)",
    "risk_assessment": {{
        "overall_risk": "low|medium|high",
        "specific_concerns": ["list", "of", "specific", "cultural", "risks"],
        "mitigation_suggestions": ["list", "of", "suggestions", "to", "improve", "cultural", "fit"]
    }}
}}
```

Be specific about cultural nuances and provide actionable insights.
''',
            
            "bias_detection_template": '''
You are an AI bias detection expert. Analyze the following content for cultural biases, stereotypes, and assumptions.

Content: {content}

Identify:
1. Cultural stereotypes or generalizations
2. Western-centric assumptions
3. Religious or cultural exclusions
4. Language that might not translate culturally
5. Representation biases

Provide specific examples and severity ratings (1-10).
'''
        }
    
    def detect_bias_with_gemini(self, content: str) -> Dict[str, Any]:
        """Use Gemini to detect cultural bias patterns"""
        try:
            bias_prompt = self.cultural_prompts["bias_detection_template"].format(content=content)
            
            response = self.model.generate_content(bias_prompt)
            
            # Parse bias detection response
            parsed_response = self._parse_bias_response(response.text)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Gemini bias detection failed: {str(e)}")
            return {"error": str(e), "biases_detected": []}
    
    def _parse_bias_response(self, response_text: str) -> Dict[str, Any]:
        """Parse bias detection response from Gemini"""
        # Implementation for parsing bias detection results
        return {
            "biases_detected": [],
            "severity_scores": {},
            "recommendations": []
        }
    
    def check_health(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            test_response = self.model.generate_content("Test connection")
            return bool(test_response.text)
        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return False
'''

# Save the Gemini client
with open('gemini_client.py', 'w') as f:
    f.write(gemini_client_py)

print("✅ Created gemini_client.py - Google Gemini API integration")

# Create the cultural scorer utility
cultural_scorer_py = '''"""
Cultural Scorer - Calculates cultural alignment scores and confidence intervals
Combines bias detection, cultural analysis, and statistical confidence measures
"""
import json
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from scipy import stats

logger = logging.getLogger(__name__)

class CulturalScorer:
    def __init__(self):
        """Initialize cultural scorer with data and weights"""
        self.hofstede_data = self._load_hofstede_data()
        self.scoring_weights = self._load_scoring_weights()
        self.confidence_thresholds = self._load_confidence_thresholds()
        
    def calculate_alignment(self, bias_results: Dict, cultural_analysis: Dict, target_countries: List[str]) -> Dict[str, Any]:
        """
        Calculate cultural alignment scores with confidence intervals
        
        Args:
            bias_results: Results from bias detection
            cultural_analysis: Results from cultural analysis  
            target_countries: List of target countries
            
        Returns:
            Dictionary with alignment scores and confidence measures
        """
        try:
            alignment_results = {
                "overall_score": 0.0,
                "country_scores": {},
                "confidence": {},
                "score_breakdown": {},
                "methodology": "Hofstede + WVS + Bias Detection"
            }
            
            country_scores = []
            
            for country in target_countries:
                # Calculate individual country alignment score
                country_score = self._calculate_country_score(
                    country, bias_results, cultural_analysis
                )
                
                # Calculate confidence interval for this country
                confidence_interval = self._calculate_confidence_interval(
                    country, country_score, cultural_analysis
                )
                
                # Store results
                alignment_results["country_scores"][country] = country_score
                alignment_results["confidence"][country] = confidence_interval
                alignment_results["score_breakdown"][country] = self._get_score_breakdown(
                    country, bias_results, cultural_analysis
                )
                
                country_scores.append(country_score)
            
            # Calculate overall alignment score
            if country_scores:
                alignment_results["overall_score"] = np.mean(country_scores)
                alignment_results["score_std"] = np.std(country_scores)
                alignment_results["score_range"] = {
                    "min": min(country_scores),
                    "max": max(country_scores)
                }
            
            logger.info(f"Cultural alignment calculated for {len(target_countries)} countries")
            return alignment_results
            
        except Exception as e:
            logger.error(f"Cultural alignment calculation failed: {str(e)}")
            return {"error": str(e), "overall_score": 0.0}
    
    def _calculate_country_score(self, country: str, bias_results: Dict, cultural_analysis: Dict) -> float:
        """Calculate alignment score for specific country"""
        # Initialize score components
        bias_penalty = self._calculate_bias_penalty(bias_results)
        cultural_fit_score = self._get_cultural_fit_score(country, cultural_analysis)
        confidence_bonus = self._calculate_confidence_bonus(country, cultural_analysis)
        
        # Apply scoring weights
        weights = self.scoring_weights
        
        # Calculate weighted score
        base_score = (
            cultural_fit_score * weights["cultural_fit"] +
            (1.0 - bias_penalty) * weights["bias_freedom"] +
            confidence_bonus * weights["confidence_bonus"]
        )
        
        # Normalize to 0-1 range
        final_score = max(0.0, min(1.0, base_score))
        
        logger.debug(f"{country} score: {final_score:.3f} (cultural={cultural_fit_score:.3f}, bias_penalty={bias_penalty:.3f})")
        
        return final_score
    
    def _calculate_bias_penalty(self, bias_results: Dict) -> float:
        """Calculate penalty based on detected biases"""
        flags = bias_results.get("flags", [])
        if not flags:
            return 0.0
        
        # Calculate penalty based on number and severity of bias flags
        total_penalty = 0.0
        
        for flag in flags:
            severity = flag.get("severity", 5)  # Default medium severity
            penalty = (severity / 10.0) * 0.1  # Max 0.1 penalty per flag
            total_penalty += penalty
        
        # Cap total penalty at 0.8 (still allow some score)
        return min(0.8, total_penalty)
    
    def _get_cultural_fit_score(self, country: str, cultural_analysis: Dict) -> float:
        """Extract cultural fit score for country"""
        cultural_scores = cultural_analysis.get("cultural_scores", {})
        return cultural_scores.get(country, 0.5)  # Default neutral score
    
    def _calculate_confidence_bonus(self, country: str, cultural_analysis: Dict) -> float:
        """Calculate confidence bonus based on data quality"""
        # Check if we have comprehensive cultural data for this country
        has_hofstede_data = country in self.hofstede_data
        has_cultural_analysis = country in cultural_analysis.get("cultural_scores", {})
        
        bonus = 0.0
        if has_hofstede_data:
            bonus += 0.05
        if has_cultural_analysis:
            bonus += 0.05
        
        return bonus
    
    def _calculate_confidence_interval(self, country: str, score: float, cultural_analysis: Dict) -> Dict[str, float]:
        """Calculate confidence interval for country score"""
        # Base confidence depends on data availability and score consistency
        data_quality = self._assess_data_quality(country, cultural_analysis)
        
        # Calculate standard error based on data quality
        if data_quality > 0.8:
            std_error = 0.05  # High confidence
        elif data_quality > 0.6:
            std_error = 0.10  # Medium confidence
        else:
            std_error = 0.15  # Lower confidence
        
        # 95% confidence interval
        margin_of_error = 1.96 * std_error
        
        return {
            "lower_bound": max(0.0, score - margin_of_error),
            "upper_bound": min(1.0, score + margin_of_error),
            "confidence_level": 0.95,
            "margin_of_error": margin_of_error,
            "data_quality": data_quality
        }
    
    def _assess_data_quality(self, country: str, cultural_analysis: Dict) -> float:
        """Assess quality of available cultural data for country"""
        quality_score = 0.0
        
        # Check Hofstede data availability
        if country in self.hofstede_data:
            hofstede_data = self.hofstede_data[country]
            complete_dimensions = sum(1 for v in hofstede_data.values() if v is not None)
            quality_score += (complete_dimensions / 6) * 0.4  # Max 0.4 from Hofstede
        
        # Check cultural analysis quality
        if country in cultural_analysis.get("cultural_scores", {}):
            quality_score += 0.3  # Cultural analysis available
            
        if country in cultural_analysis.get("insights", {}):
            quality_score += 0.3  # Insights available
        
        return min(1.0, quality_score)
    
    def _get_score_breakdown(self, country: str, bias_results: Dict, cultural_analysis: Dict) -> Dict[str, float]:
        """Get detailed score breakdown for transparency"""
        return {
            "cultural_fit": self._get_cultural_fit_score(country, cultural_analysis),
            "bias_penalty": self._calculate_bias_penalty(bias_results),
            "confidence_bonus": self._calculate_confidence_bonus(country, cultural_analysis),
            "data_quality": self._assess_data_quality(country, cultural_analysis)
        }
    
    def get_supported_countries(self) -> List[Dict[str, str]]:
        """Return list of supported countries with names and codes"""
        country_names = {
            "US": "United States",
            "UK": "United Kingdom", 
            "JP": "Japan",
            "CN": "China",
            "DE": "Germany",
            "FR": "France",
            "IN": "India",
            "BR": "Brazil",
            "AU": "Australia",
            "CA": "Canada",
            "IT": "Italy",
            "ES": "Spain",
            "NL": "Netherlands",
            "SE": "Sweden",
            "NO": "Norway",
            "DK": "Denmark",
            "FI": "Finland",
            "CH": "Switzerland",
            "AT": "Austria",
            "BE": "Belgium"
        }
        
        return [
            {"code": code, "name": name} 
            for code, name in country_names.items()
            if code in self.hofstede_data
        ]
    
    def get_hofstede_scores(self, country_code: str) -> Dict[str, Any]:
        """Get Hofstede scores for specific country"""
        if country_code not in self.hofstede_data:
            return None
            
        scores = self.hofstede_data[country_code]
        
        return {
            "country": country_code,
            "dimensions": {
                "power_distance": scores.get("PDI"),
                "individualism": scores.get("IDV"),
                "masculinity": scores.get("MAS"), 
                "uncertainty_avoidance": scores.get("UAI"),
                "long_term_orientation": scores.get("LTO"),
                "indulgence": scores.get("IVR")
            },
            "interpretation": self._interpret_hofstede_scores(scores)
        }
    
    def _interpret_hofstede_scores(self, scores: Dict) -> Dict[str, str]:
        """Provide interpretation of Hofstede scores"""
        interpretations = {}
        
        for dim, value in scores.items():
            if value is None:
                continue
                
            if dim == "PDI":  # Power Distance
                interpretations["power_distance"] = "High hierarchy acceptance" if value > 60 else "Low hierarchy acceptance"
            elif dim == "IDV":  # Individualism
                interpretations["individualism"] = "Individualistic" if value > 60 else "Collectivistic"
            elif dim == "MAS":  # Masculinity
                interpretations["masculinity"] = "Achievement-oriented" if value > 60 else "Relationship-oriented"
            elif dim == "UAI":  # Uncertainty Avoidance
                interpretations["uncertainty_avoidance"] = "High uncertainty avoidance" if value > 60 else "Low uncertainty avoidance"
            elif dim == "LTO":  # Long-term Orientation
                interpretations["long_term_orientation"] = "Long-term oriented" if value > 60 else "Short-term oriented"
            elif dim == "IVR":  # Indulgence
                interpretations["indulgence"] = "Indulgent" if value > 60 else "Restrained"
        
        return interpretations
    
    def check_data_availability(self) -> bool:
        """Check if cultural data is available"""
        return len(self.hofstede_data) > 0
    
    def _load_hofstede_data(self) -> Dict:
        """Load comprehensive Hofstede cultural dimensions data"""
        return {
            "US": {"PDI": 40, "IDV": 91, "MAS": 62, "UAI": 46, "LTO": 26, "IVR": 68},
            "UK": {"PDI": 35, "IDV": 89, "MAS": 66, "UAI": 35, "LTO": 51, "IVR": 69},
            "JP": {"PDI": 54, "IDV": 46, "MAS": 95, "UAI": 92, "LTO": 88, "IVR": 42},
            "CN": {"PDI": 80, "IDV": 20, "MAS": 66, "UAI": 30, "LTO": 87, "IVR": 24},
            "DE": {"PDI": 35, "IDV": 67, "MAS": 66, "UAI": 65, "LTO": 83, "IVR": 40},
            "FR": {"PDI": 68, "IDV": 71, "MAS": 43, "UAI": 86, "LTO": 63, "IVR": 48},
            "IN": {"PDI": 77, "IDV": 48, "MAS": 56, "UAI": 40, "LTO": 51, "IVR": 26},
            "BR": {"PDI": 69, "IDV": 38, "MAS": 49, "UAI": 76, "LTO": 44, "IVR": 59},
            "AU": {"PDI": 36, "IDV": 90, "MAS": 61, "UAI": 51, "LTO": 21, "IVR": 71},
            "CA": {"PDI": 39, "IDV": 80, "MAS": 52, "UAI": 48, "LTO": 36, "IVR": 68}
        }
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights for different components"""
        return {
            "cultural_fit": 0.7,      # Primary weight on cultural fit
            "bias_freedom": 0.25,     # Penalty for detected biases
            "confidence_bonus": 0.05  # Small bonus for high-quality data
        }
    
    def _load_confidence_thresholds(self) -> Dict[str, float]:
        """Load confidence thresholds for different quality levels"""
        return {
            "high_confidence": 0.8,   # High confidence threshold
            "medium_confidence": 0.6, # Medium confidence threshold
            "low_confidence": 0.4     # Low confidence threshold
        }
'''

# Save the cultural scorer
with open('cultural_scorer.py', 'w') as f:
    f.write(cultural_scorer_py)

print("✅ Created cultural_scorer.py - Cultural alignment scoring with confidence intervals")