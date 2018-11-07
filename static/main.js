$(function() {
    // Global AJAX setup.
    $.ajaxSetup({
        contentType: "application/json; charset=utf-8"
    });

    // Library page.
    function deletePair(photo_id) {
        $.post('/delete-photo/' + photo_id, function () {
            $("#library-row-" + photo_id).remove();
        });
    };

    $('button.library-delete-pair').on('click', function() {
        let photo_id = parseInt($(this).data('photo-id'));
        deletePair(photo_id);
    });

    // Processing page.
    function replaceImage(results) {
        $(".processing .prcessing-loading-overlay").hide();
        $('#img-processing').attr("src", results);
        console.log("Finished replaceStatus");
        $('#process-form').append(
            '<div class="mt-3">'
            + '<a class="btn btn-secondary" href="' + results
            + '" download="' + results
            + '"><i class="fas fa-download"></i></a>'
            + '</div>'
        );
    }

    function processImage() {
        let photo_id = parseInt($(this).data('photo-id'));
        let data = {
            dataset_id: parseInt($("#process-select").val()),
        };
        $.post('/process/' + photo_id, JSON.stringify(data), replaceImage);
        $(".processing .prcessing-loading-overlay").show();
    }

    $('#process-button').on('click', processImage);


    // Training page.
    function trainDatasetCompleted(dataset_id) {
        $('#dataset-' + dataset_id + ' button').remove();
        $('#dataset-' + dataset_id).append("<span>Processing</span>");
    }

    function trainButtonClick(dataset_id) {
        $.post('/train-dataset/' + dataset_id, function () {
            trainDatasetCompleted(dataset_id);
        });
    }

    $('.train-button').on('click', function () {
        let dataset_id = $(this).data('dataset-id');
        trainButtonClick(dataset_id);
    });


    // Library page.
    $('.custom-file-input').on('change', function () {
        let filename = $(this).val().split('\\').pop();
        $(this).next().html(filename);
    });
});
