const setToast = (msg) => {
  const toastContainer = document.getElementById('toast-message');
  toastContainer.querySelector('#toast-contents').innerHTML = msg;
  toastContainer.style.top = '0';
}

const hideToast = () => {
  const toastContainer = document.getElementById('toast-message');
  toastContainer.querySelector('#toast-contents').innerHTML = '';
  toastContainer.style.top = '-10rem';
}

const setSessionMsg = async (msg) => {
  const response = await fetch(
    '/set-session-msg',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ msg })
    }
  )
  return response
}

const clearSessionMsg = () => {
  setSessionMsg('')
}

document.getElementById('close-toast').addEventListener('click', hideToast);