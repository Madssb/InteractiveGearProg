import ChangelogPage from 'pages/ChangelogPage';
import ChartPage from 'pages/ChartPage';
import PrivacyPage from 'pages/PrivacyPage';
import { BrowserRouter, Route, Routes } from 'react-router';
import 'styles/chart.css';
import 'styles/right-click.css';
import 'styles/theme.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChartPage />} />
        <Route path="/changelog" element={<ChangelogPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/faq" element={<PrivacyPage />} />
      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);