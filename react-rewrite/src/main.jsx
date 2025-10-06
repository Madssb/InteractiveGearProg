import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import 'styles/theme.css';
import Chart from './chart.jsx';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Chart />
  </StrictMode>,
)
