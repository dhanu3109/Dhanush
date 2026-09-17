import React, { useState } from 'react';
import { VoterProvider, useVoter } from './context/VoterContext';
import { Navbar } from './components/layout/Navbar';
import { AccessibilityToolbar } from './components/layout/AccessibilityToolbar';
import { ProgressBar } from './components/layout/ProgressBar';
import { MainContainer } from './components/layout/MainContainer';
import { VoterJourney } from './components/timeline/VoterJourney';
import { CandidateComparison } from './components/candidate/CandidateComparison';
import { InteractiveSimulatorModal } from './components/simulators/InteractiveSimulatorModal';

const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'timeline' | 'candidates' | 'polling' | 'ballot'>('timeline');

  return (
    <MainContainer>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <AccessibilityToolbar />
      <ProgressBar />

      <div className="py-8">
        {activeTab === 'timeline' && <VoterJourney />}
        {activeTab === 'candidates' && <CandidateComparison />}
      </div>

      <InteractiveSimulatorModal />
    </MainContainer>
  );
};

export const App: React.FC = () => {
  return (
    <VoterProvider>
      <AppContent />
    </VoterProvider>
  );
};

export default App;
