import ChangelogPage from '@/pages/ChangelogPage.jsx';
import ChartPage from '@/pages/ChartPage.jsx';
import FaqPage from '@/pages/FaqPage.jsx';
import PrivacyPage from '@/pages/PrivacyPage.jsx';
import '@/styles/chart.css';
import '@/styles/theme.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChartPage />} />
        <Route path="/changelog" element={<ChangelogPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/faq" element={<FaqPage />} />
      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
