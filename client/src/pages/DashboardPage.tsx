import React, { useState, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import Sidebar, { type Tab } from '../components/layout/Sidebar';
import ChatPanel from '../components/chat/ChatPanel';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import ABTestPanel from '../components/ab/ABTestPanel';
import KnowledgeBasePanel from '../components/kb/KnowledgeBasePanel';
import { tabTransition } from '../components/ui/Animations';

const tabs: Array<{ id: Tab; render: (sessionId: string) => React.ReactNode }> = [
  { id: 'chat', render: (sessionId) => <ChatPanel sessionId={sessionId} /> },
  { id: 'analytics', render: () => <AnalyticsDashboard /> },
  { id: 'ab', render: () => <ABTestPanel /> },
  { id: 'kb', render: () => <KnowledgeBasePanel /> },
];

const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [visitedTabs, setVisitedTabs] = useState<Set<Tab>>(() => new Set(['chat']));
  const [sessionId] = useState<string>(() => crypto.randomUUID());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const shouldReduceMotion = useReducedMotion() ?? false;

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    setVisitedTabs((current) => {
      if (current.has(activeTab)) return current;
      const next = new Set(current);
      next.add(activeTab);
      return next;
    });
  }, [activeTab]);

  return (
    <div className="relative z-10 min-h-screen bg-white/95">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        sessionId={sessionId}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <main className="relative lg:ml-[240px] h-screen overflow-hidden">
        {tabs.map((tab) => {
          if (!visitedTabs.has(tab.id)) return null;

          const isActive = activeTab === tab.id;

          return (
            <motion.section
              key={tab.id}
              initial={false}
              animate={isActive ? 'active' : 'inactive'}
              variants={tabTransition(shouldReduceMotion)}
              className={`absolute inset-x-0 bottom-0 top-16 flex flex-col lg:top-0 ${isActive ? 'pointer-events-auto' : 'pointer-events-none'}`}
              aria-hidden={!isActive}
              style={{
                transform: 'translateZ(0)',
                willChange: 'transform, opacity',
                zIndex: isActive ? 1 : 0,
              }}
            >
              {tab.render(sessionId)}
            </motion.section>
          );
        })}
      </main>
    </div>
  );
};

export default DashboardPage;
