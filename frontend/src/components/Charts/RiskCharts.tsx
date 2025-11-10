import React, { useMemo } from 'react';
import { Box, Paper, Typography, Grid } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { Bar, Pie, Radar } from 'react-chartjs-2';
import { useRiskContext } from '../../contexts/RiskContext';
import { getRiskColor } from '../../utils/helpers';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
);

const RiskCharts: React.FC = () => {
  const { assessmentResult } = useRiskContext();

  const barChartData = useMemo(() => {
    if (!assessmentResult) return null;

    const labels = assessmentResult.assessments.map((a) => a.hazard_type);
    const scores = assessmentResult.assessments.map((a) => a.risk_score);
    const colors = assessmentResult.assessments.map((a) => getRiskColor(a.risk_level));

    return {
      labels: labels.map((l) => l.charAt(0).toUpperCase() + l.slice(1)),
      datasets: [
        {
          label: 'Risk Score',
          data: scores,
          backgroundColor: colors,
          borderColor: colors.map((c) => c),
          borderWidth: 1,
        },
      ],
    };
  }, [assessmentResult]);

  const pieChartData = useMemo(() => {
    if (!assessmentResult) return null;

    const labels = assessmentResult.assessments.map((a) => a.hazard_type);
    const scores = assessmentResult.assessments.map((a) => a.risk_score);
    const colors = assessmentResult.assessments.map((a) => getRiskColor(a.risk_level));

    return {
      labels: labels.map((l) => l.charAt(0).toUpperCase() + l.slice(1)),
      datasets: [
        {
          label: 'Risk Distribution',
          data: scores,
          backgroundColor: colors,
          borderColor: '#fff',
          borderWidth: 2,
        },
      ],
    };
  }, [assessmentResult]);

  const radarChartData = useMemo(() => {
    if (!assessmentResult || assessmentResult.assessments.length === 0) return null;

    // Aggregate contributing factors across all hazards
    const factorsMap = new Map<string, number[]>();

    assessmentResult.assessments.forEach((assessment) => {
      Object.entries(assessment.contributing_factors).forEach(([factor, value]) => {
        if (!factorsMap.has(factor)) {
          factorsMap.set(factor, []);
        }
        factorsMap.get(factor)!.push(value as number);
      });
    });

    const labels = Array.from(factorsMap.keys()).map((f) =>
      f.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
    );
    const data = Array.from(factorsMap.values()).map(
      (values) => values.reduce((a, b) => a + b, 0) / values.length
    );

    return {
      labels,
      datasets: [
        {
          label: 'Contributing Factors',
          data,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
        },
      ],
    };
  }, [assessmentResult]);

  if (!assessmentResult) {
    return (
      <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" color="text.secondary" align="center">
          No data available for charts
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Complete a risk assessment to view visualizations
        </Typography>
      </Paper>
    );
  }

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Risk Scores by Hazard Type',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Risk Score',
        },
      },
    },
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Risk Distribution',
      },
    },
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Contributing Factors Analysis',
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
      },
    },
  };

  return (
    <Paper elevation={3} sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Risk Visualization
      </Typography>

      <Grid container spacing={3}>
        {/* Bar Chart */}
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            {barChartData && <Bar data={barChartData} options={barOptions} />}
          </Box>
        </Grid>

        {/* Pie Chart */}
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            {pieChartData && <Pie data={pieChartData} options={pieOptions} />}
          </Box>
        </Grid>

        {/* Radar Chart */}
        {radarChartData && (
          <Grid item xs={12}>
            <Box sx={{ height: 300 }}>
              <Radar data={radarChartData} options={radarOptions} />
            </Box>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
};

export default RiskCharts;
