// Smart environment detection for API base URL
(function(){
  const host = window.location.hostname;
  const injected = '__API_BASE_URL__';
  let base = injected && injected !== '__API_BASE_URL__' ? injected.replace(/\/$/, '') : '';
  if (host === 'localhost' || host === '127.0.0.1') {
    base = 'http://localhost:9000';
    window.__ENVIRONMENT__ = 'development';
  } else {
    base = base || 'https://api.m365.smarthaus.ai';
    window.__ENVIRONMENT__ = 'production';
  }
  window.__API_BASE_URL__ = base;
})();

