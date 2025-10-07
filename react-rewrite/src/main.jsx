import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import 'styles/chart.css';
import 'styles/right-click.css';
import 'styles/theme.css';
import Chart from './chart';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Chart />
  </StrictMode>,
)
