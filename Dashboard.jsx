"""
Main Dashboard Component - Cultural Bias Shield
React component for the cultural bias analysis interface
"""
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Container, Grid, Card, CardContent, Typography, Button, 
  TextField, Chip, CircularProgress, Alert, Box,
  FormControl, InputLabel, Select, MenuItem, Checkbox,
  FormControlLabel, LinearProgress
} from '@mui/material';
import { 
  Assessment as AssessmentIcon, 
  Public as PublicIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import BiasAnalyzer from './BiasAnalyzer';
import CulturalMap from './CulturalMap';
import api from '../services/api';

const Dashboard = () => {
  // State management
  const [campaignContent, setCampaignContent] = useState('');
  const [targetCountries, setTargetCountries] = useState([]);
  const [campaignType, setCampaignType] = useState('social_media');
  const [industry, setIndustry] = useState('general');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableCountries, setAvailableCountries] = useState([]);

  // Sample campaign content for demo
  const sampleContent = `Unlock your potential with our revolutionary fitness app! 
Join millions of successful individuals who have transformed their lives. 
Our American-designed program delivers results faster than traditional methods. 
Perfect for busy professionals who demand excellence and won't settle for anything less.`;

  useEffect(() => {
    // Load available countries on component mount
    loadAvailableCountries();
  }, []);

  const loadAvailableCountries = async () => {
    try {
      const response = await api.get('/countries');
      setAvailableCountries(response.data.countries);
    } catch (err) {
      console.error('Failed to load countries:', err);
    }
  };

  const handleCountrySelection = (country) => {
    setTargetCountries(prev => {
      const isSelected = prev.includes(country.code);
      if (isSelected) {
        return prev.filter(c => c !== country.code);
      } else {
        return [...prev, country.code];
      }
    });
  };

  const analyzeCampaign = async () => {
    if (!campaignContent.trim()) {
      setError('Please enter campaign content to analyze');
      return;
    }

    if (targetCountries.length === 0) {
      setError('Please select at least one target country');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestData = {
        campaign_content: campaignContent,
        target_countries: targetCountries,
        campaign_type: campaignType,
        industry: industry
      };

      const response = await api.post('/analyze', requestData);
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleContent = () => {
    setCampaignContent(sampleContent);
    setTargetCountries(['US', 'UK', 'JP', 'CN']);
    setCampaignType('social_media');
    setIndustry('fitness');
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return '#4caf50';
      case 'medium': return '#ff9800'; 
      case 'high': return '#f44336';
      default: return '#757575';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return <CheckCircleIcon style={{ color: '#4caf50' }} />;
      case 'medium': return <WarningIcon style={{ color: '#ff9800' }} />;
      case 'high': return <WarningIcon style={{ color: '#f44336' }} />;
      default: return <AssessmentIcon />;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          🛡️ Cultural Bias Shield
        </Typography>
        <Typography variant="h6" color="text.secondary">
          AI-Powered Campaign Cultural Risk Assessment
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Campaign Analysis
              </Typography>

              <Box sx={{ mb: 3 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  label="Campaign Content"
                  value={campaignContent}
                  onChange={(e) => setCampaignContent(e.target.value)}
                  placeholder="Enter your campaign content here..."
                  variant="outlined"
                />
                <Button 
                  size="small" 
                  onClick={loadSampleContent}
                  sx={{ mt: 1 }}
                >
                  Load Sample Content
                </Button>
              </Box>

              <Box sx={{ mb: 3 }}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Campaign Type</InputLabel>
                  <Select
                    value={campaignType}
                    onChange={(e) => setCampaignType(e.target.value)}
                    label="Campaign Type"
                  >
                    <MenuItem value="social_media">Social Media</MenuItem>
                    <MenuItem value="display">Display Advertising</MenuItem>
                    <MenuItem value="video">Video Campaign</MenuItem>
                    <MenuItem value="email">Email Marketing</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Industry</InputLabel>
                  <Select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    label="Industry"
                  >
                    <MenuItem value="general">General</MenuItem>
                    <MenuItem value="fitness">Fitness & Wellness</MenuItem>
                    <MenuItem value="tech">Technology</MenuItem>
                    <MenuItem value="fashion">Fashion</MenuItem>
                    <MenuItem value="finance">Finance</MenuItem>
                    <MenuItem value="food">Food & Beverage</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Typography variant="h6" gutterBottom>
                <PublicIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Target Countries
              </Typography>

              <Box sx={{ mb: 3, maxHeight: 200, overflow: 'auto' }}>
                {availableCountries.map((country) => (
                  <FormControlLabel
                    key={country.code}
                    control={
                      <Checkbox
                        checked={targetCountries.includes(country.code)}
                        onChange={() => handleCountrySelection(country)}
                      />
                    }
                    label={`${country.name} (${country.code})`}
                  />
                ))}
              </Box>

              <Button
                variant="contained"
                size="large"
                onClick={analyzeCampaign}
                disabled={loading}
                fullWidth
                sx={{ mb: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze Cultural Risk'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          {analysis && (
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Analysis Results
                </Typography>

                {/* Overall Score */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    {getRiskIcon(analysis.risk_level)}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      Overall Cultural Alignment: {(analysis.overall_score * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.overall_score * 100}
                    sx={{ 
                      height: 10, 
                      borderRadius: 5,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getRiskColor(analysis.risk_level)
                      }
                    }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Risk Level: {analysis.risk_level.toUpperCase()}
                  </Typography>
                </Box>

                {/* Country Scores */}
                <Typography variant="h6" gutterBottom>Country Breakdown</Typography>
                {Object.entries(analysis.country_scores || {}).map(([country, score]) => (
                  <Box key={country} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2">{country}</Typography>
                      <Typography variant="body2">{(score * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={score * 100}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                ))}

                {/* Bias Flags */}
                {analysis.bias_flags && analysis.bias_flags.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      <WarningIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
                      Potential Issues
                    </Typography>
                    {analysis.bias_flags.map((flag, index) => (
                      <Chip
                        key={index}
                        label={`${flag.type}: ${flag.description}`}
                        color="warning"
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                )}

                {/* Recommendations */}
                {analysis.recommendations && analysis.recommendations.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>Recommendations</Typography>
                    {analysis.recommendations.map((rec, index) => (
                      <Alert key={index} severity="info" sx={{ mb: 1 }}>
                        <strong>{rec.country}:</strong> {rec.message}
                      </Alert>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Additional Analysis Components */}
        {analysis && (
          <>
            <Grid item xs={12}>
              <BiasAnalyzer analysis={analysis} />
            </Grid>
            <Grid item xs={12}>
              <CulturalMap analysis={analysis} />
            </Grid>
          </>
        )}
      </Grid>
    </Container>
  );
};

export default Dashboard;
