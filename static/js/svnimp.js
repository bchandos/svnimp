const getDiff = async (e) => {
  const btnEl = e.currentTarget;
  const path = btnEl.dataset.path;
  const repo = btnEl.dataset.repo;
  const state = btnEl.dataset.state;
  const hiddenEl = btnEl.nextElementSibling;
  if (state==='closed') {
    if (hiddenEl.innerHTML === '') {
      hiddenEl.innerHTML = await diffRequest(repo, path);
    }
    hiddenEl.classList.remove('w3-hide');
    btnEl.innerHTML = '&#9650;';
    btnEl.dataset.state = 'open';
  } else {
    btnEl.innerHTML = '&#9660;';
    hiddenEl.classList.add('w3-hide');
    btnEl.dataset.state = 'closed';
  }
}

const reloadDiff = async (e) => {
  const btnEl = e.target.closest('.diff-reload-btn');
  if (btnEl instanceof HTMLButtonElement) {
    const container = btnEl.closest('.diff-block');
    container.classList.add('w3-opacity', 'w3-grayscale');
    const path = btnEl.dataset.path;
    const repo = btnEl.dataset.repo;
    // container.innerHTML = '';
    container.innerHTML = await diffRequest(repo, path);
    container.classList.remove('w3-opacity', 'w3-grayscale');
  }
}

const diffRequest = async (repo, path) => {
  const url = `/diff/${repo}?path=${path}`;
    const response = await fetch(
      url
    );
    const text = await response.text();
    return text
}

const addPathToModal = (e) => {
  const bottomModal = document.getElementById('bottom-modal');
  const allCks = document.querySelectorAll('.path-check');
  // Display or hide the bottom modal panel
  if (Array.from(allCks).some(c => c.checked)) {
    bottomModal.style.bottom = 0;
    bottomModal.innerHTML = Array.from(allCks).filter(
        c => c.checked
      ).map(
        c => decodeURIComponent(c.dataset.path)
      ).join(', ');
  } else {
    bottomModal.style.bottom = '-5rem';
    bottomModal.innerHTML = '';
  }

}

for (let btn of document.querySelectorAll('.diff-button')) {
  btn.addEventListener('click', getDiff);
}

for (let block of document.querySelectorAll('.diff-block')) {
  block.addEventListener('click', reloadDiff);
}

for (let ck of document.querySelectorAll('.path-check')) {
  ck.addEventListener('change', addPathToModal);
}
