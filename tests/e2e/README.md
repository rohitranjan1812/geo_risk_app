# E2E Test Suite - Geo Risk Application

Comprehensive end-to-end testing using Playwright for the Geo Risk Assessment application.

## Overview

This E2E test suite validates complete user workflows across multiple browsers and devices, ensuring the application works correctly from frontend through API to database and back.

## Test Coverage

### 1. User Journey Tests (`01-user-journey.spec.ts`)
- **Full workflow**: Load app → Search location → Select on map → Choose hazards → Input risk factors → View results → Export data
- **Map interaction workflow**: Click map → Input custom data → Assess risk
- **Multiple location comparison**: Sequential assessments
- **Quick assessment**: Default values workflow
- **Mobile device workflow**: Touch interactions

**Key Validations**:
- App loads successfully
- Map renders and is interactive
- Search functionality works
- Location selection (click or search)
- Hazard selection (single and multiple)
- Risk factor input validation
- Results display correctly
- Export generates valid files (JSON/CSV)

### 2. Multi-Hazard Scenarios (`02-multi-hazard.spec.ts`)
- **Earthquake Zone Assessment**: Earthquake + Fire combination
- **Coastal Flood Risk**: Flood + Storm interaction
- **Wildfire Prone Area**: Fire + Earthquake + Storm
- **All Hazards Critical**: Maximum risk scenario
- **Relative risk comparison**: All 4 hazards simultaneously
- **Factor impact analysis**: Infrastructure quality comparison

**Key Validations**:
- Multiple hazards assessed simultaneously
- Risk scores meet minimum thresholds
- Risk levels (LOW/MODERATE/HIGH/CRITICAL) assigned correctly
- Hazard interactions reflected in scores
- Risk factor changes impact results
- Recommendations generated for each hazard

### 3. Error Handling Tests (`03-error-handling.spec.ts`)
- **API Failures**: Server errors (404, 500, 422), timeouts
- **Network Errors**: Disconnection, retry mechanisms
- **Invalid Inputs**: Boundary validation, required fields
- **Recovery & Resilience**: Error dismissal, partial data handling

**Key Validations**:
- User-friendly error messages displayed
- Errors can be dismissed
- Application remains functional after errors
- Validation prevents invalid submissions

### 4. Cross-Browser Compatibility (`04-cross-browser.spec.ts`)
- **Desktop Browsers**: Chrome, Firefox, Safari
- **Mobile Devices**: iPhone, iPad, Android
- **Responsive Design**: 7 breakpoints tested
- **Quality Checks**: No console errors, accessibility features

**Key Validations**:
- All browsers render correctly
- Touch and mouse interactions work
- Responsive layouts adapt
- No JavaScript errors

### 5. Performance Tests (`05-performance.spec.ts`)
- **Page Load**: Initial load < 3s, Map render < 2s
- **Interactions**: Assessment < 3s, Multi-hazard < 5s
- **Data Processing**: Large datasets, memory stability
- **Web Vitals**: LCP < 2.5s, CLS < 0.1

## Setup

```bash
cd tests/e2e
./setup.sh
```

## Running Tests

```bash
# Run all tests
npm test

# Browser visible
npm run test:headed

# Debug mode
npm run test:debug

# Specific browser
npm run test:chromium

# Interactive UI
npm run test:ui
```

## Viewing Results

```bash
npm run test:report
```

## Success Criteria

✅ All E2E scenarios pass  
✅ Complete user workflows execute without errors  
✅ Data flows correctly through full stack  
✅ Export functionality produces valid files  
✅ Error states handled gracefully  
✅ Performance targets met  
✅ Cross-browser compatibility verified

## Test Statistics

- **Total Tests**: 60+
- **Browsers**: Chrome, Firefox, Safari, Mobile
- **Devices**: 7 responsive breakpoints
- **Scenarios**: 15+ user workflows
- **Error Conditions**: 20+ scenarios
