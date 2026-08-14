// Client-side Interactive Logic for MediTriage AI

let selectedRegion = "";
let recognition = null;
let isListening = false;

// 1. Anatomical Body Region Selector
function selectRegion(region) {
  selectedRegion = region;
  document.getElementById('input-body-region').value = region;
  
  // Update Pills UI
  const chips = document.querySelectorAll('.region-chip');
  chips.forEach(chip => chip.classList.remove('active'));
  
  const selectedChip = Array.from(chips).find(c => c.textContent.toLowerCase().includes(region));
  if (selectedChip) selectedChip.classList.add('active');

  // Highlight SVG Body Parts
  const parts = document.querySelectorAll('.svg-part');
  parts.forEach(part => part.style.opacity = "0.4");

  const targetSvg = document.getElementById(`region-${region}`);
  if (targetSvg) {
    targetSvg.style.opacity = "1";
    targetSvg.style.filter = "drop-shadow(0 0 8px #06b6d4)";
  }
}

// 2. Append Symptom Pills to Textarea
function appendSymptom(text) {
  const textarea = document.getElementById('symptoms');
  if (textarea.value.trim() === "") {
    textarea.value = text;
  } else {
    textarea.value += ", " + text;
  }
  textarea.focus();
}

// 3. Web Speech API Voice Input (Speech-to-Text)
function toggleSpeechRecognition() {
  const micBtn = document.getElementById('btn-mic');
  
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert("Speech recognition is not supported in this browser. Please type your symptoms.");
    return;
  }

  if (isListening) {
    if (recognition) recognition.stop();
    isListening = false;
    micBtn.classList.remove('listening');
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  recognition.onstart = function() {
    isListening = true;
    micBtn.classList.add('listening');
  };

  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    appendSymptom(transcript);
    isListening = false;
    micBtn.classList.remove('listening');
  };

  recognition.onerror = function() {
    isListening = false;
    micBtn.classList.remove('listening');
  };

  recognition.onend = function() {
    isListening = false;
    micBtn.classList.remove('listening');
  };

  recognition.start();
}

// 4. Image Upload & Preview Handler
function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    document.getElementById('image-preview-thumb').src = e.target.result;
    document.getElementById('image-filename').textContent = file.name;
    document.getElementById('image-preview-container').style.display = 'flex';
    document.getElementById('upload-label').style.display = 'none';
    document.getElementById('input-image-attached').value = 'true';
  };
  reader.readAsDataURL(file);
}

function removeImageUpload(event) {
  event.stopPropagation();
  document.getElementById('file-image').value = '';
  document.getElementById('image-preview-container').style.display = 'none';
  document.getElementById('upload-label').style.display = 'block';
  document.getElementById('input-image-attached').value = 'false';
}

// 5. LocalStorage Triage History Logger
function toggleHistoryModal() {
  const modal = document.getElementById('history-modal');
  if (modal.style.display === 'none' || modal.style.display === '') {
    renderHistory();
    modal.style.display = 'flex';
  } else {
    modal.style.display = 'none';
  }
}

function renderHistory() {
  const container = document.getElementById('history-items-container');
  const history = JSON.parse(localStorage.getItem('meditriage_history') || '[]');
  
  if (history.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted);">No saved triage sessions in local storage.</p>`;
    return;
  }

  let html = `<ul style="list-style:none;">`;
  history.reverse().forEach(item => {
    html += `
      <li style="padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.1);">
        <strong>${item.date}</strong> - <span class="badge-tag ${item.code}">${item.urgency}</span><br>
        <small style="color:var(--text-muted);">${item.symptoms.substring(0, 60)}...</small>
      </li>
    `;
  });
  html += `</ul>`;
  container.innerHTML = html;
}

// Save Current Triage Result to History
window.addEventListener('DOMContentLoaded', () => {
  const badgeElement = document.querySelector('.result-header-badge');
  if (badgeElement) {
    const urgencyText = badgeElement.querySelector('h2')?.textContent || "Assessment";
    const symptomsText = document.getElementById('symptoms')?.value || "Symptoms evaluated";
    const code = badgeElement.classList.contains('red') ? 'red' :
                 badgeElement.classList.contains('orange') ? 'orange' :
                 badgeElement.classList.contains('yellow') ? 'yellow' : 'green';

    const history = JSON.parse(localStorage.getItem('meditriage_history') || '[]');
    history.push({
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' }),
      urgency: urgencyText,
      code: code,
      symptoms: symptomsText
    });
    if (history.length > 10) history.shift();
    localStorage.setItem('meditriage_history', JSON.stringify(history));
  }
});
