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

$("#error-alert").hide();
$("#put-btn").click(function showAlert() {
    $("#put-alert").fadeTo(5000, 500).slideUp(500, function(){
   $("#put-alert").slideUp(500);
    });   
});

        

