function showFaceID(result = null, function_name = null) {
  const overlay = document.getElementById('faceid-overlay');
  const circle = document.getElementById('faceid-circle');
  const tick = document.getElementById('faceid-tick');
  const text = document.getElementById('faceid-text');

  overlay.style.visibility = 'visible';
  circle.classList.add('show');

  if (result === null) {
    return;
  }

  setTimeout(() => {
    if (result) {
      tick.classList.add('show');
      text.textContent = "SUCCESS";
      text.classList.add('show');
    } else {
      circle.classList.add('faceid-fail');
      text.textContent = "FAIL";
      text.classList.add('show');
    }
  }, 1500);

  setTimeout(() => {
    overlay.style.visibility = 'hidden';
    circle.className = 'faceid-circle';
    tick.className = 'faceid-tick';
    text.className = 'faceid-text';
    text.textContent = '';
    if (function_name) {
      window.location.href = function_name;
    } else if (result === false) {
      window.location.href = '/dashboard';
    }

  }, 2000);

}