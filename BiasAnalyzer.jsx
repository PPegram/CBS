"""
Bias Analyzer Component
Detailed view of detected biases and cultural concerns
"""
import React, { useState } from 'react';
import {
  Card, CardContent, Typography, Box, Accordion, AccordionSummary,
  AccordionDetails, Chip, Alert, Grid, Paper, List, ListItem,
  ListItemText, Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const BiasAnalyzer = ({ analysis }) => {
  const [expanded, setExpanded] = useState(false);

  const handleChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  const getSeverityColor = (severity) => {
    if (severity >= 8) return 'error';
    if (severity >= 6) return 'warning';
    if (severity >= 4) return 'info';
    return 'success';
  };

  const getSeverityIcon = (severity) => {
    if (severity >= 8) return <ErrorIcon />;
    if (severity >= 6) return <WarningIcon />;
    return <InfoIcon />;
  };

  if (!analysis.bias_flags || analysis.bias_flags.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            🎯 Bias Analysis
          </Typography>
          <Alert severity="success">
            No significant cultural biases detected in your campaign content.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          🎯 Detailed Bias Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Comprehensive analysis of potential cultural biases and sensitivities detected in your campaign.
        </Typography>

        {/* Summary Stats */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="error">
                {analysis.bias_flags.length}
              </Typography>
              <Typography variant="body2">Issues Detected</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main">
                {Math.max(...analysis.bias_flags.map(f => f.severity || 0))}
              </Typography>
              <Typography variant="body2">Max Severity</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="info.main">
                {new Set(analysis.bias_flags.map(f => f.type)).size}
              </Typography>
              <Typography variant="body2">Bias Categories</Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Detailed Bias Flags */}
        {analysis.bias_flags.map((flag, index) => (
          <Accordion 
            key={index}
            expanded={expanded === `panel${index}`}
            onChange={handleChange(`panel${index}`)}
            sx={{ mb: 1 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                {getSeverityIcon(flag.severity || 0)}
                <Typography sx={{ ml: 1, flexGrow: 1 }}>
                  {flag.type?.replace('_', ' ').toUpperCase() || 'Unknown Type'}
                </Typography>
                <Chip 
                  label={`Severity: ${flag.severity || 0}/10`}
                  color={getSeverityColor(flag.severity || 0)}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <Typography variant="body1" paragraph>
                  <strong>Description:</strong> {flag.description || 'No description available'}
                </Typography>

                {flag.matches && flag.matches.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Detected Patterns:</strong>
                    </Typography>
                    <List dense>
                      {flag.matches.map((match, matchIndex) => (
                        <ListItem key={matchIndex}>
                          <ListItemText 
                            primary={`"${match}"`}
                            primaryTypographyProps={{ 
                              fontFamily: 'monospace',
                              backgroundColor: '#f5f5f5',
                              padding: '4px 8px',
                              borderRadius: '4px',
                              display: 'inline-block'
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {flag.cultural_context && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <strong>Cultural Context:</strong> {flag.cultural_context}
                  </Alert>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}

        {/* Cultural Insights */}
        {analysis.cultural_insights && Object.keys(analysis.cultural_insights).length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Cultural Insights by Country
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {Object.entries(analysis.cultural_insights).map(([country, insights]) => (
              <Accordion key={country} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="body1">
                    {country} - Cultural Analysis
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {Object.entries(insights).map(([key, value]) => (
                      <Grid item xs={12} key={key}>
                        <Typography variant="body2" color="text.secondary">
                          <strong>{key.replace('_', ' ').toUpperCase()}:</strong>
                        </Typography>
                        <Typography variant="body1" sx={{ ml: 2 }}>
                          {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                        </Typography>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default BiasAnalyzer;
