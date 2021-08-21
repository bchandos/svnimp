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
  // When a checkbox is changed, show/hide the side modal and add the
  // checked paths to it.
  const sideModal = document.getElementById('side-modal');
  const pathContainer = document.getElementById('side-modal-paths');
  const ckdBoxes = document.querySelectorAll('.path-check:checked');
  // Display or hide the bottom modal panel
  if (ckdBoxes.length) {
    sideModal.style.right = 0;
    const pathArray = Array.from(ckdBoxes).map(
        c => decodeURIComponent(c.dataset.path)
      );
      pathContainer.innerHTML = ''
    for (let p of pathArray) {
      pathContainer.innerHTML += `<div class="path-flex-item">${p}</div>`
    }
    setModalButtonState(ckdBoxes);
  } else {
    sideModal.style.right = '-31em';
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
  const data = getSelectedPaths();
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
  // console.log(json);
  if (json.status === 'ok') {
    // Uncheck all the boxes
    window.location.reload();
  } else {
    console.log('adding failed!');
  }
}

const clAction = async (e) => {
  // Add or remove some paths to a new or existing changelist
  const action = e.target.dataset.action;
  let clName = '';
  if (action === 'add') {
    clName = document.getElementById('changelist-name').value;
  }
  const repo = e.target.dataset.repoId;
  const url = `/changelist/${repo}/${action}`;
  const paths = getSelectedPaths();
  const response = await fetch(
    url,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ paths, clName })
    }
  );
  const json = await response.json();
  // console.log(json);
  if (json.status === 'ok') {
    // Uncheck all the boxes
    window.location.reload();
  } else {
    console.log('adding failed!');
  }
}

const clNameChange = (e) => {
  console.log(e.target.value);
  if (e.target.value !== '') {
    document.getElementById('side-modal-add-cl-button').disabled = false;
  } else {
    document.getElementById('side-modal-add-cl-button').disabled = true;
  }
}

