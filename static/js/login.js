

document.getElementById('loginBtn').addEventListener('click', function(event) {
    event.preventDefault(); 


    document.getElementById('emailError').innerText = '';
    document.getElementById('emailInput').classList.remove('invalid');


    var emailInput = document.getElementById('emailInput');
    if (emailInput.validity.typeMismatch) {
        document.getElementById('emailError').innerText = 'Пожалуйста, введите корректный адрес электронной почты.';
        document.getElementById('emailInput').classList.add('invalid');
    }
});

  

    document.querySelectorAll('.smooth-scroll').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
          e.preventDefault();
      
          document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
          });
        });
      });



      //лк