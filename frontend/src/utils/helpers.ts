import { RiskLevel, HazardCategory } from '../types';

export const getRiskColor = (riskLevel: RiskLevel): string => {
  switch (riskLevel) {
    case RiskLevel.LOW:
      return '#4caf50'; // Green
    case RiskLevel.MODERATE:
      return '#ff9800'; // Orange
    case RiskLevel.HIGH:
      return '#f44336'; // Red
    case RiskLevel.CRITICAL:
      return '#9c27b0'; // Purple
    default:
      return '#9e9e9e'; // Grey
  }
};

export const getRiskColorFromScore = (score: number): string => {
  if (score < 30) return '#4caf50';
  if (score < 50) return '#ff9800';
  if (score < 70) return '#f44336';
  return '#9c27b0';
};

export const getHazardIcon = (category: HazardCategory): string => {
  switch (category) {
    case HazardCategory.EARTHQUAKE:
      return '🌍';
    case HazardCategory.FLOOD:
      return '🌊';
    case HazardCategory.FIRE:
      return '🔥';
    case HazardCategory.STORM:
      return '⛈️';
    default:
      return '⚠️';
  }
};

export const formatNumber = (num: number, decimals: number = 2): string => {
  return num.toFixed(decimals);
};

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const exportToCSV = (data: any[], filename: string): void => {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]).join(',');
  const rows = data.map((item) =>
    Object.values(item)
      .map((value) => {
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value;
      })
      .join(',')
  );

  const csv = [headers, ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
};

export const exportToJSON = (data: any, filename: string): void => {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.json`;
  a.click();
  window.URL.revokeObjectURL(url);
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};
