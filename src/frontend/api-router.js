// API router wraps fetch against detected base URL
window.api = (function(){
  function base(){ return (window.__API_BASE_URL__ || '').replace(/\/$/, ''); }
  async function get(path){ const res = await fetch(base()+path, { headers: authHeaders() }); if(!res.ok) throw new Error(await res.text()); return res.json(); }
  async function post(path, body){ const res = await fetch(base()+path, { method:'POST', headers: { 'Content-Type': 'application/json', ...authHeaders() }, body: JSON.stringify(body||{}) }); if(!res.ok) throw new Error(await res.text()); return res.json(); }
  function authHeaders(){ const tok=localStorage.getItem('access_token'); return tok?{ Authorization: `Bearer ${tok}` }:{}; }
  return { base, get, post };
})();
