import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, BarChart2, FlaskConical, Database, LogOut } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/Button';

export type Tab = 'chat' | 'analytics' | 'ab' | 'kb';

interface SidebarProps {
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
  sessionId: string;
}

const navItems = [
  { id: 'chat', label: 'Sales Chat', icon: MessageSquare },
  { id: 'analytics', label: 'Analytics', icon: BarChart2 },
  { id: 'ab', label: 'A/B Test', icon: FlaskConical },
  { id: 'kb', label: 'Knowledge Base', icon: Database },
] as const;

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, sessionId }) => {
  const clearToken = useAuthStore((state) => state.clearToken);

  const handleLogout = () => {
    clearToken();
    window.location.href = '/'; 
  };

  return (
    <motion.div
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="fixed left-0 top-0 h-screen w-[240px] border-r border-[#F1F3F1] bg-white flex flex-col justify-between"
    >
      <div>
        <div className="p-6 flex items-center space-x-2">
          <span className="text-xl font-semibold text-auralis-green tracking-tight font-display font-normal">auralis</span>
          <div className="w-2 h-2 rounded-full bg-[#10b981] shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-blink"></div>
        </div>
        
        <nav className="px-3 space-y-1 mt-4 relative">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as Tab)}
                className={`relative w-full flex items-center px-3 py-2 rounded-lg transition-all font-sans text-sm ${
                  isActive
                    ? 'text-auralis-green font-medium'
                    : 'text-auralis-text font-light hover:bg-auralis-frost'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-pill"
                    className="absolute inset-0 bg-auralis-cream rounded-lg z-0"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
                <div className="relative z-10 flex items-center space-x-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t border-[#F1F3F1]">
        <div className="flex items-center justify-between mb-4 px-2">
          <span className="text-xs font-sans font-medium text-auralis-text uppercase tracking-widest">Session</span>
          <span className="text-xs font-mono text-auralis-mist bg-auralis-paper px-2 py-1 rounded">
            {sessionId.slice(0, 8)}
          </span>
        </div>
        <Button
          variant="ghost"
          onClick={handleLogout}
          className="w-full flex items-center justify-center space-x-2 py-2 px-3 text-auralis-mist hover:text-auralis-sage no-underline"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </Button>
      </div>
    </motion.div>
  );
};

export default Sidebar;
