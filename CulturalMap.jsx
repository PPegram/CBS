"""
Cultural Map Component
Visualization of cultural dimensions and alignment scores
"""
import React from 'react';
import {
  Card, CardContent, Typography, Box, Grid, Paper,
  LinearProgress, Chip, Tooltip
} from '@mui/material';
import {
  Public as PublicIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const CulturalMap = ({ analysis }) => {
  const dimensions = [
    { key: 'power_distance', label: 'Power Distance', description: 'Acceptance of hierarchical order' },
    { key: 'individualism', label: 'Individualism', description: 'Individual vs. collective orientation' },
    { key: 'masculinity', label: 'Masculinity', description: 'Achievement vs. relationship orientation' },
    { key: 'uncertainty_avoidance', label: 'Uncertainty Avoidance', description: 'Tolerance for ambiguity' },
    { key: 'long_term_orientation', label: 'Long-term Orientation', description: 'Focus on future vs. present' },
    { key: 'indulgence', label: 'Indulgence', description: 'Freedom vs. control of desires' }
  ];

  const getAlignmentColor = (score) => {
    if (score >= 0.8) return '#4caf50'; // Green
    if (score >= 0.6) return '#ff9800'; // Orange  
    return '#f44336'; // Red
  };

  const getProgressColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  if (!analysis.country_scores) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            🗺️ Cultural Alignment Map
          </Typography>
          <Typography variant="body1" color="text.secondary">
            No cultural analysis data available.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          🗺️ Cultural Alignment Map
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Visual representation of how well your campaign aligns with each target country's cultural values.
        </Typography>

        {/* Overall Metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <PublicIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h6">Target Markets</Typography>
              <Typography variant="h3" color="primary">
                {Object.keys(analysis.country_scores).length}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <TrendingUpIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h6">Avg. Alignment</Typography>
              <Typography variant="h3" color="success.main">
                {(analysis.overall_score * 100).toFixed(0)}%
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <AssessmentIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h6">Risk Level</Typography>
              <Chip 
                label={analysis.risk_level?.toUpperCase() || 'UNKNOWN'}
                color={analysis.risk_level === 'low' ? 'success' : analysis.risk_level === 'medium' ? 'warning' : 'error'}
                sx={{ fontSize: '1rem', height: 32 }}
              />
            </Paper>
          </Grid>
        </Grid>

        {/* Country-Specific Analysis */}
        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Country-Specific Cultural Alignment
        </Typography>

        <Grid container spacing={2}>
          {Object.entries(analysis.country_scores).map(([country, score]) => (
            <Grid item xs={12} sm={6} md={4} key={country}>
              <Paper sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h6">{country}</Typography>
                  <Chip 
                    label={`${(score * 100).toFixed(1)}%`}
                    color={getProgressColor(score)}
                    size="small"
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={score * 100}
                  color={getProgressColor(score)}
                  sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {score >= 0.8 ? 'Excellent alignment' : 
                   score >= 0.6 ? 'Good alignment' : 'Needs improvement'}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Cultural Dimensions Analysis */}
        {analysis.dimension_analysis && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Hofstede Cultural Dimensions Analysis
            </Typography>

            {Object.entries(analysis.dimension_analysis).map(([country, countryDimensions]) => (
              <Paper key={country} sx={{ p: 3, mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {country} - Cultural Dimensions
                </Typography>

                <Grid container spacing={2}>
                  {dimensions.map((dimension) => {
                    const score = countryDimensions[dimension.key];
                    if (score === undefined) return null;

                    return (
                      <Grid item xs={12} md={6} key={dimension.key}>
                        <Tooltip title={dimension.description}>
                          <Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2" fontWeight="medium">
                                {dimension.label}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {(score * 100).toFixed(1)}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={score * 100}
                              color={getProgressColor(score)}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                          </Box>
                        </Tooltip>
                      </Grid>
                    );
                  })}
                </Grid>
              </Paper>
            ))}
          </Box>
        )}

        {/* Confidence Intervals */}
        {analysis.confidence && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Confidence Intervals
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              95% confidence intervals showing the range of likely alignment scores.
            </Typography>

            <Grid container spacing={2}>
              {Object.entries(analysis.confidence).map(([country, confidence]) => (
                <Grid item xs={12} sm={6} key={country}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body1" fontWeight="medium" gutterBottom>
                      {country}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Lower Bound:</Typography>
                      <Typography variant="body2">{(confidence.lower_bound * 100).toFixed(1)}%</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Upper Bound:</Typography>
                      <Typography variant="body2">{(confidence.upper_bound * 100).toFixed(1)}%</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Data Quality:</Typography>
                      <Chip 
                        label={`${(confidence.data_quality * 100).toFixed(0)}%`}
                        size="small"
                        color={confidence.data_quality >= 0.8 ? 'success' : 'warning'}
                      />
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CulturalMap;
