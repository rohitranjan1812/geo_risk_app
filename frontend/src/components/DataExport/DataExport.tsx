import React, { useState } from 'react';
import {
  Box,
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Snackbar,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import TableChartIcon from '@mui/icons-material/TableChart';
import CodeIcon from '@mui/icons-material/Code';
import { useRiskContext } from '../../contexts/RiskContext';
import { exportToCSV, exportToJSON } from '../../utils/helpers';

const DataExport: React.FC = () => {
  const { assessmentResult } = useRiskContext();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notification, setNotification] = useState<{ open: boolean; message: string }>({
    open: false,
    message: '',
  });

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleExportCSV = () => {
    if (!assessmentResult) {
      setNotification({ open: true, message: 'No data available to export' });
      handleClose();
      return;
    }

    try {
      // Flatten assessment data for CSV
      const csvData = assessmentResult.assessments.map((assessment) => ({
        location_name: assessmentResult.location.name,
        latitude: assessmentResult.location.latitude,
        longitude: assessmentResult.location.longitude,
        hazard_type: assessment.hazard_type,
        risk_score: assessment.risk_score,
        risk_level: assessment.risk_level,
        confidence: assessment.confidence,
        ...assessment.contributing_factors,
        recommendations: assessment.mitigation_recommendations.join('; '),
      }));

      const timestamp = new Date().toISOString().split('T')[0];
      exportToCSV(csvData, `risk_assessment_${timestamp}`);

      setNotification({ open: true, message: 'CSV exported successfully' });
    } catch (error) {
      console.error('Export error:', error);
      setNotification({ open: true, message: 'Failed to export CSV' });
    }

    handleClose();
  };

  const handleExportJSON = () => {
    if (!assessmentResult) {
      setNotification({ open: true, message: 'No data available to export' });
      handleClose();
      return;
    }

    try {
      const timestamp = new Date().toISOString().split('T')[0];
      exportToJSON(assessmentResult, `risk_assessment_${timestamp}`);

      setNotification({ open: true, message: 'JSON exported successfully' });
    } catch (error) {
      console.error('Export error:', error);
      setNotification({ open: true, message: 'Failed to export JSON' });
    }

    handleClose();
  };

  return (
    <Box>
      <Button
        variant="outlined"
        startIcon={<DownloadIcon />}
        onClick={handleClick}
        disabled={!assessmentResult}
      >
        Export Data
      </Button>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        <MenuItem onClick={handleExportCSV}>
          <ListItemIcon>
            <TableChartIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export as CSV</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleExportJSON}>
          <ListItemIcon>
            <CodeIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export as JSON</ListItemText>
        </MenuItem>
      </Menu>

      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setNotification({ ...notification, open: false })}
          severity="success"
          variant="filled"
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DataExport;
