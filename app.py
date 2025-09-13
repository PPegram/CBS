"""
Cultural Bias Shield - Main Flask Application
AI-Powered Campaign Cultural Risk Assessment Tool
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime

# Import custom modules
from models.bias_detector import BiasDetector
from models.cultural_analyzer import CulturalAnalyzer
from utils.gemini_client import GeminiClient
from utils.cultural_scorer import CulturalScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize core components
gemini_client = GeminiClient()
bias_detector = BiasDetector()
cultural_analyzer = CulturalAnalyzer()
cultural_scorer = CulturalScorer()

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_campaign():
    """
    Main endpoint for cultural bias analysis

    Expected payload:
    {
        "campaign_content": "Campaign text/description",
        "target_countries": ["US", "UK", "JP", "CN"],
        "campaign_type": "social_media|display|video",
        "industry": "fashion|tech|food|finance"
    }
    """
    try:
        data = request.json
        campaign_content = data.get('campaign_content', '')
        target_countries = data.get('target_countries', [])
        campaign_type = data.get('campaign_type', 'social_media')
        industry = data.get('industry', 'general')

        logger.info(f"Analyzing campaign for countries: {target_countries}")

        # Step 1: Generate cultural sentiment analysis using Gemini
        gemini_analysis = gemini_client.analyze_cultural_sentiment(
            content=campaign_content,
            countries=target_countries
        )

        # Step 2: Detect potential bias patterns
        bias_results = bias_detector.detect_bias(
            content=campaign_content,
            gemini_analysis=gemini_analysis
        )

        # Step 3: Analyze cultural dimensions
        cultural_analysis = cultural_analyzer.analyze_cultural_fit(
            content=campaign_content,
            countries=target_countries,
            industry=industry
        )

        # Step 4: Calculate cultural alignment scores
        alignment_scores = cultural_scorer.calculate_alignment(
            bias_results=bias_results,
            cultural_analysis=cultural_analysis,
            target_countries=target_countries
        )

        # Step 5: Generate recommendations
        recommendations = _generate_recommendations(
            alignment_scores, cultural_analysis, target_countries
        )

        # Compile final response
        response = {
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "overall_score": alignment_scores.get('overall_score', 0),
            "country_scores": alignment_scores.get('country_scores', {}),
            "bias_flags": bias_results.get('flags', []),
            "cultural_insights": cultural_analysis.get('insights', {}),
            "recommendations": recommendations,
            "risk_level": _calculate_risk_level(alignment_scores),
            "confidence_intervals": alignment_scores.get('confidence', {}),
            "processing_time": datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/api/countries', methods=['GET'])
def get_supported_countries():
    """Return list of supported countries with cultural data"""
    return jsonify({
        "countries": cultural_scorer.get_supported_countries(),
        "total_count": len(cultural_scorer.get_supported_countries())
    })

@app.route('/api/cultural-dimensions/<country_code>', methods=['GET'])
def get_cultural_dimensions(country_code):
    """Get Hofstede cultural dimensions for specific country"""
    dimensions = cultural_scorer.get_hofstede_scores(country_code)
    if dimensions:
        return jsonify(dimensions)
    return jsonify({"error": "Country not found"}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini_api": gemini_client.check_health(),
            "cultural_data": cultural_scorer.check_data_availability(),
            "bias_detector": bias_detector.check_status()
        }
    })

def _generate_recommendations(alignment_scores, cultural_analysis, target_countries):
    """Generate actionable recommendations based on analysis"""
    recommendations = []

    for country in target_countries:
        score = alignment_scores.get('country_scores', {}).get(country, 0)

        if score < 0.6:  # Low alignment score
            recommendations.append({
                "country": country,
                "priority": "high",
                "type": "cultural_adaptation",
                "message": f"Consider significant cultural adaptation for {country}",
                "specific_suggestions": cultural_analysis.get('suggestions', {}).get(country, [])
            })
        elif score < 0.8:  # Medium alignment score
            recommendations.append({
                "country": country,
                "priority": "medium", 
                "type": "minor_adjustments",
                "message": f"Minor cultural adjustments recommended for {country}",
                "specific_suggestions": cultural_analysis.get('suggestions', {}).get(country, [])
            })

    return recommendations

def _calculate_risk_level(alignment_scores):
    """Calculate overall campaign risk level"""
    overall_score = alignment_scores.get('overall_score', 0)

    if overall_score >= 0.8:
        return "low"
    elif overall_score >= 0.6:
        return "medium"
    else:
        return "high"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
