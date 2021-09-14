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

document.getElementById('close-toast').addEventListener('click', hideToast);