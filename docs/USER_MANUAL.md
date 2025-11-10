# Geo Risk Assessment Platform - User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Features & Workflows](#features--workflows)
5. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Introduction

### What is Geo Risk?

Geo Risk is a comprehensive natural disaster risk assessment platform that helps you:

- **Evaluate** risk levels for specific geographic locations
- **Analyze** multiple hazard types simultaneously (earthquakes, floods, fires, storms)
- **Visualize** risk data on interactive maps with heat mapping
- **Export** assessment results for reporting and analysis
- **Compare** risk across different locations

### Who Should Use This?

- **Emergency Management:** Disaster preparedness planning
- **Insurance:** Risk underwriting and premium calculation
- **Real Estate:** Property risk assessment
- **Government:** Urban planning and zoning decisions
- **Research:** Academic study of natural hazards

### Key Capabilities

✅ **Multi-Hazard Assessment** - Evaluate up to 4 hazard types simultaneously  
✅ **Interactive Mapping** - Visual risk exploration with Leaflet/MapBox  
✅ **Real-Time Scoring** - Instant risk calculation as you input data  
✅ **Heat Map Visualization** - Geographic risk distribution  
✅ **Data Export** - Download results as JSON or CSV  
✅ **Historical Context** - View past disaster events  

---

## Getting Started

### Accessing the Application

**Web Application:**
```
Local Development: http://localhost:3000
Production:        https://georisk.example.com
Docker Deployment: http://localhost
```

**System Requirements:**
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Internet connection for map tiles
- JavaScript enabled
- Minimum screen resolution: 1024x768

### First Time Setup

1. **Open your web browser** and navigate to the application URL
2. **Wait for the application to load** - the map will initialize automatically
3. **No login required** - the application is currently open access
4. **Start exploring** by searching for a location or clicking on the map

---

## User Interface Overview

