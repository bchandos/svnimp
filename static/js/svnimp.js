// Event Handlers

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
  const pathContainer = document.getElementById('bottom-modal-paths');
  const allCks = document.querySelectorAll('.path-check');
  // Display or hide the bottom modal panel
  if (Array.from(allCks).some(c => c.checked)) {
    bottomModal.style.bottom = 0;
    const pathArray = Array.from(allCks).filter(
        c => c.checked
      ).map(
        c => decodeURIComponent(c.dataset.path)
      );
      pathContainer.innerHTML = ''
    for (let p of pathArray) {
      pathContainer.innerHTML += `<div class="path-flex-item">${p}</div>`
    }
  } else {
    bottomModal.style.bottom = '-5rem';
    pathContainer.innerHTML = '';
  }
}

const toggleVersioned = (e) => {
  // Disable or enable checkboxes based on their version status
  // i.e. unversioned files cannot be selected with versioned files
  // and vice-versa
  const vPaths = Array.from(document.querySelectorAll('.path-check[data-versioned="true"]'));
  const uvPaths = Array.from(document.querySelectorAll('.path-check[data-versioned="false"]'));
  if (vPaths.some(p => p.checked)) {
    for (let p of uvPaths) {
      p.checked = false;
      p.disabled = true;
    }
  } else if (uvPaths.some(p => p.checked)) {
    for (let p of vPaths) {
      p.checked = false;
      p.disabled = true;
    } 
  } else {
    for (let p of [...vPaths, ...uvPaths]) {
      p.disabled = false;
    }
  }
}

const addPaths = async (e) => {
  const repo = e.target.dataset.repoId;
  const url = `/add-paths/${repo}`;
  const ckdBoxes = Array.from(document.querySelectorAll('.path-check:checked'));
  const data = ckdBoxes.map(c => c.dataset.path);
  const response = await fetch(
    url,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({paths: data})
    }
  );
  const json = await response.json();
  console.log(json);
  if (json.status === 'ok') {
    // Uncheck all the boxes
    window.reload();
  } else {
    console.log('adding failed!');
  }
}

// End Event Handlers

// Attach Event Listeners

for (let btn of document.querySelectorAll('.diff-button')) {
  btn.addEventListener('click', getDiff);
}

for (let block of document.querySelectorAll('.diff-block')) {
  block.addEventListener('click', reloadDiff);
}

for (let ck of document.querySelectorAll('.path-check')) {
  ck.addEventListener('change', addPathToModal);
  ck.addEventListener('change', toggleVersioned);
}

document.getElementById('bottom-modal-add-button').addEventListener('click', addPaths);
