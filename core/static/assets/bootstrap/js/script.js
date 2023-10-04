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
      const url = baseURL + 'auth/jwt/create/'
    $.ajax({
        type: method,
        url: url,
        data: formData,
        success: function(response) {
          if ($('#formCheck-1')[0].checked){
            const expirationDate = new Date();
            expirationDate.setDate(expirationDate.getDate() + 30);
            document.cookie = `Token=${response['access']}; rememberMeCookie=value; expires=${expirationDate.toUTCString()}; path=/`;
            window.location.href = baseURL + 'area/general/';
          }
          else {
            document.cookie = `Token=${response['access']}; sessionCookie=value; path=/`;
          }

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
