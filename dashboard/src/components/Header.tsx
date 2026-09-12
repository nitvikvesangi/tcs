import React from 'react';
import { Menu, Search, Bell, User } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

interface Props {
  title: string;
  toggleSidebar: () => void;
}

export const Header: React.FC<Props> = ({ title, toggleSidebar }) => {
  const { filters, updateFilter } = useAppContext();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 lg:px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <button onClick={toggleSidebar} className="lg:hidden p-2 -ml-2 text-slate-500 hover:bg-slate-100 rounded-lg">
          <Menu size={20} />
        </button>
        <h1 className="text-xl font-semibold text-slate-900 hidden sm:block">{title}</h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4 lg:gap-6">
        <div className="hidden md:flex items-center gap-2">
          <select 
            value={filters.city || ''} 
            onChange={(e) => updateFilter('city', e.target.value || undefined)}
            className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 outline-none focus:border-purple-400"
          >
            <option value="">All Cities</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Bengaluru">Bengaluru</option>
            <option value="Mumbai">Mumbai</option>
          </select>
          <select 
            value={filters.dark_store_id || ''} 
            onChange={(e) => updateFilter('dark_store_id', e.target.value || undefined)}
            className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 outline-none focus:border-purple-400"
          >
            <option value="">All Stores</option>
            <option value="HYD-DS1">HYD-DS1</option>
            <option value="HYD-DS2">HYD-DS2</option>
            <option value="HYD-DS3">HYD-DS3</option>
            <option value="BLR-DS1">BLR-DS1</option>
            <option value="BLR-DS2">BLR-DS2</option>
            <option value="MUM-DS1">MUM-DS1</option>
          </select>
        </div>

        <div className="relative hidden sm:block">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input 
            type="text" 
            placeholder="Search products..." 
            value={filters.search_query || ''}
            onChange={(e) => updateFilter('search_query', e.target.value || undefined)}
            className="pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-sm w-48 lg:w-64 outline-none focus:border-purple-400 focus:bg-white transition-colors"
          />
        </div>

        <div className="flex items-center gap-3 border-l border-slate-200 pl-4 lg:pl-6 ml-2">
          <button className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors">
            <Bell size={20} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
          </button>
          <div className="flex items-center gap-2 cursor-pointer p-1 pr-2 rounded-full hover:bg-slate-50 transition-colors">
            <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-sm">
              RA
            </div>
            <span className="text-sm font-medium text-slate-700 hidden lg:block">Retailer Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
};
