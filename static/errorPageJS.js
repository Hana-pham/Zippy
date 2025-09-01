document.addEventListener('DOMContentLoaded', function() {
    var extractButton = document.getElementById('extractButton');
    var inputUrl = document.getElementById('inputUrl');
    var result = document.getElementById('result');

    extractButton.addEventListener('click', function(event) {
        event.preventDefault();
        var url = inputUrl.value;

        var pattern = new RegExp('^https:\/\/www.figma.com\/design\/.*$');
        if (!pattern.test(url)) {
            result.textContent = 'Error: URL does not match the required format.';
            return;
        }

        result.textContent = 'Checking URL...';

        fetch('/check-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'url=' + encodeURIComponent(url)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network error or the server returned an invalid response.');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // URL is valid, start the image extraction process
                result.textContent = 'Downloading images...';
                // Redirect to loading page or display a loading message
                window.location.href = '/loading'; // Redirect to loading page

                // Initiate the image extraction by sending a POST request to '/extract'
                return fetch('/extract', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: 'inputUrl=' + encodeURIComponent(url)
                });
            } else {
                result.textContent = 'Error: ' + data.message;
                throw new Error('URL is not accessible.');
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network error while extracting images.');
            }
            // If the server returns a success status, the images are being processed
            // You can add additional logic here if needed
        })
        .catch(error => {
            result.textContent = 'Error: ' + error.message;
            setTimeout(function() {
                // window.location.reload();
            }, 2000);
        });
    });

    // Event listeners for display and loading buttons
    var displayButton = document.getElementById('display');
    displayButton.addEventListener('click', function(event) {
        window.location.href = '/display';
    });

    var loadingButton = document.getElementById('loading');
    loadingButton.addEventListener('click', function(event) {
        window.location.href = '/loading';
    });
});
