import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Tabs,
  Tab,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import { RiskProvider } from './contexts/RiskContext';
import MapComponent from './components/Map/MapComponent';
import RiskForm from './components/RiskForm/RiskForm';
import RiskDisplay from './components/RiskForm/RiskDisplay';
import RiskCharts from './components/Charts/RiskCharts';
import LocationSearch from './components/LocationSearch/LocationSearch';
import DataExport from './components/DataExport/DataExport';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      {...other}
      style={{ height: value === index ? '100%' : 0 }}
    >
      {value === index && <Box sx={{ height: '100%' }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [resultsTab, setResultsTab] = React.useState(0);
  const [showHeatmap, setShowHeatmap] = React.useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleResultsTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setResultsTab(newValue);
    setShowHeatmap(newValue === 1); // Show heatmap when Charts tab is active
  };

  return (
    <RiskProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {/* Header */}
        <AppBar position="static" elevation={1}>
          <Toolbar>
            <TravelExploreIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Geo Risk Simulation Platform
            </Typography>
            <DataExport />
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth={false} sx={{ flex: 1, py: 3, overflow: 'hidden' }}>
          <Grid container spacing={2} sx={{ height: '100%' }}>
            {/* Left Panel - Map */}
            <Grid item xs={12} md={6} sx={{ height: isMobile ? '50%' : '100%' }}>
              <Paper elevation={3} sx={{ height: '100%', overflow: 'hidden' }}>
                <Box sx={{ p: 2, pb: 1 }}>
                  <LocationSearch />
                </Box>
                <Box sx={{ height: 'calc(100% - 80px)' }}>
                  <MapComponent showHeatmap={showHeatmap} />
                </Box>
              </Paper>
            </Grid>

            {/* Right Panel - Split into Input and Results */}
            <Grid item xs={12} md={6} sx={{ height: isMobile ? '50%' : '100%' }}>
              <Grid container spacing={2} sx={{ height: '100%' }}>
                {/* Input Form */}
                <Grid item xs={12} md={12} lg={5} sx={{ height: isMobile ? 'auto' : '100%' }}>
                  <RiskForm />
                </Grid>

                {/* Results Area */}
                <Grid item xs={12} md={12} lg={7} sx={{ height: isMobile ? 'auto' : '100%' }}>
                  <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                      <Tabs
                        value={resultsTab}
                        onChange={handleResultsTabChange}
                        aria-label="results tabs"
                        variant="fullWidth"
                      >
                        <Tab label="Results" />
                        <Tab label="Charts" />
                      </Tabs>
                    </Box>
                    <Box sx={{ flex: 1, overflow: 'hidden' }}>
                      <TabPanel value={resultsTab} index={0}>
                        <RiskDisplay />
                      </TabPanel>
                      <TabPanel value={resultsTab} index={1}>
                        <RiskCharts />
                      </TabPanel>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </RiskProvider>
  );
}

export default App;
