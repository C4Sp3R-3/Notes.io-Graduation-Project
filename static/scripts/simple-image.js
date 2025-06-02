class SimpleImage {
    static get toolbox() {
        return {
            title: 'Image',
            icon: '<svg width="17" height="15" viewBox="0 0 336 276" xmlns="http://www.w3.org/2000/svg"><path d="M291 150V79c0-19-15-34-34-34H79c-19 0-34 15-34 34v42l67-44 81 72 56-29 42 30zm0 52l-43-30-56 30-81-67-66 39v23c0 19 15 34 34 34h178c17 0 31-13 34-29zM79 0h178c44 0 79 35 79 79v118c0 44-35 79-79 79H79c-44 0-79-35-79-79V79C0 35 35 0 79 0z"/></svg>'
        };
    }

    constructor({ data }) {
        this.data = data || {};
        this.wrapper = null;
    }

    render() {
        this.wrapper = document.createElement('div');
        this.wrapper.classList.add('simple-image-wrapper');
        this.wrapper.style.marginTop = '8px';
        this.wrapper.style.marginBottom = '8px';
        this.wrapper.style.display = 'flex';
        this.wrapper.style.flexDirection = 'column';  // stack elements vertically
        this.wrapper.style.alignItems = 'center';     // center them horizontally

        if (!this.data.url) {
            // URL input
            const urlInput = document.createElement('input');
            urlInput.placeholder = 'Paste image URL...';
            urlInput.classList.add('simple-image-input');
            urlInput.type = 'url';

            urlInput.addEventListener('change', () => {
                const url = urlInput.value;
                if (url) {
                    this.data.url = url;
                    this._updateImage(url);
                }
            });

            // Hidden file input
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*';
            fileInput.style.display = 'none';
            fileInput.id = 'file-upload-' + Math.random().toString(36).substr(2, 9);

            // Styled label as button
            const fileLabel = document.createElement('label');
            fileLabel.htmlFor = fileInput.id;
            fileLabel.innerText = 'Upload Image';
            fileLabel.classList.add('upload-btn-style');
            fileLabel.style.marginTop = '8px';  // spacing between input and button

            fileInput.addEventListener('change', async (event) => {
                const file = event.target.files[0];
                if (file) {
                    const base64 = await this._readFileAsBase64(file);
                    this.data.url = base64;
                    this._updateImage(base64);
                }
            });

            this.wrapper.appendChild(urlInput);
            this.wrapper.appendChild(fileInput);
            this.wrapper.appendChild(fileLabel);
        } else {
            this._updateImage(this.data.url);
        }

        return this.wrapper;
    }

    _updateImage(url) {
        this.wrapper.innerHTML = ''; // Clear inputs

        const imageElement = document.createElement('img');
        imageElement.src = url;
        imageElement.classList.add('simple-image-preview');

        this.wrapper.appendChild(imageElement);

        this.data.url = url;
    }

    _readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
            reader.readAsDataURL(file);
        });
    }

    save(blockContent) {
        const img = blockContent.querySelector('img');
        return {
            url: img?.src || ''
        };
    }
}

window.SimpleImage = SimpleImage;
