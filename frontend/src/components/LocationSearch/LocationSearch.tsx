import React, { useState, useEffect, useCallback } from 'react';
import { Autocomplete, TextField, Box, Typography, CircularProgress } from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { useRiskContext } from '../../contexts/RiskContext';
import { Location } from '../../types';
import apiService from '../../services/api';
import { debounce } from '../../utils/helpers';

const LocationSearch: React.FC = () => {
  const { selectedLocation, setSelectedLocation, allLocations, setAllLocations } = useRiskContext();
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load all locations on mount
    const loadLocations = async () => {
      try {
        const locations = await apiService.getLocations();
        setAllLocations(locations);
        setOptions(locations);
      } catch (error) {
        console.error('Failed to load locations:', error);
      }
    };
    loadLocations();
  }, [setAllLocations]);

  const searchLocations = useCallback(
    debounce(async (query: string) => {
      if (!query || query.length < 2) {
        setOptions(allLocations);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const filtered = allLocations.filter(
          (loc) =>
            loc.name.toLowerCase().includes(query.toLowerCase()) ||
            loc.extra_data?.state?.toLowerCase().includes(query.toLowerCase()) ||
            loc.extra_data?.country?.toLowerCase().includes(query.toLowerCase())
        );
        setOptions(filtered);
      } catch (error) {
        console.error('Search error:', error);
        setOptions(allLocations);
      } finally {
        setLoading(false);
      }
    }, 300),
    [allLocations]
  );

  useEffect(() => {
    searchLocations(inputValue);
  }, [inputValue, searchLocations]);

  return (
    <Autocomplete
      value={selectedLocation}
      onChange={(_, newValue) => {
        setSelectedLocation(newValue);
      }}
      inputValue={inputValue}
      onInputChange={(_, newInputValue) => {
        setInputValue(newInputValue);
      }}
      options={options}
      getOptionLabel={(option) => option.name}
      loading={loading}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Search Location"
          placeholder="Enter city name..."
          InputProps={{
            ...params.InputProps,
            startAdornment: <LocationOnIcon sx={{ mr: 1, color: 'action.active' }} />,
            endAdornment: (
              <>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      renderOption={(props, option) => (
        <Box component="li" {...props}>
          <Box>
            <Typography variant="body1">{option.name}</Typography>
            <Typography variant="caption" color="text.secondary">
              Lat: {option.latitude.toFixed(4)}, Lng: {option.longitude.toFixed(4)}
              {option.extra_data?.state && ` • ${option.extra_data.state}`}
              {option.extra_data?.country && ` • ${option.extra_data.country}`}
            </Typography>
          </Box>
        </Box>
      )}
      isOptionEqualToValue={(option, value) => option.id === value.id}
      noOptionsText="No locations found"
      fullWidth
    />
  );
};

export default LocationSearch;
