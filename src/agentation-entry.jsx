import React from 'react';
import { createRoot } from 'react-dom/client';
import { Agentation } from 'agentation';

function initAgentation() {
  // Prevent duplicate mounts
  if (window.__AGENTATION_MOUNTED__) return;
  window.__AGENTATION_MOUNTED__ = true;

  let rootEl = document.getElementById('agentation-root');
  if (!rootEl) {
    rootEl = document.createElement('div');
    rootEl.id = 'agentation-root';
    document.body.appendChild(rootEl);
  }

  const root = createRoot(rootEl);
  root.render(React.createElement(Agentation, null));
  console.log('🚀 [Agentation] Visual AI feedback widget active.');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAgentation);
} else {
  initAgentation();
}
