import React, { useState, useEffect } from 'react';
import Sidebar, { type Tab } from '../components/layout/Sidebar';
import ChatPanel from '../components/chat/ChatPanel';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import ABTestPanel from '../components/ab/ABTestPanel';
import KnowledgeBasePanel from '../components/kb/KnowledgeBasePanel';

const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // Generate or fetch session ID once per dashboard load
    const id = crypto.randomUUID();
    setSessionId(id);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatPanel sessionId={sessionId} />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'ab':
        return <ABTestPanel />;
      case 'kb':
        return <KnowledgeBasePanel />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} sessionId={sessionId} />
      <main className="ml-[240px] h-screen overflow-y-auto">
        {renderContent()}
      </main>
    </div>
  );
};

export default DashboardPage;
