$("#loader").hide()

$("#entrar").on('click', () => {
    $("#loader").show()
})

$(document).ready(function() {
    $('#login').submit(function(e) {
      e.preventDefault(); 
      

      console.log('hey que pasa chavale')
      const formData = $(this).serialize();
      const method = 'POST'; 
      const parsedUrl = new URL(window.location.href);
      const baseURL = `${parsedUrl.protocol}//${parsedUrl.hostname}${parsedUrl.port ? `:${parsedUrl.port}` : ''}/`;
      const url = baseURL + 'login/auth'
    $.ajax({
        type: method,
        url: url,
        data: formData,
        success: function(response) {
          window.location.href = baseURL + 'area/general/';
          console.log('POST request succesful');

        },
        error: function(error) {
          location.reload()
          localStorage.setItem('displayError', 'true');
          console.error('POST request failed');
        }
      });
    });
})
