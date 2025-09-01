function checkImagesAndRedirect() {
  let attempt = 0; // Initialize attempt counter
  const checkInterval = 10000; // Check every 10 seconds (10000 milliseconds)

  // Define the interval ID to be able to clear it later
  let intervalId = setInterval(() => {
    attempt += 1; // Increment the attempt counter

    // Fetch function to check if the extraction is complete
    fetch('/check-extraction-status')
      .then(response => response.json())
      .then(data => {
        if (data.extraction.completed && data.analysis.completed) {
          // If both extraction and analysis are complete, clear the interval and redirect to the display page
          clearInterval(intervalId);
          window.location.href = '/display';
        } else if (data.extraction.error || data.analysis.error) {
          // If there is an error, clear the interval and redirect to the error page
          clearInterval(intervalId);
          window.location.href = '/errorpage';
        }
      })
      .catch(error => {
        // If there is an error during the fetch, log it and clear the interval
        console.error('Failed to check extraction status:', error);
        clearInterval(intervalId);
      });
  }, checkInterval);
}

// Expose the function so it can be called when the DOM content is loaded
window.checkImagesAndRedirect = checkImagesAndRedirect;

// When the DOM is fully loaded, invoke the checkImagesAndRedirect function
document.addEventListener('DOMContentLoaded', () => {
  checkImagesAndRedirect();

  const socket = io();

  // Listen for 'update' events from the server
  socket.on('update', function(data) {
    const messageDiv = document.getElementById('progress-message');
    // Extract image name from the full path in data.message
    let messageText = data.message;
    if (messageText.includes('static/output_images/')) {
      const parts = messageText.split('/');
      const imageName = parts.pop();
      messageText = `Downloading ${imageName}`;
    }
    messageDiv.textContent = messageText; // Update the text content of the messageDiv
  });
});
