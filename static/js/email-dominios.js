(function () {
  var dominiosPermitidos = new Set([
    'gmail.com', 'googlemail.com', 'outlook.com', 'hotmail.com', 'live.com',
    'msn.com', 'yahoo.com', 'yahoo.es', 'icloud.com', 'me.com', 'mac.com',
    'proton.me', 'protonmail.com', 'aol.com', 'zoho.com', 'gmx.com',
    'gmx.net', 'mail.com', 'yandex.com', 'yandex.ru', 'fastmail.com',
    'tutanota.com', 'tuta.com', 'hey.com', 'inbox.com'
  ]);

  function validarEmailDominioPermitido(email) {
    email = String(email || '').trim();
    if (!email) {
      input.classList.remove('is-invalid', 'is-valid');
      return true;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return false;
    if (email.indexOf('..') !== -1) return false;

    var partes = email.split('@');
    if (partes.length !== 2) return false;

    return dominiosPermitidos.has(partes[1].toLowerCase());
  }

  function mensajeEmail(email) {
    email = String(email || '').trim();
    if (!email) return '';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.indexOf('..') !== -1) {
      return 'Ingresa un correo valido.';
    }

    var dominio = email.split('@').pop().toLowerCase();
    if (!dominiosPermitidos.has(dominio)) {
      return 'Usa un correo con dominio permitido.';
    }

    return '';
  }

  function buscarMensaje(input) {
    var candidates = [
      'msg_' + input.id.replace(/^id_/, ''),
      'msg-' + input.id.replace(/^.*email.*$/i, 'email'),
      input.id.replace(/input/i, 'error')
    ];

    for (var i = 0; i < candidates.length; i++) {
      var el = document.getElementById(candidates[i]);
      if (el) return el;
    }

    var group = input.closest('.form-group, .field-group, .input-group, .form-field');
    if (group) {
      var msg = group.querySelector('.field-msg, .field-error, .field-help, small');
      if (msg) return msg;
    }

    return null;
  }

  function aplicarEstado(input) {
    var email = input.value.trim();
    var error = mensajeEmail(email);
    input.setCustomValidity(error);

    if (!email) return true;

    input.classList.toggle('is-invalid', !!error);
    input.classList.toggle('is-valid', !error);

    var msg = buscarMensaje(input);
    if (msg && error) {
      var span = msg.querySelector('span');
      if (span) span.textContent = error;
      else msg.textContent = error;
      msg.style.color = '#B3261E';
    }

    return !error;
  }

  function inicializar() {
    var inputs = Array.prototype.slice.call(document.querySelectorAll('input[type="email"], input[name="email"]'));

    inputs.forEach(function (input) {
      input.addEventListener('input', function () { aplicarEstado(input); });
      input.addEventListener('blur', function () { aplicarEstado(input); });
      if (input.value) aplicarEstado(input);
    });

    document.addEventListener('submit', function (event) {
      var form = event.target;
      if (!form || !form.querySelectorAll) return;

      var emails = Array.prototype.slice.call(form.querySelectorAll('input[type="email"], input[name="email"]'));
      var invalido = emails.some(function (input) { return !aplicarEstado(input); });

      if (invalido) {
        event.preventDefault();
        event.stopPropagation();
        var primero = emails.find(function (input) { return !validarEmailDominioPermitido(input.value); });
        if (primero) primero.focus();
      }
    }, true);
  }

  window.dominiosEmailPermitidos = dominiosPermitidos;
  window.validarEmailDominioPermitido = validarEmailDominioPermitido;
  window.mensajeEmailDominioPermitido = mensajeEmail;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }
})();
