"""
Cultural Analyzer - Hofstede Dimensions & World Values Survey Integration
Analyzes campaign content against cultural dimensions and values
"""
import json
import numpy as np
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class CulturalAnalyzer:
    def __init__(self):
        """Initialize cultural analyzer with Hofstede and WVS data"""
        self.hofstede_data = self._load_hofstede_data()
        self.wvs_mappings = self._load_wvs_mappings()
        self.cultural_keywords = self._load_cultural_keywords()

    def analyze_cultural_fit(self, content: str, countries: List[str], industry: str = "general") -> Dict[str, Any]:
        """
        Analyze how well campaign content fits with target countries' cultural values

        Args:
            content: Campaign content to analyze
            countries: List of target country codes
            industry: Industry context for analysis

        Returns:
            Cultural analysis results
        """
        try:
            analysis_results = {
                "cultural_scores": {},
                "dimension_analysis": {},
                "insights": {},
                "suggestions": {},
                "industry_context": industry
            }

            for country in countries:
                # Get cultural dimensions for country
                dimensions = self.hofstede_data.get(country, {})
                if not dimensions:
                    logger.warning(f"No cultural data available for {country}")
                    continue

                # Analyze content against each cultural dimension
                dimension_scores = self._analyze_dimensions(content, dimensions, country)

                # Calculate overall cultural fit score
                cultural_score = self._calculate_cultural_score(dimension_scores)

                # Generate insights and suggestions
                insights = self._generate_insights(content, dimensions, dimension_scores, country)
                suggestions = self._generate_suggestions(dimension_scores, country, industry)

                # Store results
                analysis_results["cultural_scores"][country] = cultural_score
                analysis_results["dimension_analysis"][country] = dimension_scores
                analysis_results["insights"][country] = insights
                analysis_results["suggestions"][country] = suggestions

            logger.info(f"Cultural analysis completed for {len(countries)} countries")
            return analysis_results

        except Exception as e:
            logger.error(f"Cultural analysis failed: {str(e)}")
            return {"error": str(e)}

    def _analyze_dimensions(self, content: str, dimensions: Dict, country: str) -> Dict[str, float]:
        """Analyze content against Hofstede's 6 cultural dimensions"""
        dimension_scores = {}

        # Power Distance Index (PDI)
        pdi_score = self._analyze_power_distance(content, dimensions.get("PDI", 50))
        dimension_scores["power_distance"] = pdi_score

        # Individualism vs Collectivism (IDV)
        idv_score = self._analyze_individualism(content, dimensions.get("IDV", 50))
        dimension_scores["individualism"] = idv_score

        # Masculinity vs Femininity (MAS)
        mas_score = self._analyze_masculinity(content, dimensions.get("MAS", 50))
        dimension_scores["masculinity"] = mas_score

        # Uncertainty Avoidance Index (UAI)
        uai_score = self._analyze_uncertainty_avoidance(content, dimensions.get("UAI", 50))
        dimension_scores["uncertainty_avoidance"] = uai_score

        # Long-term vs Short-term Orientation (LTO)
        lto_score = self._analyze_long_term_orientation(content, dimensions.get("LTO", 50))
        dimension_scores["long_term_orientation"] = lto_score

        # Indulgence vs Restraint (IVR)
        ivr_score = self._analyze_indulgence(content, dimensions.get("IVR", 50))
        dimension_scores["indulgence"] = ivr_score

        return dimension_scores

    def _analyze_power_distance(self, content: str, pdi_value: float) -> float:
        """Analyze content alignment with Power Distance dimension"""
        # Keywords indicating high power distance
        high_pd_keywords = ["hierarchy", "authority", "boss", "leader", "executive", "management"]
        low_pd_keywords = ["equality", "peer", "team", "collaborative", "democratic", "accessible"]

        high_pd_count = sum(1 for word in high_pd_keywords if word.lower() in content.lower())
        low_pd_count = sum(1 for word in low_pd_keywords if word.lower() in content.lower())

        content_pd_tendency = (high_pd_count - low_pd_count) / max(1, high_pd_count + low_pd_count)
        country_pd_tendency = (pdi_value - 50) / 50  # Normalize to -1 to 1

        # Calculate alignment (1.0 = perfect alignment, 0.0 = complete misalignment)
        alignment = 1.0 - abs(content_pd_tendency - country_pd_tendency) / 2
        return max(0.0, alignment)

    def _analyze_individualism(self, content: str, idv_value: float) -> float:
        """Analyze content alignment with Individualism dimension"""
        individualistic_keywords = ["individual", "personal", "self", "independence", "freedom", "choice"]
        collectivistic_keywords = ["community", "team", "together", "family", "group", "collective"]

        ind_count = sum(1 for word in individualistic_keywords if word.lower() in content.lower())
        col_count = sum(1 for word in collectivistic_keywords if word.lower() in content.lower())

        content_idv_tendency = (ind_count - col_count) / max(1, ind_count + col_count)
        country_idv_tendency = (idv_value - 50) / 50

        alignment = 1.0 - abs(content_idv_tendency - country_idv_tendency) / 2
        return max(0.0, alignment)

    def _analyze_masculinity(self, content: str, mas_value: float) -> float:
        """Analyze content alignment with Masculinity dimension"""
        masculine_keywords = ["compete", "win", "achieve", "success", "performance", "ambitious"]
        feminine_keywords = ["caring", "quality", "cooperation", "relationships", "supportive", "nurturing"]

        mas_count = sum(1 for word in masculine_keywords if word.lower() in content.lower())
        fem_count = sum(1 for word in feminine_keywords if word.lower() in content.lower())

        content_mas_tendency = (mas_count - fem_count) / max(1, mas_count + fem_count)
        country_mas_tendency = (mas_value - 50) / 50

        alignment = 1.0 - abs(content_mas_tendency - country_mas_tendency) / 2
        return max(0.0, alignment)

    def _analyze_uncertainty_avoidance(self, content: str, uai_value: float) -> float:
        """Analyze content alignment with Uncertainty Avoidance dimension"""
        high_uai_keywords = ["security", "certainty", "rules", "structure", "planning", "reliable"]
        low_uai_keywords = ["flexible", "adaptable", "innovation", "risk", "experiment", "spontaneous"]

        high_uai_count = sum(1 for word in high_uai_keywords if word.lower() in content.lower())
        low_uai_count = sum(1 for word in low_uai_keywords if word.lower() in content.lower())

        content_uai_tendency = (high_uai_count - low_uai_count) / max(1, high_uai_count + low_uai_count)
        country_uai_tendency = (uai_value - 50) / 50

        alignment = 1.0 - abs(content_uai_tendency - country_uai_tendency) / 2
        return max(0.0, alignment)

    def _analyze_long_term_orientation(self, content: str, lto_value: float) -> float:
        """Analyze content alignment with Long-term Orientation dimension"""
        long_term_keywords = ["future", "tradition", "persistence", "patience", "investment", "sustainable"]
        short_term_keywords = ["immediate", "quick", "now", "instant", "current", "present"]

        lt_count = sum(1 for word in long_term_keywords if word.lower() in content.lower())
        st_count = sum(1 for word in short_term_keywords if word.lower() in content.lower())

        content_lto_tendency = (lt_count - st_count) / max(1, lt_count + st_count)
        country_lto_tendency = (lto_value - 50) / 50

        alignment = 1.0 - abs(content_lto_tendency - country_lto_tendency) / 2
        return max(0.0, alignment)

    def _analyze_indulgence(self, content: str, ivr_value: float) -> float:
        """Analyze content alignment with Indulgence dimension"""
        indulgent_keywords = ["enjoy", "fun", "pleasure", "freedom", "happiness", "celebration"]
        restrained_keywords = ["control", "discipline", "modest", "serious", "formal", "conservative"]

        ind_count = sum(1 for word in indulgent_keywords if word.lower() in content.lower())
        res_count = sum(1 for word in restrained_keywords if word.lower() in content.lower())

        content_ivr_tendency = (ind_count - res_count) / max(1, ind_count + res_count)
        country_ivr_tendency = (ivr_value - 50) / 50

        alignment = 1.0 - abs(content_ivr_tendency - country_ivr_tendency) / 2
        return max(0.0, alignment)

    def _calculate_cultural_score(self, dimension_scores: Dict[str, float]) -> float:
        """Calculate overall cultural fit score"""
        if not dimension_scores:
            return 0.0

        # Weight dimensions based on research importance
        weights = {
            "power_distance": 0.20,
            "individualism": 0.25,
            "masculinity": 0.15,
            "uncertainty_avoidance": 0.20,
            "long_term_orientation": 0.10,
            "indulgence": 0.10
        }

        weighted_score = sum(
            dimension_scores.get(dim, 0.5) * weight 
            for dim, weight in weights.items()
        )

        return weighted_score

    def _generate_insights(self, content: str, dimensions: Dict, scores: Dict[str, float], country: str) -> Dict[str, Any]:
        """Generate cultural insights for specific country"""
        insights = {
            "alignment_summary": "",
            "strongest_alignment": "",
            "weakest_alignment": "",
            "cultural_notes": []
        }

        # Find strongest and weakest alignments
        if scores:
            strongest_dim = max(scores.keys(), key=lambda k: scores[k])
            weakest_dim = min(scores.keys(), key=lambda k: scores[k])

            insights["strongest_alignment"] = f"{strongest_dim}: {scores[strongest_dim]:.2f}"
            insights["weakest_alignment"] = f"{weakest_dim}: {scores[weakest_dim]:.2f}"

            overall_score = self._calculate_cultural_score(scores)
            if overall_score > 0.8:
                insights["alignment_summary"] = f"Excellent cultural alignment with {country}"
            elif overall_score > 0.6:
                insights["alignment_summary"] = f"Good cultural alignment with {country}"
            else:
                insights["alignment_summary"] = f"Cultural misalignment detected for {country}"

        # Add specific cultural notes
        insights["cultural_notes"] = self._get_cultural_notes(country, dimensions)

        return insights

    def _generate_suggestions(self, scores: Dict[str, float], country: str, industry: str) -> List[str]:
        """Generate specific suggestions for improving cultural alignment"""
        suggestions = []

        for dimension, score in scores.items():
            if score < 0.6:  # Low alignment
                suggestion = self._get_dimension_suggestion(dimension, country, industry)
                if suggestion:
                    suggestions.append(suggestion)

        return suggestions

    def _get_dimension_suggestion(self, dimension: str, country: str, industry: str) -> str:
        """Get specific suggestion for improving dimension alignment"""
        suggestions_map = {
            "power_distance": {
                "high": "Consider emphasizing hierarchy, authority, and formal structures",
                "low": "Focus on equality, accessibility, and collaborative approaches"
            },
            "individualism": {
                "high": "Highlight personal choice, individual benefits, and self-expression",
                "low": "Emphasize community, family, and collective benefits"
            },
            "masculinity": {
                "high": "Focus on achievement, competition, and performance metrics",
                "low": "Emphasize cooperation, quality of life, and relationships"
            },
            "uncertainty_avoidance": {
                "high": "Provide security, guarantees, and detailed information",
                "low": "Embrace flexibility, innovation, and risk-taking"
            },
            "long_term_orientation": {
                "high": "Emphasize tradition, patience, and long-term benefits",
                "low": "Focus on immediate results and current trends"
            },
            "indulgence": {
                "high": "Highlight enjoyment, freedom, and positive emotions",
                "low": "Emphasize control, modesty, and serious benefits"
            }
        }

        dimension_suggestions = suggestions_map.get(dimension, {})
        country_tendency = self._get_country_tendency(dimension, country)

        return dimension_suggestions.get(country_tendency, f"Adjust {dimension} alignment for {country}")

    def _get_country_tendency(self, dimension: str, country: str) -> str:
        """Determine if country has high or low tendency for given dimension"""
        dimensions = self.hofstede_data.get(country, {})
        value = dimensions.get(self._dimension_code_map().get(dimension, dimension), 50)

        return "high" if value > 50 else "low"

    def _dimension_code_map(self) -> Dict[str, str]:
        """Map dimension names to Hofstede codes"""
        return {
            "power_distance": "PDI",
            "individualism": "IDV", 
            "masculinity": "MAS",
            "uncertainty_avoidance": "UAI",
            "long_term_orientation": "LTO",
            "indulgence": "IVR"
        }

    def _get_cultural_notes(self, country: str, dimensions: Dict) -> List[str]:
        """Get cultural notes for specific country"""
        notes = []

        # Add notes based on extreme dimension values
        for dim_code, value in dimensions.items():
            if value > 80:
                notes.append(f"Very high {dim_code}: Consider strong alignment with this cultural trait")
            elif value < 20:
                notes.append(f"Very low {dim_code}: Avoid assumptions related to this cultural trait")

        return notes

    def _load_hofstede_data(self) -> Dict:
        """Load Hofstede cultural dimensions data"""
        # Sample data - in production, load from comprehensive dataset
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

    def _load_wvs_mappings(self) -> Dict:
        """Load World Values Survey variable mappings"""
        return {
            "happiness": "A008",
            "life_satisfaction": "A170", 
            "importance_family": "A001",
            "trust_most_people": "A165",
            "importance_work": "A002"
        }

    def _load_cultural_keywords(self) -> Dict:
        """Load cultural keyword mappings"""
        return {
            "power_distance": {
                "high": ["hierarchy", "authority", "boss", "leader"],
                "low": ["equality", "peer", "democratic", "accessible"]
            },
            "individualism": {
                "high": ["individual", "personal", "self", "independence"],
                "low": ["community", "team", "family", "collective"]
            }
        }
