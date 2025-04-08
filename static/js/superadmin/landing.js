let currentStep = 1;
let emailAvailable = true;
let shopNameAvailable = true;

function showStep(step) {
  document.querySelectorAll('.modal-body > div').forEach(div => div.classList.add('d-none'));
  const current = document.getElementById('step' + step);
  if (current) current.classList.remove('d-none');

  document.getElementById('prevBtn').style.display = step === 1 ? 'none' : 'inline-block';
  document.getElementById('nextBtn').style.display = step === 3 ? 'none' : 'inline-block';
}

function nextStep() {
  if (validateStep(currentStep)) {
    if (currentStep < 3) currentStep++;
    showStep(currentStep);
  }
}

function prevStep() {
  if (currentStep > 1) currentStep--;
  showStep(currentStep);
}

function setInvalid(id, message) {
  const el = document.getElementById(id);
  el.classList.add('is-invalid');
  const feedback = el.nextElementSibling;
  if (feedback) {
    feedback.classList.remove('d-none');
    feedback.textContent = message;
  }
}

function clearInvalid(id) {
  const el = document.getElementById(id);
  el.classList.remove('is-invalid');
  const feedback = el.nextElementSibling;
  if (feedback) {
    feedback.classList.add('d-none');
  }
}

function validateStep(step) {
  if (step === 1) {
    const shop_name = document.getElementById('shop_name').value.trim();
    if (!shop_name || !shopNameAvailable) {
      document.getElementById('shopNameHelp').classList.remove('d-none');
      return false;
    }
    document.getElementById('shopNameHelp').classList.add('d-none');
    return true;
  }

  if (step === 2) {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!email || !emailAvailable) {
      setInvalid('email', 'Email is required or already used');
      return false;
    } else {
      clearInvalid('email');
    }

    if (!password || password !== confirmPassword) {
      document.getElementById('passwordMismatch').classList.remove('d-none');
      return false;
    } else {
      document.getElementById('passwordMismatch').classList.add('d-none');
    }

    return true;
  }

  return true;
}

function updateNextButtonVisibility() {
  const nextBtn = document.getElementById('nextBtn');
  if (!emailAvailable || !shopNameAvailable) {
    nextBtn.style.display = 'none';
  } else {
    if (currentStep < 3) {
      nextBtn.style.display = 'inline-block';
    }
  }
}

function debounce(func, delay) {
  let timeout;
  return function () {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, arguments), delay);
  };
}

const checkEmail = debounce(function () {
  const email = $('#email').val().trim().toLowerCase();
  $('#email').val(email);
  if (!email) return;

  $.get('/api/check_email', { email }, function (response) {
    if (response.status === 'exists') {
      emailAvailable = false;
      updateNextButtonVisibility();
      Swal.fire({
        icon: 'error',
        title: 'Email already registered',
        text: 'Please use another email or log in.'
      });
      $('#email').addClass('is-invalid').next('.invalid-feedback')
        .removeClass('d-none').text('Email already registered.');
    } else {
      emailAvailable = true;
      updateNextButtonVisibility();
      $('#email').removeClass('is-invalid').next('.invalid-feedback').addClass('d-none');
    }
  }).fail(() => {
    Swal.fire({
      icon: 'error',
      title: 'Connection error',
      text: 'Could not verify email. Please try again later.'
    });
  });
}, 600);

const checkShopName = debounce(function () {
  const shopName = $('#shop_name').val().trim().toLowerCase().replace(/\s+/g, '-');
  $('#shop_name').val(shopName);
  if (!shopName) return;

  $.get('/api/check_shopname', { shop_name: shopName }, function (response) {
    if (response.status === 'exists') {
      shopNameAvailable = false;
      updateNextButtonVisibility();
      Swal.fire({
        icon: 'error',
        title: 'Store name already in use',
        text: 'Choose a different name for your store.'
      });
      $('#shop_name').addClass('is-invalid').next('.invalid-feedback')
        .removeClass('d-none').text('Store name not available.');
    } else {
      shopNameAvailable = true;
      updateNextButtonVisibility();
      $('#shop_name').removeClass('is-invalid').next('.invalid-feedback').addClass('d-none');
    }
  }).fail(() => {
    Swal.fire({
      icon: 'error',
      title: 'Connection error',
      text: 'Could not verify store name. Try again later.'
    });
  });
}, 600);

document.addEventListener('DOMContentLoaded', function () {
  showStep(currentStep);

  document.getElementById('shop_name').addEventListener('input', function () {
    const formatted = this.value.toLowerCase().replace(/\s+/g, '-');
    this.value = formatted;
  });

  document.getElementById('email').addEventListener('input', function () {
    this.value = this.value.toLowerCase().trim();
  });

  document.getElementById('confirmPassword').addEventListener('input', function () {
    const password = document.getElementById('password').value;
    const confirm = this.value;
    const mismatchWarning = document.getElementById('passwordMismatch');

    if (password && confirm && password !== confirm) {
      mismatchWarning.classList.remove('d-none');
    } else {
      mismatchWarning.classList.add('d-none');
    }
  });

  $('#email').on('input', checkEmail);
  $('#shop_name').on('input', checkShopName);

  document.getElementById('password').addEventListener('input', updatePasswordStrength);
  
  // Inizializza AOS
  if (AOS) {
    AOS.init();
  }
});

function updatePasswordStrength() {
  const password = document.getElementById('password').value;
  const meterFill = document.getElementById('strength-meter-fill');
  const strengthText = document.getElementById('passwordStrengthText');

  let strength = 0;
  if (password.length > 6) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[@$!%*?&#]/.test(password)) strength++;

  const strengths = ['Low', 'Medium', 'Strong', 'Very Strong'];
  const colors = ['bg-danger', 'bg-warning', 'bg-info', 'bg-success'];
  let index = Math.min(strength, strengths.length - 1);

  if (meterFill) {
    meterFill.style.width = (strength * 25) + '%';
    meterFill.className = 'strength-meter-fill ' + colors[index];
  }

  if (strengthText) {
    strengthText.textContent = 'Degree of password security: ' + strengths[index];
  }
}

async function inviaDati() {
  const shopName = document.getElementById('shop_name').value.trim().toLowerCase();
  const selectedThemeOption = document.querySelector('input[name="themeOptions"]:checked')?.value;
  const email = document.getElementById('email').value.trim().toLowerCase();
  const password = document.getElementById('password').value;

  if (!shopName || !selectedThemeOption || !email || !password) {
    Swal.fire({
      icon: 'warning',
      title: 'Missing data',
      text: 'Please fill out all required fields.'
    });
    return;
  }

  const formData = new FormData();
  formData.append('shop_name', shopName);
  formData.append('themeOptions', selectedThemeOption);
  formData.append('email', email);
  formData.append('password', password);

  try {
    const response = await fetch('/api/create_shop', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Errore sconosciuto');
    }

    if (data.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Success',
        text: data.message
      });
      document.body.style.overflow = '';
      window.location.href = '/login';
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Oops',
        text: data.message
      });
    }

  } catch (error) {
    console.error('Errore:', error);
    Swal.fire({
      icon: 'error',
      title: 'Server error',
      text: 'An error occurred while creating the store: ' + error.message
    });
  }
}
