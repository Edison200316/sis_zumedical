(function () {
  function esCedulaEcuatorianaValida(cedula) {
    cedula = String(cedula || '').trim();

    if (!/^\d{10}$/.test(cedula)) return false;
    if (/^(\d)\1{9}$/.test(cedula)) return false;

    var codigoProvincia = parseInt(cedula.substring(0, 2), 10);
    if (!(codigoProvincia >= 1 && codigoProvincia <= 24)) return false;

    var tercerDigito = parseInt(cedula.charAt(2), 10);
    if (tercerDigito >= 6) return false;

    var coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2];
    var suma = 0;

    for (var i = 0; i < 9; i++) {
      var resultado = parseInt(cedula.charAt(i), 10) * coeficientes[i];
      if (resultado >= 10) resultado -= 9;
      suma += resultado;
    }

    var residuo = suma % 10;
    var verificador = residuo === 0 ? 0 : 10 - residuo;
    return verificador === parseInt(cedula.charAt(9), 10);
  }

  function buscarMensaje(input) {
    var byId = document.getElementById('msg_' + input.id.replace(/^id_/, ''));
    if (byId) return byId;

    var group = input.closest('.form-group, .field-group, .input-group, .form-field');
    if (group) {
      var msg = group.querySelector('.field-msg, .field-error, .field-help, small');
      if (msg) return msg;
    }

    var creado = document.createElement('small');
    creado.className = 'field-msg cedula-validacion-msg';
    creado.style.display = 'block';
    creado.style.marginTop = '.45rem';
    creado.style.fontSize = '.82rem';
    input.insertAdjacentElement('afterend', creado);
    return creado;
  }

  function setEstado(input, estado, mensaje) {
    var msg = buscarMensaje(input);
    input.classList.remove('is-valid', 'is-invalid');
    input.setCustomValidity('');

    if (!mensaje) {
      if (msg) msg.textContent = '';
      return;
    }

    if (estado === 'ok') {
      input.classList.add('is-valid');
      if (msg) {
        msg.textContent = mensaje;
        msg.style.color = '#007E4A';
      }
      return;
    }

    input.classList.add('is-invalid');
    input.setCustomValidity(mensaje);
    if (msg) {
      msg.textContent = mensaje;
      msg.style.color = '#B3261E';
    }
  }

  function validarInputCedula(input, mostrarCompleto) {
    input.value = input.value.replace(/\D/g, '').slice(0, 10);
    var cedula = input.value;

    if (!cedula) {
      setEstado(input, null, '');
      return !input.required;
    }

    if (cedula.length < 10) {
      setEstado(input, 'error', mostrarCompleto ? 'La cedula debe tener 10 digitos.' : '');
      return false;
    }

    if (!esCedulaEcuatorianaValida(cedula)) {
      setEstado(input, 'error', 'Ingresa una cedula ecuatoriana real.');
      return false;
    }

    setEstado(input, 'ok', 'Cedula valida');
    return true;
  }

  function inicializar() {
    var inputs = Array.prototype.slice.call(document.querySelectorAll('input[name="cedula"]'));

    inputs.forEach(function (input) {
      input.setAttribute('maxlength', '10');
      input.setAttribute('minlength', '10');
      input.setAttribute('inputmode', 'numeric');
      input.setAttribute('autocomplete', input.getAttribute('autocomplete') || 'off');

      input.addEventListener('input', function () {
        validarInputCedula(input, false);
      });
      input.addEventListener('blur', function () {
        validarInputCedula(input, true);
      });

      if (input.value) validarInputCedula(input, false);
    });

    document.addEventListener('submit', function (event) {
      var form = event.target;
      if (!form || !form.querySelectorAll) return;

      var cedulas = Array.prototype.slice.call(form.querySelectorAll('input[name="cedula"]'));
      var invalida = cedulas.some(function (input) {
        return !validarInputCedula(input, true);
      });

      if (invalida) {
        event.preventDefault();
        event.stopPropagation();
        var primera = cedulas.find(function (input) { return !esCedulaEcuatorianaValida(input.value); });
        if (primera) primera.focus();
      }
    }, true);
  }

  window.esCedulaEcuatorianaValida = esCedulaEcuatorianaValida;
  window.validarInputCedulaEcuatoriana = validarInputCedula;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }
})();
