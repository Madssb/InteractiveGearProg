import { BrowserRouter, Route, Routes } from 'react-router';
import 'styles/chart.css';
import 'styles/right-click.css';
import 'styles/theme.css';
import ChangelogPage from './pages/ChangelogPage.jsx';
import { ChartPage, ChartPageBareBones } from './pages/ChartPage.jsx';
import FaqPage from './pages/FaqPage.jsx';
import PrivacyPage from './pages/PrivacyPage.jsx';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChartPage />} />
        <Route path="/changelog" element={<ChangelogPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/faq" element={<FaqPage />} />
        <Route path="/barebones" element={<ChartPageBareBones />} />
      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);