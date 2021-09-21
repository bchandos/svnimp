class PopperBox extends HTMLElement {
    constructor() {
        super();
        const shadow = this.attachShadow({mode: 'open'}); // sets and returns 'this.shadowRoot'
        // Apply external styles to the shadow dom
        const linkElem = document.createElement('link');
        linkElem.setAttribute('rel', 'stylesheet');
        linkElem.setAttribute('href', '/static/css/poppers.css');

        // Event listener that needs removal (https://stackoverflow.com/a/22870717)
        this._zPopBack = this.zPopBack.bind(this);
        
        // Create backdrop
        const popperBackDrop = document.createElement('div'); 
        popperBackDrop.id = 'popper-backdrop';
        popperBackDrop.addEventListener('click', (e) => this.closePoppers(e));
        
        // Create the trigger button element
        const triggerBtn = document.createElement('button');
        triggerBtn.innerText = this.dataset.triggerText;
        triggerBtn.type = 'button';
        triggerBtn.classList.add('popper-button');
        triggerBtn.addEventListener('click', (e) => this.openPopper(e));
        
        // Create the actual popper
        const popper = document.createElement('div');
        popper.classList.add('popper');
        popper.dataset.open = 'false';
        popper.dataset.position = this.dataset.position || 'left';
        popper.innerHTML = this.innerHTML;
        
        // Remove the innerHTML to make inspection less confusing
        this.innerHTML = null;
        
        // Create box containing trigger and popper
        const popperBox = document.createElement('span');
        popperBox.classList = this.classList;
        popperBox.classList.add('popper-box');
        popperBox.appendChild(triggerBtn);
        popperBox.appendChild(popper);
        
        // Attach the created elements to the shadow dom
        shadow.appendChild(linkElem);
        shadow.appendChild(popperBackDrop);
        shadow.appendChild(popperBox);
    }

    popperFit(desiredPosition, popper, pBox) {
        /*  Given a desired position, a popper element, and its containing
            box, return the appropriate `top` and `left` positioning.
        */
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

    openPopper(e) {
        // Open a popper
        const popper = e.currentTarget.nextSibling;
        const pBox = e.currentTarget;
        popper.style.display = 'block';
        let fit = this.popperFit(popper.dataset.position, popper, pBox);
        popper.style.top = `${fit.pTop}px`;
        popper.style.left = `${fit.pLeft}px`;
        const pRect = popper.getBoundingClientRect();
        // If the popper is going to render offscreen, find another location for it.
        // This will only handle a single case, and should handle all cases...
        if (pRect.x < 0) {
            popper.style.top, popper.style.left = null;
            fit = this.popperFit('right', popper, pBox);
            popper.style.top = `${fit.pTop}px`;
            popper.style.left = `${fit.pLeft}px`;
        } else if ((pRect.x + pRect.width) > document.documentElement.clientWidth) {
            popper.style.top, popper.style.left = null;
            fit = this.popperFit('left', popper, pBox);
            popper.style.top = `${fit.pTop}px`;
            popper.style.left = `${fit.pLeft}px`;
        } else if (pRect.y < 0) {
            popper.style.top, popper.style.left = null;
            fit = this.popperFit('bottom', popper, pBox);
            popper.style.top = `${fit.pTop}px`;
            popper.style.left = `${fit.pLeft}px`;
        } else if ((pRect.y + pRect.height) > document.documentElement.clientHeight) {
            popper.style.top, popper.style.left = null;
            fit = this.popperFit('top', popper, pBox);
            popper.style.top = `${fit.pTop}px`;
            popper.style.left = `${fit.pLeft}px`;
        }
        popper.dataset.position = fit.pos;
        popper.classList.add(`pos-${fit.pos}`);
        popper.removeEventListener('transitionend', this._zPopBack);
        popper.style.opacity = '1';
        popper.style.zIndex = '10';
        popper.dataset.open = 'true';
        const popperBackDrop = this.shadowRoot.getElementById('popper-backdrop');
        popperBackDrop.style.opacity = '1';
        popperBackDrop.style.zIndex = '5';
        popperBackDrop.removeEventListener('transitionend', this._zPopBack);
    }

    zPopBack(e) {
        /*  To enable animations, transitionend event handler to lower
            element's z-index and clear added styles so `display: none`
            can take precedence
        */
        e.target.style.zIndex = '-1';
        e.target.style = null;
    }

    closePoppers(e) {
        // Close a popper
        const p = this.shadowRoot.querySelector('div.popper');
        p.addEventListener('transitionend', this._zPopBack);
        p.style.opacity = '0';
        p.dataset.open = 'false';
        e.currentTarget.addEventListener('transitionend', this._zPopBack);
        e.currentTarget.style.opacity = '0';
    }
}

customElements.define('popper-box', PopperBox);
