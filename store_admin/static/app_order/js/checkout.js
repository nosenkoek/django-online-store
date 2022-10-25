let button=document.getElementById('button_next')
button.addEventListener('click', function (){
  let text_inputs=document.querySelectorAll('.form-input, .form-textarea, .radio_select:checked')
  text_inputs.forEach(function (element) {
    let field = document.querySelector(`.${element.name}`)
    if(field !== null) {
      field.innerHTML = element.value
    }
    })
})


