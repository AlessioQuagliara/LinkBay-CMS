
let currentStep = 1;
let shopNameAvailable = true;

function showStep(step) {
  document.querySelectorAll('.modal-body > div').forEach(div => div.classList.add('d-none'));
  const current = document.getElementById('step' + step);
  if (current) current.classList.remove('d-none');
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
  return true;
}

function debounce(func, delay) {
  let timeout;
  return function () {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, arguments), delay);
  };
}

const checkShopName = debounce(function () {
  const shopName = document.getElementById('shop_name').value.trim();
  if (!shopName) return;

  $.get('/api/check_shopname', { shop_name: shopName }, function (response) {
    if (response.status === 'exists') {
      shopNameAvailable = false;
      document.getElementById('shopNameHelp').classList.remove('d-none');
    } else {
      shopNameAvailable = true;
      document.getElementById('shopNameHelp').classList.add('d-none');
    }
  }).fail(() => {
    Swal.fire({
      icon: 'error',
      title: 'Errore di rete',
      text: 'Impossibile verificare il nome. Riprova più tardi.'
    });
  });
}, 600);

document.addEventListener('DOMContentLoaded', function () {
  showStep(currentStep);

  const shopNameInput = document.getElementById('shop_name');
  shopNameInput.addEventListener('input', function () {
    this.value = this.value
      .toLowerCase()
      .replace(/[^a-z0-9\-]/g, '')
      .replace(/\s+/g, '-');
  });

  $('#shop_name').on('input', checkShopName);
});

async function creaNegozioPerUtente() {
  const shopName = document.getElementById('shop_name').value.trim().toLowerCase();
  const shopType = document.getElementById('shop_type').value;

  if (!shopName || !shopType) {
    Swal.fire({
      icon: 'warning',
      title: 'Dati mancanti',
      text: 'Compila tutti i campi richiesti.'
    });
    return;
  }

  const formData = new FormData();
  formData.append('shop_name', shopName);
  formData.append('themeOptions', shopType);

  try {
    const response = await fetch('/api/create_shop_access', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.message || 'Errore sconosciuto');
    }

    await Swal.fire({
      icon: 'success',
      title: 'Negozio creato!',
      text: data.message
    });
    window.location.href = '/dashboard/stores';

  } catch (error) {
    console.error('Errore:', error);
    Swal.fire({
      icon: 'error',
      title: 'Errore server',
      text: 'Errore durante la creazione del negozio: ' + error.message
    });
  }
}

async function confirmDeleteShop(shopId) {
  const confirmed = await Swal.fire({
    title: 'Sei sicuro?',
    text: "Questa azione eliminerà definitivamente il negozio.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#aaa',
    confirmButtonText: 'Sì, elimina',
    cancelButtonText: 'Annulla'
  });

  if (confirmed.isConfirmed) {
    try {
      const response = await fetch('/api/delete_shop', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ shop_id: shopId })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        Swal.fire('Eliminato!', data.message, 'success').then(() => {
          window.location.reload();
        });
      } else {
        throw new Error(data.message || 'Errore durante l\'eliminazione.');
      }
    } catch (error) {
      Swal.fire('Errore', error.message, 'error');
    }
  }
}
