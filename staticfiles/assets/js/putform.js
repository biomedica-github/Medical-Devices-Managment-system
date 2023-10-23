$(document).ready(function () {
    $("#put-form").submit(function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Serialize the form data
        var formData = $(this).serialize();

        // Send the PUT request
        $.ajax({
            url: $(this).attr("action"),
            type: "PUT",
            data: formData,
            success: function (response) {
                // Handle the success response
                location.reload()
                
                
                localStorage.setItem('displayAlert', 'true')
                console.log("PUT request successful");
                // You can update the page or display a success message here
            },
            error: function (error) {
                // Handle the error response 
                location.reload()
                localStorage.setItem('displayError', 'true')
                console.error("PUT request failed");
                // You can display an error message here
            }
        });
    });
});
