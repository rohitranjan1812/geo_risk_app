import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Grid,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { useRiskContext } from '../../contexts/RiskContext';
import { getRiskColor, getHazardIcon, formatNumber } from '../../utils/helpers';
import { RiskLevel } from '../../types';

const RiskDisplay: React.FC = () => {
  const { assessmentResult } = useRiskContext();

  if (!assessmentResult) {
    return (
      <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" color="text.secondary" align="center">
          No risk assessment available
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Select a location and hazard types, then click "Assess Risk"
        </Typography>
      </Paper>
    );
  }

  const { location, assessments, overall_risk_score } = assessmentResult;

  const getOverallRiskLevel = (score: number): RiskLevel => {
    if (score < 30) return RiskLevel.LOW;
    if (score < 50) return RiskLevel.MODERATE;
    if (score < 70) return RiskLevel.HIGH;
    return RiskLevel.CRITICAL;
  };

  const overallRiskLevel = getOverallRiskLevel(overall_risk_score);

  return (
    <Paper elevation={3} sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Risk Assessment Results
      </Typography>

      {/* Location Info */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Location
        </Typography>
        <Typography variant="h6">{location.name}</Typography>
        <Typography variant="body2" color="text.secondary">
          Lat: {location.latitude.toFixed(4)}, Lng: {location.longitude.toFixed(4)}
        </Typography>
      </Box>

      {/* Overall Risk Score */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle1">Overall Risk Score</Typography>
          <Chip
            label={overallRiskLevel}
            sx={{
              backgroundColor: getRiskColor(overallRiskLevel),
              color: 'white',
              fontWeight: 'bold',
            }}
          />
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LinearProgress
            variant="determinate"
            value={overall_risk_score}
            sx={{
              flex: 1,
              height: 10,
              borderRadius: 5,
              backgroundColor: '#e0e0e0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: getRiskColor(overallRiskLevel),
              },
            }}
          />
          <Typography variant="h6" fontWeight="bold">
            {formatNumber(overall_risk_score, 1)}
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Individual Hazard Assessments */}
      <Typography variant="h6" gutterBottom>
        Hazard-Specific Risks
      </Typography>

      <Grid container spacing={2}>
        {assessments.map((assessment, index) => (
          <Grid item xs={12} key={index}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="h6">
                    {getHazardIcon(assessment.hazard_type)}
                  </Typography>
                  <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                    {assessment.hazard_type}
                  </Typography>
                </Box>
                <Chip
                  label={assessment.risk_level}
                  size="small"
                  sx={{
                    backgroundColor: getRiskColor(assessment.risk_level),
                    color: 'white',
                  }}
                />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <LinearProgress
                  variant="determinate"
                  value={assessment.risk_score}
                  sx={{
                    flex: 1,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: '#e0e0e0',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getRiskColor(assessment.risk_level),
                    },
                  }}
                />
                <Typography variant="body1" fontWeight="bold">
                  {formatNumber(assessment.risk_score, 1)}
                </Typography>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Confidence: {formatNumber(assessment.confidence * 100, 0)}%
              </Typography>

              {/* Contributing Factors */}
              {Object.keys(assessment.contributing_factors).length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Contributing Factors:
                  </Typography>
                  <Grid container spacing={1} sx={{ mt: 0.5 }}>
                    {Object.entries(assessment.contributing_factors).map(([factor, value]) => (
                      <Grid item xs={6} key={factor}>
                        <Typography variant="caption">
                          {factor.replace(/_/g, ' ')}: {formatNumber(value as number, 1)}
                        </Typography>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Mitigation Recommendations */}
              {assessment.mitigation_recommendations.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" fontWeight="bold" color="primary">
                    Recommendations:
                  </Typography>
                  <List dense sx={{ py: 0 }}>
                    {assessment.mitigation_recommendations.map((rec, idx) => (
                      <ListItem key={idx} sx={{ py: 0, px: 0 }}>
                        <ListItemText
                          primary={rec}
                          primaryTypographyProps={{ variant: 'caption' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default RiskDisplay;
