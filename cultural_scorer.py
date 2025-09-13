"""
Cultural Scorer - Calculates cultural alignment scores and confidence intervals
"""
import json
import numpy as np
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class CulturalScorer:
    def __init__(self):
        """Initialize cultural scorer with data and weights"""
        self.hofstede_data = self._load_hofstede_data()
        self.scoring_weights = self._load_scoring_weights()

    def calculate_alignment(self, bias_results: Dict, cultural_analysis: Dict, target_countries: List[str]) -> Dict[str, Any]:
        """Calculate cultural alignment scores with confidence intervals"""
        try:
            alignment_results = {
                "overall_score": 0.0,
                "country_scores": {},
                "confidence": {},
                "score_breakdown": {}
            }

            country_scores = []

            for country in target_countries:
                # Calculate individual country alignment score
                country_score = self._calculate_country_score(country, bias_results, cultural_analysis)

                # Calculate confidence interval
                confidence_interval = self._calculate_confidence_interval(country, country_score, cultural_analysis)

                # Store results
                alignment_results["country_scores"][country] = country_score
                alignment_results["confidence"][country] = confidence_interval
                alignment_results["score_breakdown"][country] = self._get_score_breakdown(country, bias_results, cultural_analysis)

                country_scores.append(country_score)

            # Calculate overall alignment score
            if country_scores:
                alignment_results["overall_score"] = np.mean(country_scores)

            return alignment_results

        except Exception as e:
            logger.error(f"Cultural alignment calculation failed: {str(e)}")
            return {"error": str(e), "overall_score": 0.0}

    def _calculate_country_score(self, country: str, bias_results: Dict, cultural_analysis: Dict) -> float:
        """Calculate alignment score for specific country"""
        bias_penalty = self._calculate_bias_penalty(bias_results)
        cultural_fit_score = self._get_cultural_fit_score(country, cultural_analysis)
        confidence_bonus = self._calculate_confidence_bonus(country, cultural_analysis)

        weights = self.scoring_weights

        base_score = (
            cultural_fit_score * weights["cultural_fit"] +
            (1.0 - bias_penalty) * weights["bias_freedom"] +
            confidence_bonus * weights["confidence_bonus"]
        )

        return max(0.0, min(1.0, base_score))

    def _calculate_bias_penalty(self, bias_results: Dict) -> float:
        """Calculate penalty based on detected biases"""
        flags = bias_results.get("flags", [])
        if not flags:
            return 0.0

        total_penalty = 0.0
        for flag in flags:
            severity = flag.get("severity", 5)
            penalty = (severity / 10.0) * 0.1
            total_penalty += penalty

        return min(0.8, total_penalty)

    def _get_cultural_fit_score(self, country: str, cultural_analysis: Dict) -> float:
        """Extract cultural fit score for country"""
        cultural_scores = cultural_analysis.get("cultural_scores", {})
        return cultural_scores.get(country, 0.5)

    def _calculate_confidence_bonus(self, country: str, cultural_analysis: Dict) -> float:
        """Calculate confidence bonus based on data quality"""
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
        data_quality = self._assess_data_quality(country, cultural_analysis)

        if data_quality > 0.8:
            std_error = 0.05
        elif data_quality > 0.6:
            std_error = 0.10
        else:
            std_error = 0.15

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

        if country in self.hofstede_data:
            quality_score += 0.4

        if country in cultural_analysis.get("cultural_scores", {}):
            quality_score += 0.3

        if country in cultural_analysis.get("insights", {}):
            quality_score += 0.3

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
        """Return list of supported countries"""
        country_names = {
            "US": "United States", "UK": "United Kingdom", "JP": "Japan", "CN": "China",
            "DE": "Germany", "FR": "France", "IN": "India", "BR": "Brazil"
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
            }
        }

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
            "BR": {"PDI": 69, "IDV": 38, "MAS": 49, "UAI": 76, "LTO": 44, "IVR": 59}
        }

    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights for different components"""
        return {
            "cultural_fit": 0.7,
            "bias_freedom": 0.25,
            "confidence_bonus": 0.05
        }
