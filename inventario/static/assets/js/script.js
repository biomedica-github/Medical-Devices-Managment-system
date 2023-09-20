jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});

 const delBtn = document.getElementById('del-btn');

$("#delete-alert").hide();
$("#del-btn").click(function showAlert() {
    $("#error-alert").show();
    $("#delete-alert").fadeTo(5000, 500).slideUp(500, function(){
   $("#delete-alert").slideUp(500);
    });   
});