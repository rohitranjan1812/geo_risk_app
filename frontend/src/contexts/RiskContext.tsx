import React, { createContext, useContext, useState, ReactNode } from 'react';
import {
  Location,
  RiskAssessmentResponse,
  HazardCategory,
  RiskFactors,
  Hazard,
} from '../types';

interface RiskContextType {
  selectedLocation: Location | null;
  setSelectedLocation: (location: Location | null) => void;
  selectedHazards: HazardCategory[];
  setSelectedHazards: (hazards: HazardCategory[]) => void;
  customFactors: RiskFactors;
  setCustomFactors: (factors: RiskFactors) => void;
  assessmentResult: RiskAssessmentResponse | null;
  setAssessmentResult: (result: RiskAssessmentResponse | null) => void;
  availableHazards: Hazard[];
  setAvailableHazards: (hazards: Hazard[]) => void;
  allLocations: Location[];
  setAllLocations: (locations: Location[]) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const RiskContext = createContext<RiskContextType | undefined>(undefined);

export const useRiskContext = (): RiskContextType => {
  const context = useContext(RiskContext);
  if (!context) {
    throw new Error('useRiskContext must be used within RiskProvider');
  }
  return context;
};

interface RiskProviderProps {
  children: ReactNode;
}

export const RiskProvider: React.FC<RiskProviderProps> = ({ children }) => {
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [selectedHazards, setSelectedHazards] = useState<HazardCategory[]>([]);
  const [customFactors, setCustomFactors] = useState<RiskFactors>({});
  const [assessmentResult, setAssessmentResult] = useState<RiskAssessmentResponse | null>(null);
  const [availableHazards, setAvailableHazards] = useState<Hazard[]>([]);
  const [allLocations, setAllLocations] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const value: RiskContextType = {
    selectedLocation,
    setSelectedLocation,
    selectedHazards,
    setSelectedHazards,
    customFactors,
    setCustomFactors,
    assessmentResult,
    setAssessmentResult,
    availableHazards,
    setAvailableHazards,
    allLocations,
    setAllLocations,
    isLoading,
    setIsLoading,
    error,
    setError,
  };

  return <RiskContext.Provider value={value}>{children}</RiskContext.Provider>;
};
