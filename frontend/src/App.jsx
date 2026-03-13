import { useState } from 'react'

function App() {
  const [formData, setFormData] = useState({
    name: '',
    contact_info: '',
    source: 'Website Form' // Default source for the dummy page
  });
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Sending to AI Agent...');

    try {
        const response = await fetch('http://127.0.0.1:5000/api/lead', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setStatus('Lead Sent Successfully! Check Telegram.');
        setFormData({ name: '', contact_info: '', source: 'Website Form' }); // Reset form
      } else {
        setStatus('Failed to send lead.');
      }
    } catch (error) {
      console.error('Error:', error);
      setStatus('Server connection error.');
    }
  };

  return (
    <div style={{ padding: '50px', fontFamily: 'sans-serif' }}>
      <h1>TechBlitz Lead Generator</h1>
      <p>Simulating a prospect filling out a website form.</p>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px', maxWidth: '300px' }}>
        <input 
          type="text" 
          placeholder="Lead Name" 
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required 
        />
        <input 
          type="text" 
          placeholder="Email or Phone" 
          value={formData.contact_info}
          onChange={(e) => setFormData({...formData, contact_info: e.target.value})}
          required 
        />
        <select 
          value={formData.source}
          onChange={(e) => setFormData({...formData, source: e.target.value})}
        >
          <option value="Website Form">Website Form</option>
          <option value="Instagram Ad">Instagram Ad</option>
          <option value="WhatsApp">WhatsApp</option>
        </select>
        
        <button type="submit" style={{ padding: '10px', background: 'black', color: 'white' }}>
          Submit Lead
        </button>
      </form>

      {status && <p style={{ marginTop: '20px', fontWeight: 'bold' }}>{status}</p>}
    </div>
  )
}

export default App