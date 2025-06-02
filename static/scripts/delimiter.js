
/**
 * Editor.js Delimiter plugin with full config support, no build tools required
 * Supports: styleOptions, defaultStyle, lineWidth, lineThickness
 */
class Delimiter {
  static get toolbox() {
    return {
      title: 'Delimiter',
      icon: '<svg width="17" height="14" viewBox="0 0 17 14"><text x="1" y="12" font-size="14">---</text></svg>',
    };
  }

  constructor({ data = {}, config = {}, api }) {
    this.api = api;
    this.data = {
      style: data.style || config.defaultStyle || 'star',
      lineWidth: data.lineWidth || config.defaultLineWidth || 50,
      lineThickness: data.lineThickness || config.defaultLineThickness || 2,
    };

    this.config = {
      styleOptions: config.styleOptions || ['star', 'dash', 'line'],
      lineWidthOptions: config.lineWidthOptions || [25, 50, 100],
      lineThicknessOptions: config.lineThicknessOptions || [1, 2, 3],
    };
  }

  render() {
    const wrapper = document.createElement('div');
    wrapper.className = 'custom-delimiter';
    wrapper.style.textAlign = 'center';
    wrapper.style.padding = '8px 0';

    const child = document.createElement('div');

    if (this.data.style === 'star') {
      child.textContent = '***';
    } else if (this.data.style === 'dash') {
      child.textContent = '---';
    } else {
      // line
      child.style.width = this.data.lineWidth + '%';
      child.style.height = this.data.lineThickness + 'px';
      child.style.margin = '0 auto';
      child.style.backgroundColor = '#000';
    }

    wrapper.appendChild(child);
    return wrapper;
  }

  save() {
    return {
      style: this.data.style,
      lineWidth: this.data.lineWidth,
      lineThickness: this.data.lineThickness,
    };
  }

  static get sanitize() {
    return {
      style: false,
      lineWidth: false,
      lineThickness: false,
    };
  }
}

window.Delimiter = Delimiter;