### Main Interface Components

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Geo Risk Assessment Platform          [Export] [Help]│
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│  Location     │                                             │
│  Search       │                                             │
│  Panel        │          Interactive Map                    │
│               │          with Heat Layer                    │
│               │                                             │
├───────────────┤                                             │
│               │                                             │
│  Risk Factor  │                                             │
│  Inputs       │                                             │
│               │                                             │
├───────────────┴─────────────────────────────────────────────┤
│                 Risk Results Panel                          │
│  [Earthquake: HIGH] [Flood: MODERATE] [Fire: LOW]          │
│  Overall Risk Score: 58.9 - HIGH                           │
└─────────────────────────────────────────────────────────────┘
```

### 1. Location Search Panel

**Purpose:** Find and select geographic locations for assessment

**Components:**
- **Search Bar** - Type city name, address, or coordinates
- **Autocomplete** - Suggested locations as you type
- **Recent Locations** - Quick access to previously searched areas
- **Manual Coordinates** - Enter latitude/longitude directly

**How to Use:**
```
1. Click on the search bar
2. Type location name (e.g., "San Francisco, CA")
3. Select from dropdown suggestions
4. Or click on the map to select a point
```

### 2. Interactive Map

**Purpose:** Visual exploration and location selection

**Features:**
- **Pan & Zoom** - Drag to move, scroll to zoom
- **Click Selection** - Click anywhere to assess that location
- **Heat Map Layer** - Shows risk intensity across regions
- **Markers** - Previous assessment locations
- **Map Controls** - Zoom in/out, reset view, layer toggle

**Map Legend:**
```
Heat Map Colors:
🟢 Green   - Low Risk (0-25)
🟡 Yellow  - Moderate Risk (26-50)
🟠 Orange  - High Risk (51-75)
🔴 Red     - Critical Risk (76-100)
```

**Interaction Tips:**
- **Double-click** to zoom in quickly
- **Right-click** for location details
- **Shift + Drag** to zoom to an area
- **Toggle heat layer** using the layer control button

### 3. Risk Factor Inputs

**Purpose:** Customize assessment parameters

**Input Fields:**

| Factor | Description | Range | Default |
|--------|-------------|-------|---------|
| **Population Density** | People per sq km | 0+ | Current location data |
| **Building Code Rating** | Construction quality | 0-10 | 5.0 |
| **Infrastructure Quality** | Roads, utilities, emergency services | 0-10 | 5.0 |

**Hazard Selection:**
- ☑️ **Earthquake** - Seismic activity risk
- ☑️ **Flood** - Water inundation risk
- ☑️ **Fire** - Wildfire risk
- ☑️ **Storm** - Hurricane/typhoon risk

**How to Adjust:**
```
1. Use sliders to adjust numeric values
2. Check/uncheck hazard types
3. Click "Assess Risk" button
4. Results update in real-time
```

### 4. Risk Results Panel

**Purpose:** Display assessment results and recommendations

**Components:**

**Individual Hazard Cards:**
```
┌──────────────────────────────┐
│ 🌎 EARTHQUAKE                │
│ Risk Score: 72.5             │
│ Level: HIGH ⚠️               │
│ Confidence: 85%              │
│                              │
│ Factors Analysis:            │
│ • Population density: +15.2  │
│ • Building codes: -8.5       │
│ • Infrastructure: -5.0       │
│                              │
│ Recommendations:             │
│ ✓ Strengthen building codes  │
│ ✓ Conduct earthquake drills  │
└──────────────────────────────┘
```

**Overall Risk Summary:**
- **Composite Score** - Average across all hazards
- **Risk Level** - Low/Moderate/High/Critical
- **Trending** - Comparison with regional average

---

## Features & Workflows

### Workflow 1: Quick Location Assessment

**Use Case:** Rapidly assess risk for a single address

**Steps:**

1. **Search for Location**
   ```
   - Type "123 Main St, City, State" in search bar
   - Select from autocomplete suggestions
   ```

2. **Select Hazards**
   ```
   - Check hazard types relevant to your area
   - Default: All 4 hazards selected
   ```

3. **Run Assessment**
   ```
   - Click "Assess Risk" button
   - Wait 2-3 seconds for calculation
   ```

4. **Review Results**
   ```
   - Overall risk score displayed prominently
   - Individual hazard breakdowns shown
   - Recommendations listed
   ```

5. **Export (Optional)**
   ```
   - Click "Export" button
   - Choose JSON or CSV format
   - Save file to computer
   ```

**Expected Time:** 30 seconds

---

### Workflow 2: Multi-Location Comparison

**Use Case:** Compare risk across several potential sites

**Steps:**

1. **Assess First Location**
   ```
   - Search "Location A"
   - Run assessment
   - Note overall risk score
   ```

2. **Assess Second Location**
   ```
   - Search "Location B"
   - Use SAME hazard selections
   - Use SAME risk factor values
   - Run assessment
   ```

3. **Repeat** for additional locations

4. **Compare Results**
   ```
   - View markers on map
   - Compare risk scores side-by-side
   - Identify lowest-risk option
   ```

5. **Export All Results**
   ```
   - Export comprehensive report
   - Include all assessed locations
   ```

**Expected Time:** 2-3 minutes for 3 locations

---

### Workflow 3: Custom Risk Factor Analysis

**Use Case:** Understand impact of building codes or infrastructure

**Steps:**

1. **Baseline Assessment**
   ```
   - Select location
   - Use default risk factors
   - Run assessment
   - Record baseline score: 65.0
   ```

2. **Adjust Single Factor**
   ```
   - Increase building code rating: 5.0 → 9.0
   - Keep other factors constant
   - Run assessment
   - New score: 52.5 (improvement!)
   ```

3. **Test Infrastructure Impact**
   ```
   - Reset building codes to baseline
   - Increase infrastructure quality: 5.0 → 9.0
   - Run assessment
   - New score: 58.0
   ```

4. **Optimize Both**
   ```
   - Set building codes: 9.0
   - Set infrastructure: 9.0
   - Run assessment
   - New score: 45.0 (best case)
   ```

5. **Generate Report**
   ```
   - Document findings
   - Export data
   - Share with stakeholders
   ```

**Expected Time:** 5-10 minutes

---

### Workflow 4: Regional Heat Map Exploration

**Use Case:** Identify high-risk zones in a region

**Steps:**

1. **Navigate to Region**
   ```
   - Search for city or region
   - Zoom out to see broader area
   ```

2. **Enable Heat Map**
   ```
   - Toggle heat map layer ON
   - Select primary hazard type
   ```

3. **Identify Hot Spots**
   ```
   - Look for red/orange zones
   - Note geographic patterns
   - Click on high-risk areas
   ```

4. **Assess Specific Sites**
   ```
   - Click on hot spot
   - Run detailed assessment
   - Review contributing factors
   ```

5. **Document Findings**
   ```
   - Screenshot heat map
   - Export assessed locations
   - Compile regional report
   ```

**Expected Time:** 10-15 minutes

---

### Workflow 5: Export and Reporting

**Use Case:** Generate reports for analysis or compliance

**Export Formats:**

**JSON Export:**
```json
{
  "location": {
    "name": "San Francisco, CA",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "assessments": [
    {
      "hazard_type": "earthquake",
      "risk_score": 72.5,
      "risk_level": "high",
      "recommendations": [...]
    }
  ],
  "overall_risk_score": 58.9,
  "overall_risk_level": "high",
  "assessed_at": "2024-01-01T15:00:00Z"
}
```

**CSV Export:**
```csv
Location,Latitude,Longitude,Hazard,Risk Score,Risk Level,Confidence
"San Francisco, CA",37.7749,-122.4194,earthquake,72.5,high,0.85
"San Francisco, CA",37.7749,-122.4194,fire,45.3,moderate,0.78
```

**Export Options:**
- **Single Assessment** - Current location only
- **Multiple Assessments** - All locations from session
- **Historical Data** - Include past events
- **Full Details** - Complete factors analysis

**How to Export:**
```
1. Click "Export" button in top-right
2. Choose format (JSON or CSV)
3. Select data scope
4. Click "Download"
5. File saves to Downloads folder
```

---

## Frequently Asked Questions (FAQ)

### General Questions

**Q: Do I need to create an account?**  
A: No, the application is currently open access. Future versions may add user accounts for saved assessments.

**Q: How accurate are the risk assessments?**  
A: Risk scores are calculated using validated algorithms and historical data. Confidence levels (0-100%) indicate reliability. Scores >85% confidence are highly reliable.

**Q: Can I use this for official purposes?**  
A: Assessments provide guidance but should not replace professional risk analysis for critical decisions. Consult with certified risk assessors for official evaluations.

**Q: How often is data updated?**  
A: Historical disaster data is updated monthly. Hazard severity parameters are reviewed quarterly.

**Q: Is my data saved?**  
A: Current version does not save data between sessions. Export your results before closing the browser.

### Technical Questions

**Q: Why is the map not loading?**  
A: Check your internet connection. Map tiles require network access. Try refreshing the page.

**Q: Why are search results not appearing?**  
A: Ensure you're connected to the internet. The geocoding service requires network access. Try searching with more specific terms.

**Q: Can I use this on mobile devices?**  
A: Yes! The interface is responsive and works on tablets (iPad, Android) and smartphones. Best experience on tablet-sized screens.

**Q: What browsers are supported?**  
A: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+. Internet Explorer is NOT supported.

**Q: Why is the assessment taking so long?**  
A: Typical assessments complete in 2-3 seconds. If taking longer, check network connection or try with fewer hazard types.

### Assessment Questions

**Q: How is overall risk calculated?**  
A: Overall risk is the weighted average of individual hazard scores. Critical hazards receive higher weight.

**Q: What do the confidence levels mean?**  
A: Confidence indicates data quality:
- **90-100%:** Excellent historical data
- **70-89%:** Good data, reliable assessment
- **50-69%:** Limited data, use caution
- **<50%:** Insufficient data, low confidence

**Q: Can I assess locations outside the US?**  
A: Yes! The system works globally. However, data quality varies by region. US locations have highest confidence.

**Q: Why do two nearby locations have different scores?**  
A: Even small distances can have different risk profiles due to:
- Elevation differences
- Proximity to fault lines, water bodies, forests
- Local building codes and infrastructure
- Historical event patterns

**Q: How should I interpret recommendations?**  
A: Recommendations are prioritized by impact. Top items have greatest risk reduction potential. Consult local experts for implementation guidance.

### Data Export Questions

**Q: What format should I choose?**  
A: 
- **JSON:** For software integration, programming, detailed analysis
- **CSV:** For Excel, spreadsheets, simple tabular data

**Q: Can I export multiple locations at once?**  
A: Yes! The batch export includes all locations assessed in current session.

**Q: How do I open JSON files?**  
A: JSON files can be opened with:
- Text editors (Notepad++, VS Code)
- Programming tools (Python, JavaScript)
- Online viewers (jsonviewer.stack.hu)

**Q: Can I re-import exported data?**  
A: Not in current version. Future updates will support import functionality.

---

## Troubleshooting

### Common Issues

#### Map Not Displaying

**Symptoms:** Blank gray area where map should be

**Solutions:**
1. Check internet connection
2. Refresh the page (Ctrl+R or Cmd+R)
3. Clear browser cache
4. Try a different browser
5. Disable browser extensions (ad blockers)

#### Search Not Working

**Symptoms:** No results when typing in search bar

**Solutions:**
1. Check internet connection (geocoding requires network)
2. Use more specific search terms
   - ❌ "Main St"
   - ✅ "123 Main St, Springfield, IL"
3. Try coordinates: "37.7749, -122.4194"
4. Refresh the page

#### Assessment Fails or Times Out

**Symptoms:** Spinning loader that never completes

**Solutions:**
1. Check network connection
2. Verify backend is running (`/health` endpoint)
3. Reduce number of hazard types
4. Try a different location
5. Refresh the page and try again

#### Heat Map Not Appearing

**Symptoms:** Heat layer toggle on but no color overlay

**Solutions:**
1. Zoom out - heat map requires broader view
2. Ensure sufficient assessment data exists
3. Try toggling layer off and on
4. Refresh the page
5. Check browser console for errors (F12)

#### Export Button Not Working

**Symptoms:** Nothing happens when clicking Export

**Solutions:**
1. Ensure assessment has completed
2. Check browser's pop-up blocker settings
3. Try right-click → "Save link as"
4. Check Downloads folder (may have downloaded silently)
5. Try different export format

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Location not found" | Invalid location ID | Use search to find location first |
| "Network error" | API unreachable | Check internet, verify backend running |
| "Invalid input" | Form validation failed | Check all fields have valid values |
| "Assessment timeout" | Request took too long | Reduce hazard count, try again |
| "Export failed" | Download error | Check disk space, browser permissions |

### Performance Issues

**Symptoms:** Slow response, laggy interface

**Solutions:**
1. **Close other browser tabs** - Free up memory
2. **Disable heat map** - Improves rendering performance
3. **Reduce zoom level** - Less map detail to render
4. **Clear browser cache** - Remove old cached data
5. **Update browser** - Ensure latest version
6. **Restart browser** - Clear memory leaks

### Getting Help

If issues persist:

1. **Check browser console:** Press F12, look for red errors
2. **Take screenshot:** Include error message
3. **Note steps to reproduce:** What did you click?
4. **Contact support:** support@georisk.example.com

Include in your report:
- Browser name and version
- Operating system
- Steps to reproduce
- Screenshot of error
- Network status (online/offline)

---

## Best Practices

### For Accurate Assessments

✅ **Use precise locations** - Exact addresses provide better results than city-level  
✅ **Update risk factors** - Adjust population, building codes to current values  
✅ **Select relevant hazards** - Don't assess flood risk in deserts  
✅ **Check confidence levels** - >80% confidence is ideal  
✅ **Review recommendations** - Context-specific guidance for each hazard  

❌ **Avoid:**
- Assessing very large areas (use specific points)
- Ignoring confidence levels
- Using default values without verification
- Relying solely on overall score (review individual hazards)

### For Multi-Location Comparisons

✅ **Standardize inputs** - Use same risk factors across locations  
✅ **Same hazard types** - Compare apples to apples  
✅ **Document methodology** - Note which factors were adjusted  
✅ **Export all results** - Keep comprehensive records  

### For Reporting

✅ **Include confidence levels** - Show data reliability  
✅ **Provide context** - Explain risk factors used  
✅ **Show trends** - Compare to regional averages  
✅ **List recommendations** - Action items for stakeholders  
✅ **Cite data sources** - Reference historical events  

### For Performance

✅ **Assess one location at a time** - Don't queue multiple requests  
✅ **Disable heat map when not needed** - Improves responsiveness  
✅ **Export periodically** - Don't lose session data  
✅ **Use modern browsers** - Ensure optimal performance  

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl/Cmd + F** | Focus search bar |
| **Escape** | Clear search |
| **Enter** | Run assessment |
| **Ctrl/Cmd + E** | Export data |
| **+** / **-** | Zoom map in/out |
| **Arrow Keys** | Pan map |
| **H** | Toggle heat map |
| **F11** | Full screen mode |

---

## Accessibility

The application supports:

- **Keyboard Navigation** - Full functionality without mouse
- **Screen Readers** - ARIA labels on all interactive elements
- **High Contrast Mode** - Respects OS accessibility settings
- **Zoom Support** - Text scales up to 200%
- **Focus Indicators** - Clear visual focus states

---

## Privacy & Data

**What we collect:**
- Assessment queries (location, hazard types)
- Anonymous usage statistics

**What we DON'T collect:**
- Personal information
- Account credentials (no accounts yet)
- Location tracking beyond explicit searches

**Data retention:**
- Session data cleared on browser close
- Historical disaster data retained indefinitely (public information)

---

## Credits

**Built with:**
- **Frontend:** React, TypeScript, Leaflet, Material-UI
- **Backend:** FastAPI, PostgreSQL, Python
- **Data Sources:** USGS, NOAA, FEMA, OpenStreetMap

**Version:** 1.0.0  
**Last Updated:** 2024-01-01

---

**Need more help?** Contact support@georisk.example.com

