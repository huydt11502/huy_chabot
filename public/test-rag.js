// Quick debug script - paste into browser console

console.log('🔍 Testing RAG API Connection...');

const API_BASE = 'http://localhost:5000/api';

// Test 1: Health Check
fetch(`${API_BASE}/health`)
  .then(res => res.json())
  .then(data => {
    console.log('✅ Health Check:', data);
  })
  .catch(err => {
    console.error('❌ Health Check Failed:', err);
  });

// Test 2: Get Diseases  
setTimeout(() => {
  fetch(`${API_BASE}/diseases`)
    .then(res => res.json())
    .then(data => {
      console.log(`✅ Diseases: ${data.total} found`);
      console.log('First 3 diseases:', data.diseases.slice(0, 3));
    })
    .catch(err => {
      console.error('❌ Get Diseases Failed:', err);
    });
}, 1000);

console.log('🎯 Tests queued. Check results above.');
