import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { useRiskContext } from '../../contexts/RiskContext';
import { HazardCategory, RiskAssessmentRequest } from '../../types';
import apiService from '../../services/api';
import { getHazardIcon } from '../../utils/helpers';

const RiskForm: React.FC = () => {
  const {
    selectedLocation,
    selectedHazards,
    setSelectedHazards,
    customFactors,
    setCustomFactors,
    setAssessmentResult,
    isLoading,
    setIsLoading,
    error,
    setError,
  } = useRiskContext();

  const [populationDensity, setPopulationDensity] = useState<number>(1000);
  const [buildingCodeRating, setBuildingCodeRating] = useState<number>(5);
  const [infrastructureQuality, setInfrastructureQuality] = useState<number>(5);

  useEffect(() => {
    if (selectedLocation) {
      setPopulationDensity(selectedLocation.population_density || 1000);
      setBuildingCodeRating(selectedLocation.building_code_rating || 5);
      setInfrastructureQuality(selectedLocation.infrastructure_quality || 5);
    }
  }, [selectedLocation]);

  const handleHazardToggle = (hazard: HazardCategory) => {
    setSelectedHazards((prev) =>
      prev.includes(hazard) ? prev.filter((h) => h !== hazard) : [...prev, hazard]
    );
  };

  const handleAssessRisk = async () => {
    if (!selectedLocation && selectedHazards.length === 0) {
      setError('Please select a location and at least one hazard type');
      return;
    }

    if (selectedHazards.length === 0) {
      setError('Please select at least one hazard type');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const request: RiskAssessmentRequest = {
        location_id: selectedLocation?.id,
        hazard_types: selectedHazards,
        custom_factors: {
          population_density: populationDensity,
          building_code_rating: buildingCodeRating,
          infrastructure_quality: infrastructureQuality,
        },
      };

      const result = await apiService.assessRisk(request);
      setAssessmentResult(result);
      setCustomFactors({
        population_density: populationDensity,
        building_code_rating: buildingCodeRating,
        infrastructure_quality: infrastructureQuality,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to assess risk. Please try again.');
      console.error('Risk assessment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const allHazards = Object.values(HazardCategory);

  return (
    <Paper elevation={3} sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Risk Assessment Parameters
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Location Info */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Selected Location
        </Typography>
        {selectedLocation ? (
          <Box>
            <Typography variant="body1" fontWeight="bold">
              {selectedLocation.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Lat: {selectedLocation.latitude.toFixed(4)}, Lng:{' '}
              {selectedLocation.longitude.toFixed(4)}
            </Typography>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Click on the map to select a location
          </Typography>
        )}
      </Box>

      {/* Hazard Selection */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Hazard Types
        </Typography>
        <FormGroup>
          {allHazards.map((hazard) => (
            <FormControlLabel
              key={hazard}
              control={
                <Checkbox
                  checked={selectedHazards.includes(hazard)}
                  onChange={() => handleHazardToggle(hazard)}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>{getHazardIcon(hazard)}</span>
                  <span style={{ textTransform: 'capitalize' }}>{hazard}</span>
                </Box>
              }
            />
          ))}
        </FormGroup>
      </Box>

      {/* Risk Factors */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Risk Factors
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="body2" gutterBottom>
              Population Density: {populationDensity.toFixed(0)} per sq km
            </Typography>
            <Slider
              value={populationDensity}
              onChange={(_, value) => setPopulationDensity(value as number)}
              min={0}
              max={20000}
              step={100}
              valueLabelDisplay="auto"
              marks={[
                { value: 0, label: '0' },
                { value: 10000, label: '10K' },
                { value: 20000, label: '20K' },
              ]}
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body2" gutterBottom>
              Building Code Rating: {buildingCodeRating.toFixed(1)}/10
            </Typography>
            <Slider
              value={buildingCodeRating}
              onChange={(_, value) => setBuildingCodeRating(value as number)}
              min={0}
              max={10}
              step={0.1}
              valueLabelDisplay="auto"
              marks={[
                { value: 0, label: '0' },
                { value: 5, label: '5' },
                { value: 10, label: '10' },
              ]}
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body2" gutterBottom>
              Infrastructure Quality: {infrastructureQuality.toFixed(1)}/10
            </Typography>
            <Slider
              value={infrastructureQuality}
              onChange={(_, value) => setInfrastructureQuality(value as number)}
              min={0}
              max={10}
              step={0.1}
              valueLabelDisplay="auto"
              marks={[
                { value: 0, label: '0' },
                { value: 5, label: '5' },
                { value: 10, label: '10' },
              ]}
            />
          </Grid>
        </Grid>
      </Box>

      {/* Assess Button */}
      <Button
        variant="contained"
        color="primary"
        fullWidth
        size="large"
        onClick={handleAssessRisk}
        disabled={isLoading || selectedHazards.length === 0}
        startIcon={isLoading ? <CircularProgress size={20} /> : <AssessmentIcon />}
      >
        {isLoading ? 'Assessing...' : 'Assess Risk'}
      </Button>
    </Paper>
  );
};

export default RiskForm;
