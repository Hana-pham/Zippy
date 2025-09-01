// displayJS.js
document.addEventListener('DOMContentLoaded', async function() {
    let dataTable;

    try {
        const response = await fetch('/check-images-count');
        const data = await response.json();
        const images = data.images;

        const tableData = images.map((img, index) => [
            `<div class="thumbnail-wrapper">
                <img src="/static/output_images/${img}" alt="Thumbnail" class="thumbnail">
                <div class="thumbnail-name">${img}</div>
            </div>`,
            `<div class="btn-container">
                <button class="btn btn-outline-secondary showVariation" data-screen-index="${index + 1}" data-toggle="modal" data-target="#variationsModal">See Variations</button>
            </div>`,
            `<div class="btn-container">
                <button class="btn btn-outline-secondary showImage" data-image-url="/static/output_images/${img}" data-toggle="modal" data-target="#imageModal">See Screen</button>
            </div>`,
            `<div class="checkbox-container">
                <label class="checkbox-container">
                    <input type="checkbox" id="screen${index}" name="selectedScreens" value="${img}">
                    <span class="checkmark"></span>
                </label>
            </div>`
        ]);

        dataTable = $('#screensContainer').DataTable({
            data: tableData,
            ordering: false,
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            columns: [
                { title: "Thumbnail" },
                { title: "Variations" },
                { title: "Screen" },
                { title: "Select" }
            ]
        });

        // Event delegation for dynamically added modal buttons (image preview)
        $('#screensContainer tbody').on('click', '.showImage', function () {
            const imageUrl = $(this).data('image-url');
            $('#imageModal img').attr('src', imageUrl);
            $('#imageModal').modal('show');
        });

        $('#screensContainer tbody').on('click', '.showVariation', async function () {
            const screenIndex = $(this).data('screen-index');
            $('#currentScreenIndex').val(screenIndex);

            console.log(`Fetching variations for screen ${screenIndex}`);  // Debugging
            const response = await fetch(`/get-variations/${screenIndex}`);
            const data = await response.json();
            const variations = data.images;
            console.log(`Received variations: ${variations}`);  // Debugging

            // Clear previous data
            if ($.fn.DataTable.isDataTable('#variationsTable')) {
                $('#variationsTable').DataTable().clear().destroy();
            }

            // Populate new data
            const variationsTableContent = variations.map(variation => [
                `<img src="${variation}" alt="Variation" class="img-fluid mb-3">`
            ]);

            $('#variationsTable').DataTable({
                data: variationsTableContent,
                ordering: false,
                paging: false,
                searching: false,
                info: false,
                columns: [
                    { title: "Variation" }
                ]
            });

            $('#variationsModal').modal('show');
        });

    } catch (error) {
        console.error('Error:', error);
    }

    // Checkbox selection handling
    $('input[name="selectedScreens"]').change(function() {
        var selectedImages = [];
        $('input[name="selectedScreens"]:checked').each(function() {
            selectedImages.push($(this).val());
        });
        localStorage.setItem('selectedImages', JSON.stringify(selectedImages));
    });

    $(document).ready(function() {
        $('#example').DataTable();

        // Event listener for showing variations
        $('#screensContainer tbody').on('click', '.showVariation', async function () {
            const screenIndex = $(this).data('screen-index');
            $('#currentScreenIndex').val(screenIndex); // Store the screen index in the hidden field

            // Your existing code for showing variations...
        });

        // Update the download function to include screen indices
        function downloadZip() {
            var selectedImages = [];
            var screenIndices = [];

            $('input[name="selectedScreens"]:checked').each(function() {
                selectedImages.push($(this).val());
                screenIndices.push($(this).closest('tr').find('.showVariation').data('screen-index')); // Capture the screen index
            });

            var query = selectedImages.length > 0 ? '?selected=' + encodeURIComponent(selectedImages.join(';')) : '';
            query += screenIndices.length > 0 ? '&indices=' + encodeURIComponent(screenIndices.join(';')) : '';

            window.location.href = '/download-zip' + query;
        }

        $('#download').click(downloadZip);
    });

    function backToIndex() {
        window.location.href = '/';
    }

    $('#backToIndex').click(backToIndex);
});
