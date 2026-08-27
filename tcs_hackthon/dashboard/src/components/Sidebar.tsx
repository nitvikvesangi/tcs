import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Sparkles, Package, Percent, BarChart3, Settings, HelpCircle, Menu } from 'lucide-react';
import { cn } from './ActionBadge';

interface Props {
  isOpen: boolean;
  setIsOpen: (val: boolean) => void;
}

export const Sidebar: React.FC<Props> = ({ isOpen, setIsOpen }) => {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'AI Recommendations', path: '/recommendations', icon: Sparkles },
    { name: 'Inventory', path: '/inventory', icon: Package },
    { name: 'Promotions', path: '/promotions', icon: Percent },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      <aside className={cn(
        "fixed lg:sticky top-0 left-0 h-screen bg-slate-900 text-slate-300 w-64 flex flex-col transition-transform duration-300 z-50",
        isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="h-16 flex items-center px-6 font-bold text-white text-xl border-b border-slate-800 gap-2">
          <Sparkles className="text-accent text-purple-400" size={24} />
          QuickAI
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-3 flex flex-col gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors",
                  isActive 
                    ? "bg-purple-600/10 text-purple-400" 
                    : "hover:bg-slate-800 hover:text-white"
                )}
              >
                <Icon size={18} />
                {item.name}
              </NavLink>
            );
          })}
        </div>

        <div className="p-4 border-t border-slate-800 flex flex-col gap-1 px-3">
          <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-slate-400 hover:bg-slate-800 hover:text-white transition-colors w-full text-left">
            <Settings size={18} /> Settings
          </button>
          <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-slate-400 hover:bg-slate-800 hover:text-white transition-colors w-full text-left">
            <HelpCircle size={18} /> Help
          </button>
        </div>
      </aside>
    </>
  );
};
