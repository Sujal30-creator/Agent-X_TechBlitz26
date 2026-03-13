import { useState } from 'react'

function App() {

  const [formData, setFormData] = useState({
    source: 'website',
    name: '',
    contact: '',
    company: '',
    message: ''
  })

  const [status, setStatus] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()

    setStatus('Sending lead to AI agent...')

    try {

      const response = await fetch('http://127.0.0.1:5000/api/lead', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {

        setStatus('Lead captured successfully! Check Telegram.')

        setFormData({
          source: 'website',
          name: '',
          contact: '',
          company: '',
          message: ''
        })

      } else {
        setStatus('Failed to send lead.')
      }

    } catch (error) {
      console.error(error)
      setStatus('Server connection error.')
    }
  }

  return (

    <div style={{ padding: '50px', fontFamily: 'sans-serif' }}>

      <h1>TechBlitz Lead Generator</h1>
      <p>Simulating multi-channel lead capture</p>

      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '15px',
          maxWidth: '350px'
        }}
      >

        {/* Lead Source */}
        <select
          value={formData.source}
          onChange={(e) =>
            setFormData({ ...formData, source: e.target.value })
          }
        >
          <option value="website">Website Form</option>
          <option value="instagram">Instagram Ad</option>
          <option value="whatsapp">WhatsApp Message</option>
          <option value="linkedin">LinkedIn Inquiry</option>
        </select>

        {/* Name */}
        <input
          type="text"
          placeholder="Full Name"
          value={formData.name}
          onChange={(e) =>
            setFormData({ ...formData, name: e.target.value })
          }
          required
        />

        {/* Contact */}
        <input
          type="text"
          placeholder="Email or Phone"
          value={formData.contact}
          onChange={(e) =>
            setFormData({ ...formData, contact: e.target.value })
          }
          required
        />

        {/* Company */}
        <input
          type="text"
          placeholder="Company (optional)"
          value={formData.company}
          onChange={(e) =>
            setFormData({ ...formData, company: e.target.value })
          }
        />

        {/* Message */}
        <textarea
          placeholder="What are you interested in?"
          rows="4"
          value={formData.message}
          onChange={(e) =>
            setFormData({ ...formData, message: e.target.value })
          }
          required
        />

        <button
          type="submit"
          style={{
            padding: '10px',
            background: 'black',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          Submit Lead
        </button>

      </form>

      {status && (
        <p style={{ marginTop: '20px', fontWeight: 'bold' }}>
          {status}
        </p>
      )}

    </div>
  )
}

export default App