const commit = async (e) => {
  const repo = e.target.dataset.repoId;
  const commitMessage = document.getElementById('commit-message').value;
  if (commitMessage) {
    const url = `/commit/${repo}`;
    const paths = getSelectedPaths();
    const response = await fetch(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ paths, commitMessage })
      }
    );
    const json = await response.json();
    // console.log(json);
    if (json.status === 'ok') {
      // Uncheck all the boxes
      window.location.reload();
    } else {
      console.log('Commit failed!');
    }
  } else {
    console.log('Must provide commit message!')
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

document.getElementById('side-modal-add-button').addEventListener('click', addPaths);
document.getElementById('side-modal-add-cl-button').addEventListener('click', clAction);
document.getElementById('side-modal-rm-cl-button').addEventListener('click', clAction);
document.getElementById('changelist-name').addEventListener('change', clNameChange);
document.getElementById('changelist-name').addEventListener('keyup', clNameChange);
document.getElementById('side-modal-ci-button').addEventListener('click', commit);

document.getElementById('repo-add').addEventListener('click', (e) => {
  document.getElementById('center-modal').style.display = 'block';
});

document.getElementById('close-center-modal').addEventListener('click', (e) => {
  document.getElementById('center-modal').style.display = 'none';
})

// End Attaching Event Listeners

// Utility functions

const getSelectedPaths = () => {
  const ckdBoxes = Array.from(document.querySelectorAll('.path-check:checked'));
  return ckdBoxes.map(c => c.dataset.path);
}

const hideElems = (...arguments) => {
  for (let elem of arguments) {
    elem.classList.add('w3-hide');
  }
}

const showElems = (...arguments) => {
  for (let elem of arguments) {
    elem.classList.remove('w3-hide');
  }
}

const setModalButtonState = (ckdBoxes) => {
  // Examining the types of boxes that are checked, show/hide modal buttons
  const boxArr = Array.from(ckdBoxes);
  
  const addBtn = document.getElementById('side-modal-add-button');
  const addClBtn = document.getElementById('side-modal-add-cl-button');
  const addClName = document.getElementById('changelist-name');
  const rmClBtn = document.getElementById('side-modal-rm-cl-button');
  const ciBtn = document.getElementById('side-modal-ci-button');
  const ciMsg = document.getElementById('commit-message');
  
  if (boxArr.every(c => c.dataset.versioned==='false')) {
    // Hide everything but the Add button
    showElems(addBtn);
    hideElems(addClBtn, addClName, rmClBtn, ciBtn, ciMsg);
  } else {
    hideElems(addBtn);
  }
  
  if (boxArr.some(c => !c.dataset.changelist) && boxArr.every(c => c.dataset.versioned==='true')) {
    showElems(addClBtn, addClName, ciBtn, ciMsg);
    hideElems(rmClBtn, addBtn);
  }
  if (boxArr.every(c => c.dataset.changelist)) {
    hideElems(addClBtn, addClName, addBtn);
    showElems(rmClBtn, ciBtn, ciMsg);
  }
}

const addOptionsToClDatalist = () => {
  // Add any existing changelist names to the datalist under the changelist name input
  // Done via Javascript because the input and datalist element are in the base template
  // which either can't access the variables passed into the inner template (untested)
  // or because the data structure is too annoying to deal with
  const dl = document.querySelector('datalist#changelists');
  for (let n of Array.from(document.querySelectorAll('h2.cl-name'))) {
    const opt = document.createElement('option');
    opt.value = n.innerHTML;
    dl.appendChild(opt);
  }
}
addOptionsToClDatalist();


// Drag and drop

var dragAndDrop = {
  draggedFrom: null,
  draggedTo: null,
  isDragging: false,
  droppedOn: null,
}

const dragStart = (e) => {
  const initialCl = e.currentTarget.dataset.changelist;
  dragAndDrop.draggedFrom = initialCl;
  dragAndDrop.isDragging = true;
  e.dataTransfer.setData("text/html", ''); // Firefox?
}

const dragOver = (e) => {
  e.preventDefault();
  const clContainer = e.currentTarget.closest('ul.w3-ul');
  clContainer.classList.add('dragged-over');
  dragAndDrop.draggedTo = e.currentTarget.dataset.changelist;
}

const dragLeave = (e) => {
  const clContainer = e.currentTarget.closest('ul.w3-ul');
  clContainer.classList.remove('dragged-over');
  dragAndDrop.draggedTo = null;
}

const drop = (e) => {
  // Only process change if dropped on a valid target
  if (e.currentTarget.classList.contains('draggable-row')) {
      const clContainer = e.currentTarget.closest('ul.w3-ul');
      clContainer.classList.remove('dragged-over');
      dragAndDrop.droppedOn = e.currentTarget;
  }
}

const dragEnd = async (e) => {
  if (dragAndDrop.droppedOn && dragAndDrop.droppedOn != e.currentTarget && dragAndDrop.draggedTo != e.currentTarget.dataset.changelist) {
    const ck = e.currentTarget.querySelector('input.path-check');
    const repo = ck.dataset.repo;
    const url = `/changelist/${repo}/add`;
    const paths = [ck.dataset.path];
    const clName = dragAndDrop.draggedTo;
    const response = await fetch(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ paths, clName })
      }
    );
    const json = await response.json();
    if (json.status === 'ok') {
      window.location.reload();
    } else {
      console.log('adding failed!');
    }
  }
  dragAndDrop.draggedTo = null;
  dragAndDrop.isDragging = false;
  dragAndDrop.droppedOn = null;
  dragAndDrop.draggedFrom = null;
}

for (let row of document.querySelectorAll('li.draggable-row')) {
  row.addEventListener('dragstart', dragStart);
  row.addEventListener('dragover', dragOver);
  row.addEventListener('dragleave', dragLeave);
  row.addEventListener('drop', drop);
  row.addEventListener('dragend', dragEnd);
}