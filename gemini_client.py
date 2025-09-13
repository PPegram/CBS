"""
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
        """Analyze cultural sentiment of campaign content for specific countries"""
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
        lines = response_text.strip().split('\n')

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
                    numbers = re.findall(r'\d+\.?\d*', value)
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

        cultural_analysis_template = """You are a cultural analysis expert specializing in cross-cultural marketing and communication. 

Analyze the following campaign content for cultural appropriateness and reception in {country}.

Cultural Context: {country_context}

Campaign Content: {campaign_content}

Provide your analysis in the following JSON format:
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

Be specific about cultural nuances and provide actionable insights."""

        bias_detection_template = """You are an AI bias detection expert. Analyze the following content for cultural biases, stereotypes, and assumptions.

Content: {content}

Identify:
1. Cultural stereotypes or generalizations
2. Western-centric assumptions
3. Religious or cultural exclusions
4. Language that might not translate culturally
5. Representation biases

Provide specific examples and severity ratings (1-10)."""

        return {
            "cultural_analysis_template": cultural_analysis_template,
            "bias_detection_template": bias_detection_template
        }

    def check_health(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            test_response = self.model.generate_content("Test connection")
            return bool(test_response.text)
        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return False
