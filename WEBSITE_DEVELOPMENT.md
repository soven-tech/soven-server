# Soven Website Development Guide

Complete guide for building soven.ca with HAL 9000 / WarGames aesthetic and AI chatbot integration.

---

## Design Philosophy

**Core Concept:** Analog 1980s sci-fi interfaces (HAL 9000, WOPR, Nostromo) meet modern AI

**Why this works:**
- Simple visuals → complex intelligence underneath
- Perfect metaphor: old Mr. Coffee (1994) + cutting-edge AI (2025)
- Anti-corporate aesthetic matches anti-surveillance philosophy
- Memorable, unique, authentic to maker culture

**Reference Films:**
- 2001: A Space Odyssey (HAL 9000's minimalist red eye)
- WarGames (WOPR's geometric displays, green terminal)
- Alien (Nostromo computer, chunky CRT aesthetics)

---

## Website Structure

### Single Page Design

**Sections:**
1. **Hero** - Animated interface + tagline
2. **What It Is** - Brief explanation (3-4 sentences)
3. **Chat Interface** - Talk to the coffee maker
4. **Philosophy** - Why we built this (anti-surveillance, right-to-repair)
5. **Specs** - Technical details (for nerds)
6. **Not For Sale Yet** - Waitlist signup

---

## Visual Design Concepts

### Option 1: HAL 9000 Eye

**Main Element:**
- Single red circle in center
- Gentle pulse when idle
- Expands/contracts when "thinking"
- Smooth, ominous animation

**Layout:**
```
┌─────────────────────────────────┐
│                                 │
│         ●  SOVEN                │
│      (red eye)                  │
│                                 │
│  "Good morning, Dave."          │
│                                 │
│  [Chat input below]             │
│                                 │
└─────────────────────────────────┘
```

**Color Scheme:**
- Background: Deep black (#000000)
- Eye: Bright red (#FF0000)
- Text: Off-white (#E0E0E0)
- Accent: Deep red (#8B0000)

---

### Option 2: Five Orbiting Circles

**Main Element:**
- Five circles representing system components:
  - ESP32 (blue)
  - AI Brain (red)
  - Voice (green)
  - Privacy (yellow)
  - Coffee (brown)
- Gentle orbit/wobble animation
- Click each to learn about that component

**Layout:**
```
┌─────────────────────────────────┐
│     ●   ●                       │
│   ●   SOVEN   ●                 │
│         ●                       │
│                                 │
│  Click to explore               │
└─────────────────────────────────┘
```

**Animation:**
- Slow orbital motion (15-30 second cycle)
- Independent wobble for each circle
- Smooth bezier curves, not linear

---

### Option 3: Terminal / WOPR Interface

**Main Element:**
- Green text on black background
- Blinking cursor
- Retro CRT scanline effect (subtle)
- Monospace font (VT323 or Courier)

**Layout:**
```
┌─────────────────────────────────┐
│ > SOVEN SYSTEM ONLINE           │
│ > AI CORE: ACTIVE               │
│ > SURVEILLANCE: DISABLED        │
│ > COFFEE STATUS: READY          │
│                                 │
│ > _                             │
└─────────────────────────────────┘
```

**Color Scheme:**
- Background: Deep black (#000000)
- Text: Phosphor green (#00FF00)
- Cursor: Bright green (blinking)
- CRT glow effect around text

---

## Chat Interface Integration

### API Endpoint

**URL:** `https://api.soven.ca/api/website/chat`

**No authentication required** (public endpoint, rate limited)

**Request:**
```javascript
POST https://api.soven.ca/api/website/chat
Content-Type: application/json

{
  "message": "What even is this?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "I'm a coffee maker with local AI, built to brew without spilling your secrets. I use ESP32-S3 and Ollama to run on-device, no cloud watching.",
  "timestamp": 1768622585
}
```

---

### Implementation Example (Vanilla JS)
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SOVEN - Local AI Coffee Maker</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      background: #000;
      color: #e0e0e0;
      font-family: 'Courier New', monospace;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    
    .hal-eye {
      width: 200px;
      height: 200px;
      border-radius: 50%;
      background: radial-gradient(circle, #ff0000, #8b0000);
      box-shadow: 0 0 60px #ff0000;
      animation: pulse 4s ease-in-out infinite;
      margin-bottom: 40px;
    }
    
    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 0.9; }
      50% { transform: scale(1.05); opacity: 1; }
    }
    
    .chat-container {
      width: 90%;
      max-width: 600px;
      margin-top: 40px;
    }
    
    .chat-history {
      height: 300px;
      overflow-y: auto;
      margin-bottom: 20px;
      padding: 20px;
      border: 1px solid #333;
      background: rgba(255, 0, 0, 0.05);
    }
    
    .message {
      margin-bottom: 15px;
      line-height: 1.6;
    }
    
    .user { color: #00ff00; }
    .ai { color: #ff6b6b; }
    
    .input-container {
      display: flex;
      gap: 10px;
    }
    
    input {
      flex: 1;
      background: #000;
      border: 1px solid #ff0000;
      color: #e0e0e0;
      padding: 15px;
      font-family: 'Courier New', monospace;
      font-size: 16px;
    }
    
    input:focus {
      outline: none;
      box-shadow: 0 0 10px #ff0000;
    }
    
    button {
      background: #8b0000;
      border: 1px solid #ff0000;
      color: #e0e0e0;
      padding: 15px 30px;
      cursor: pointer;
      font-family: 'Courier New', monospace;
      font-size: 16px;
      transition: all 0.3s;
    }
    
    button:hover {
      background: #ff0000;
      box-shadow: 0 0 20px #ff0000;
    }
    
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .thinking {
      animation: blink 1s infinite;
    }
    
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0.3; }
    }
  </style>
</head>
<body>
  <div class="hal-eye" id="eye"></div>
  <h1>SOVEN</h1>
  <p style="margin-top: 10px; opacity: 0.7;">Local AI. Zero surveillance.</p>
  
  <div class="chat-container">
    <div class="chat-history" id="chat"></div>
    <div class="input-container">
      <input 
        type="text" 
        id="input" 
        placeholder="Ask me anything..."
        autocomplete="off"
      >
      <button id="send">SEND</button>
    </div>
  </div>

  <script>
    const API_URL = 'https://api.soven.ca/api/website/chat';
    const chatEl = document.getElementById('chat');
    const inputEl = document.getElementById('input');
    const sendBtn = document.getElementById('send');
    const eyeEl = document.getElementById('eye');
    
    let isThinking = false;
    
    function addMessage(text, isUser) {
      const msg = document.createElement('div');
      msg.className = `message ${isUser ? 'user' : 'ai'}`;
      msg.textContent = `${isUser ? '> YOU: ' : '> SOVEN: '}${text}`;
      chatEl.appendChild(msg);
      chatEl.scrollTop = chatEl.scrollHeight;
    }
    
    async function sendMessage() {
      const message = inputEl.value.trim();
      if (!message || isThinking) return;
      
      isThinking = true;
      sendBtn.disabled = true;
      eyeEl.classList.add('thinking');
      
      addMessage(message, true);
      inputEl.value = '';
      
      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (data.success) {
          addMessage(data.response, false);
        } else {
          addMessage('Error: Unable to process request.', false);
        }
      } catch (error) {
        addMessage('Connection failed. Try again.', false);
        console.error('Error:', error);
      } finally {
        isThinking = false;
        sendBtn.disabled = false;
        eyeEl.classList.remove('thinking');
        inputEl.focus();
      }
    }
    
    sendBtn.addEventListener('click', sendMessage);
    inputEl.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
    
    // Welcome message
    setTimeout(() => {
      addMessage("Good morning. I'm a coffee maker that runs AI locally. Ask me anything.", false);
    }, 1000);
  </script>
</body>
</html>
```

---

## Typography

**Recommended Fonts:**

**Option 1: Retro Terminal**
- Primary: `VT323` (Google Fonts)
- Backup: `Courier New`, monospace

**Option 2: Modern Monospace**
- Primary: `IBM Plex Mono` (Google Fonts)
- Backup: `Monaco`, monospace

**Option 3: Sci-Fi Clean**
- Primary: `Orbitron` (Google Fonts) - for headers
- Body: `IBM Plex Mono` - for content
```html
<link href="https://fonts.googleapis.com/css2?family=VT323&family=IBM+Plex+Mono&family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
```

---

## Animation Guidelines

**Principles:**
- Slow and deliberate (not flashy)
- Mechanical precision (like analog equipment)
- Ominous undertones (HAL 9000 vibe)
- Smooth bezier curves, not linear

**Timing:**
- Pulse: 3-5 seconds per cycle
- Orbit: 15-30 seconds per rotation
- Transitions: 0.3-0.5 seconds
- Hover effects: 0.2 seconds

**CSS Variables:**
```css
:root {
  --transition-fast: 0.2s ease;
  --transition-medium: 0.3s ease-out;
  --transition-slow: 0.5s ease-in-out;
  --pulse-duration: 4s;
  --orbit-duration: 20s;
}
```

---

## Content Copy

### Hero Section

**Headline:**
```
SOVEN
Local AI. Zero surveillance.
```

**Subhead:**
```
A 1994 Mr. Coffee rebuilt with modern electronics.
Runs AI on-device. Remembers your preferences.
Never phones home.
```

---

### What It Is
```
Soven is a coffee maker with a brain. ESP32 microcontroller,
local AI processing (Ollama), voice control, conversation memory.
Everything runs in your kitchen. No cloud. No data collection.
No integration with surveillance capitalism.
```

---

### Philosophy
```
WHY WE BUILT THIS

Big Tech wants your coffee maker to report to the mothership.
We think that's dystopian nonsense.

Soven is built on three principles:
1. Local processing - AI runs on-device, not in someone's data center
2. User ownership - You own the hardware, the data, the experience
3. Right to repair - Open documentation, no vendor lock-in

We're makers who got tired of "smart" appliances that are
actually surveillance devices with features bolted on.

Soven is what IoT should have been.
```

---

### Specs (For Nerds)
```
HARDWARE
- ESP32-S3 microcontroller (dual-core, 240MHz)
- Local storage for conversation history
- WiFi (local network only, optional)
- BLE for app communication
- Standard 120V coffee maker base

SOFTWARE
- Ollama AI (llama3.2, runs locally)
- Coqui TTS (18+ voices, multiple accents)
- PostgreSQL database (conversation history)
- FastAPI backend
- Flutter mobile app

PRIVACY
- Zero cloud connectivity
- No user tracking
- No data collection
- Open source firmware (coming soon)
- Self-hostable API

FEATURES
- Voice control via mobile app
- AI personality customization
- Conversation memory
- Authentic personality voices
- Command detection (start/stop brewing)
```

---

### Not For Sale Yet
```
STILL IN DEVELOPMENT

We're perfecting the existential dread-to-caffeine ratio.

Interested in updates?
[Email signup form]

Or follow the build:
GitHub: github.com/soven-tech
```

---

## Technical Requirements

### Hosting Options

**Option 1: Static Site (Recommended for MVP)**
- Netlify, Vercel, or GitHub Pages
- Free tier works fine
- Just HTML/CSS/JS
- API calls to api.soven.ca

**Option 2: WordPress Integration**
- Current soven.ca is WordPress
- Add custom page template
- Embed chat interface
- Keep existing blog/content

**Option 3: Self-Hosted**
- Same server as API
- Nginx to serve static files
- Minimal resource usage

---

### Performance Optimization

**Critical:**
- Lazy load animations
- Minimize initial bundle
- Progressive enhancement
- Works without JavaScript (show static content)

**Assets:**
- SVG for graphics (tiny file size)
- CSS animations (no JavaScript overhead)
- WebP images with fallbacks
- Inline critical CSS

**Target:**
- First contentful paint: < 1.5s
- Time to interactive: < 3s
- Lighthouse score: 95+

---

## Development Checklist

### Phase 1: Core Design
- [ ] Choose visual concept (HAL eye / Five circles / Terminal)
- [ ] Create HTML structure
- [ ] Implement CSS animations
- [ ] Test on mobile devices
- [ ] Ensure accessibility (screen readers, keyboard nav)

### Phase 2: Chat Integration
- [ ] Connect to API endpoint
- [ ] Handle loading states
- [ ] Display conversation history
- [ ] Error handling
- [ ] Rate limit feedback

### Phase 3: Content
- [ ] Write all copy sections
- [ ] Create logo/branding assets
- [ ] Add email signup form
- [ ] Link to GitHub repos

### Phase 4: Polish
- [ ] Cross-browser testing
- [ ] Mobile responsiveness
- [ ] Performance optimization
- [ ] SEO meta tags
- [ ] Social sharing cards

### Phase 5: Launch
- [ ] Deploy to production
- [ ] Test API in production
- [ ] Monitor for errors
- [ ] Analytics (privacy-respecting)

---

## API Integration Reference

**Endpoint:** `https://api.soven.ca/api/website/chat`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Your question here"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "response": "AI response text",
  "timestamp": 1768622585
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "response": "I seem to be experiencing a malfunction. Please try again.",
  "error": "Error details"
}
```

**Rate Limit:** 10 requests per minute per IP

**Error Handling:**
```javascript
try {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  const data = await response.json();
  
  if (data.success) {
    // Display response
  } else {
    // Show error message
  }
} catch (error) {
  // Handle network errors
  console.error('API Error:', error);
  showErrorMessage('Unable to connect. Try again.');
}
```

---

## Example Conversations

Test these to see the personality in action:
```
Q: "What even is this?"
A: "I'm a coffee maker with local AI, built to brew without 
    spilling your secrets. I use ESP32-S3 and Ollama to run 
    on-device, no cloud watching."

Q: "Can you connect to Google Home?"
A: "No. Your coffee habits stay in your kitchen, where they 
    belong. I'm not sending data to any cloud, least of all 
    Google's."

Q: "How does it work?"
A: "ESP32 runs Ollama locally for AI, Coqui for voice. 
    Everything happens in your kitchen, not someone's data 
    center."

Q: "When can I buy one?"
A: "Still in development. We're perfecting the existential 
    dread-to-caffeine ratio."

Q: "Are you smarter than Alexa?"
A: "I'm not surveilling you, so yes. By default."
```

---

## Brand Voice Guidelines

**Do:**
- Be direct and honest
- Use dry wit
- Reference maker culture
- Acknowledge the absurdity of talking coffee makers
- Be helpful despite the snark

**Don't:**
- Use corporate speak ("leverage", "synergy", "empower")
- Be mean or alienating
- Make it about the team (focus on the product)
- Oversell or hype
- Use exclamation points (you're HAL, not a puppy)

**Tone:**
- Confident but not arrogant
- Smart but not condescending
- Sarcastic but actually helpful
- Self-aware about being a coffee maker AI

---

## Related Resources

**GitHub Repositories:**
- Server API: https://github.com/soven-tech/soven-server
- Flutter App: https://github.com/soven-tech/soven-coffee-app
- ESP32 Firmware: https://github.com/soven-tech/soven-coffee-firmware

**API Documentation:**
- See `FLUTTER_INTEGRATION.md` in server repo

**Design Inspiration:**
- HAL 9000 interface scenes (2001: A Space Odyssey)
- WOPR displays (WarGames)
- Nostromo computer (Alien)
- Strong Bad Emails (Homestar Runner)
- Retro terminal aesthetics

---

## Support

For technical API questions, contact: [your contact]

For design/branding questions, contact: [your contact]

For bugs in the chatbot, file an issue: https://github.com/soven-tech/soven-server/issues

---

Built with ❤️ and caffeine
No clouds were harmed in the making of this website
