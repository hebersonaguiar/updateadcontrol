function toggleInputAction(element, className) {
  for (
    var inputAction = element;
    !inputAction.classList.contains(className);
    inputAction = inputAction.parentNode
  );

  var icon = element.getElementsByClassName('fas')[0]

  if (icon.classList.contains('fa-eye')) {
    inputAction
      .querySelector("input[type='password'")
      .setAttribute('type', 'text')
    icon.classList.remove('fa-eye')
    icon.classList.add('fa-eye-slash')
  } else if (icon.classList.contains('fa-eye-slash')) {
    inputAction
      .querySelector("input[type='text'")
      .setAttribute('type', 'password')
    icon.classList.remove('fa-eye-slash')
    icon.classList.add('fa-eye')
  }
}
