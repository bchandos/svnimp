// Add a universal backdrop to the body the will only be displayed 
// when a popper is open and clicking on it will close all poppers

// TODO: refine positioning so it doesn't render outside the viewport

const popperBackDrop = document.createElement('div');
popperBackDrop.id = 'popper-backdrop';
document.body.appendChild(popperBackDrop);

const popperFit = (desiredPosition, popper, pBox) => {
    let pos, pTop, pLeft;
    const btnHeight = pBox.clientHeight;
    const btnWidth = pBox.clientWidth;
    const popperHeight = popper.clientHeight;
    const popperWidth = popper.clientWidth;
    switch (desiredPosition) {
        case 'bottom':
            pTop = btnHeight + 8;
            pLeft = -(popperWidth/2) + (btnWidth/2);
            pos = 'bottom';
            break;
        case 'top':
            pTop = -popperHeight - 8;
            pLeft = -(popperWidth/2) + (btnWidth/2);
            pos = 'top';
            break;
        case 'left':
            pTop = -(popperHeight/2) + 8;
            pLeft = -popperWidth - 8;
            pos = 'left';
            break;
        case 'right':
            pTop = -(popperHeight/2) + 8;
            pLeft = btnWidth + 8;
            pos = 'right';
            break;
    }
    return { pos, pTop, pLeft }
}

const createPopper = (elem) => {
    const trigger = elem.dataset.triggerText || elem.querySelectorAll('span.popper-trigger').innerHTML;
    const triggerBtn = document.createElement('button');
    triggerBtn.innerText = trigger;
    triggerBtn.type = 'button';
    triggerBtn.classList.add('popper-button');
    triggerBtn.addEventListener('click', openPopper);
    const popper = document.createElement('div');
    popper.classList.add('popper');
    popper.dataset.open = 'false';
    popper.dataset.position = elem.dataset.position || 'left';
    popper.innerHTML = elem.innerHTML;
    
    const popperBox = document.createElement('span');
    popperBox.classList = elem.classList;
    popperBox.classList.add('popper-box');
    popperBox.appendChild(triggerBtn);
    popperBox.appendChild(popper);
    elem.replaceWith(popperBox);
}


const createPoppers = () => {
    const allDialogElems = document.querySelectorAll('popper');
    for (let elem of allDialogElems) {
        createPopper(elem);
    }
}

const zPopBack = (e) => {
    e.target.style.zIndex = '-1';
    e.target.style = null;
}

const openPopper = (e) => {
    const popper = e.currentTarget.nextSibling;
    const pBox = e.currentTarget;
    popper.style.display = 'block';
    console.log(popper.style);
    let fit = popperFit(popper.dataset.position, popper, pBox);
    console.log(popper.style);
    popper.style.top = `${fit.pTop}px`;
    popper.style.left = `${fit.pLeft}px`;
    const pRect = popper.getBoundingClientRect();
    // If the popper is going to render offscreen, find another location for it.
    // This will only handle a single case, and should handle all cases...
    if (pRect.x < 0) {
        popper.style.top, popper.style.left = null;
        fit = popperFit('right', popper, pBox);
        popper.style.top = `${fit.pTop}px`;
        popper.style.left = `${fit.pLeft}px`;
    } else if ((pRect.x + pRect.width) > document.documentElement.clientWidth) {
        popper.style.top, popper.style.left = null;
        fit = popperFit('left', popper, pBox);
        popper.style.top = `${fit.pTop}px`;
        popper.style.left = `${fit.pLeft}px`;
    } else if (pRect.y < 0) {
        popper.style.top, popper.style.left = null;
        fit = popperFit('bottom', popper, pBox);
        popper.style.top = `${fit.pTop}px`;
        popper.style.left = `${fit.pLeft}px`;
    } else if ((pRect.y + pRect.height) > document.documentElement.clientHeight) {
        popper.style.top, popper.style.left = null;
        fit = popperFit('top', popper, pBox);
        popper.style.top = `${fit.pTop}px`;
        popper.style.left = `${fit.pLeft}px`;
    }
    popper.dataset.position = fit.pos;
    popper.classList.add(`pos-${fit.pos}`);
    popper.removeEventListener('transitionend', zPopBack);
    popper.style.opacity = '1';
    popper.style.zIndex = '10';
    popper.dataset.open = 'true';
    
    popperBackDrop.style.opacity = '1';
    popperBackDrop.style.zIndex = '5';
    popperBackDrop.removeEventListener('transitionend', zPopBack);
}


const closePoppers = () => {
    const openPoppers = document.querySelectorAll('div.popper[data-open="true"]');
    for (let p of openPoppers) {
        p.addEventListener('transitionend', zPopBack);
        p.style.opacity = '0';
        p.dataset.open = 'false';
    }
    popperBackDrop.addEventListener('transitionend', zPopBack);
    popperBackDrop.style.opacity = '0';
}

popperBackDrop.addEventListener('click', closePoppers);

createPoppers();