// API Base URL
const API_URL = 'http://127.0.0.1:5000/api/v1';

// Get DOM elements
const textarea = document.querySelector('textarea');
const fileInput = document.querySelector('input[type="file"]');
const langSpan = document.getElementById('lang');
const listenBtn = document.querySelector('.listen-btn');
const clearBtn = document.querySelector('.clear-btn');
const audioPlayer = document.querySelector('audio');

// Listen button click handler
listenBtn.addEventListener('click', async () => {
    // Disable button during processing
    listenBtn.disabled = true;
    listenBtn.textContent = '⏳ Processing...';

    try {
        let response;

        // Check if user uploaded a file
        if (fileInput.files.length > 0) {
            response = await handleFileUpload();
        } 
        // Otherwise, use textarea text
        else if (textarea.value.trim()) {
            response = await handleTextInput();
        } 
        // No input provided
        else {
            alert('Please enter text or upload a file!');
            return;
        }

        // If API call successful
        // If API call successful
        // If API call successful
if (response.success) {
    // Update detected language
    langSpan.textContent = response.language_name || response.language;
    
    // Play audio - FIXED
    const audioSource = audioPlayer.querySelector('source');
    if (audioSource) {
        audioSource.src = response.audio_url;
    } else {
        audioPlayer.src = response.audio_url;
    }
    audioPlayer.load();  // Force reload
    audioPlayer.play();  // Auto-play
    
    console.log('Audio loaded:', response.audio_url);
} else {
    alert('Error: ' + response.error);
}

    } catch (error) {
        alert('Failed to connect to server: ' + error.message);
    } finally {
        // Re-enable button
        listenBtn.disabled = false;
        listenBtn.textContent = '🔊 Listen';
    }
});

// Handle text input
async function handleTextInput() {
    const text = textarea.value.trim();
    
    // Call pipeline API with text input
    const res = await fetch(`${API_URL}/pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            input_type: 'text',
            text: text
        })
    });
    
    return await res.json();
}

// Handle file upload (PDF, DOCX, Images)
async function handleFileUpload() {
    const file = fileInput.files[0];
    const ext = file.name.split('.').pop().toLowerCase();
    
    // Determine input type based on file extension
    let inputType;
    if (ext === 'pdf' || ext === 'docx') {
        inputType = 'file';
    } else if (['png', 'jpg', 'jpeg', 'bmp', 'tiff'].includes(ext)) {
        inputType = 'image';
    } else {
        throw new Error('Unsupported file type');
    }
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('input_type', inputType);
    formData.append(inputType === 'file' ? 'file' : 'image', file);
    
    // Call pipeline API with file
    const res = await fetch(`${API_URL}/pipeline`, {
        method: 'POST',
        body: formData
    });
    
    return await res.json();
}

// Clear button handler
clearBtn.addEventListener('click', () => {
    textarea.value = '';
    fileInput.value = '';
    langSpan.textContent = 'Auto';
    audioPlayer.pause();
    audioPlayer.src = '';
});