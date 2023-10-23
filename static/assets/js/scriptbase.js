$(document).ready(function() {
    $('#logout-btn').on('click',function(e) {
      e.preventDefault(); 
      
      const url = baseURL + 'login/logout/'
    $.ajax({
        type: method,
        url: url,
        data: '',
        success: function(response) {
          console.log('POST request succesful');

        },
        error: function(error) {
          console.error('POST request failed');
        }
      });
    });
})