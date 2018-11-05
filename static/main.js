$(function() {
    // Global AJAX setup.
    $.ajaxSetup({
        contentType: "application/json; charset=utf-8"
    });


    // Processing page.
    function replaceImage(results) {
        $(".loader").remove();
        $('#img-processing').attr("src", results);
        console.log("Finished replaceStatus");
        $('#process-form').append(
            '<a href="' + results
            + '" download="' + results
            + '">Download</a>'
        );
    }

    function processImage() {
        let photo_id = parseInt($(this).data('photo-id'));
        let data = {
            dataset_id: parseInt($("#process-select").val()),
        };
        $.post('/process/' + photo_id, JSON.stringify(data), replaceImage);
        console.log("Finished sending AJAX");
        var div = document.createElement("div");
        div.setAttribute("class", "loader");
        document.body.appendChild(div);
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
});
