import React, { createContext, useContext, useState, ReactNode } from 'react';
import { RecommendationFilters } from '../types/recommendation';

interface AppContextType {
  filters: RecommendationFilters;
  setFilters: React.Dispatch<React.SetStateAction<RecommendationFilters>>;
  updateFilter: (key: keyof RecommendationFilters, value: any) => void;
  clearFilters: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [filters, setFilters] = useState<RecommendationFilters>({});

  const updateFilter = (key: keyof RecommendationFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  return (
    <AppContext.Provider value={{ filters, setFilters, updateFilter, clearFilters }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
