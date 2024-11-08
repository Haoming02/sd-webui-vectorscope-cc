class VectorscopeCC {

    static dot = { 'txt': undefined, 'img': undefined };

    /**
     * @param {number} r @param {number} g @param {number} b
     * @param {string} mode "txt" | "img"
     */
    static updateCursor(r, g, b, mode) {
        const mag = Math.abs(r) + Math.abs(g) + Math.abs(b);
        let condX, condY;

        if (mag < Number.EPSILON) {
            condX = 0.0;
            condY = 0.0;
        } else {
            condX = 25 * Math.sqrt(r * r + g * g + b * b) * (r * -0.5 + g * -0.5 + b * 1.0) / mag;
            condY = 25 * Math.sqrt(r * r + g * g + b * b) * (r * -0.866 + g * 0.866 + b * 0.0) / mag;
        }

        this.dot[mode].style.left = `calc(50% + ${condX - 12}px)`;
        this.dot[mode].style.top = `calc(50% + ${condY - 12}px)`;
    }

    /**
     * @param {HTMLImageElement} wheel
     * @param {HTMLInputElement[]} sliders
     * @param {HTMLImageElement} dot
     */
    static registerPicker(wheel, sliders, dot) {
        ['mousemove', 'click'].forEach((event) => {
            wheel.addEventListener(event, (e) => {
                e.preventDefault();
                if (e.type === 'mousemove' && e.buttons != 1)
                    return;

                const rect = e.target.getBoundingClientRect();
                const p_rect = e.target.parentNode.getBoundingClientRect();

                const shift = (p_rect.width - rect.width) / 2.0;
                dot.style.left = `calc(${e.clientX - rect.left}px - 12px + ${shift}px)`;
                dot.style.top = `calc(${e.clientY - rect.top}px - 12px)`;

                const x = ((e.clientX - rect.left) - 100.0) / 25;
                const y = ((e.clientY - rect.top) - 100.0) / 25;

                let r = -0.077 * (4.33 * x + 7.5 * y);
                let g = y / 0.866 + r;
                let b = x + 0.5 * r + 0.5 * g;

                const mag = Math.sqrt(r * r + g * g + b * b);
                const len = Math.abs(r) + Math.abs(g) + Math.abs(b);

                r = (r / mag * len).toFixed(2);
                g = (g / mag * len).toFixed(2);
                b = (b / mag * len).toFixed(2);

                sliders[0][0].value = r;
                sliders[0][1].value = r;
                sliders[1][0].value = g;
                sliders[1][1].value = g;
                sliders[2][0].value = b;
                sliders[2][1].value = b;
            });
        });

        ['mouseleave', 'mouseup'].forEach((event) => {
            wheel.addEventListener(event, () => {
                updateInput(sliders[0][0]);
                updateInput(sliders[1][0]);
                updateInput(sliders[2][0]);
            });
        });
    }

}

onUiLoaded(() => {

    ['txt', 'img'].forEach((mode) => {
        const container = document.getElementById(`cc-colorwheel-${mode}`);
        container.style.height = '200px';
        container.style.width = '200px';

        const wheel = container.querySelector('img');
        container.insertBefore(wheel, container.firstChild);

        while (container.firstChild !== container.lastChild)
            container.lastChild.remove();

        wheel.ondragstart = (e) => { e.preventDefault(); return false; };
        wheel.id = `cc-img-${mode}`;

        const sliders = [
            document.getElementById(`cc-r-${mode}`).querySelectorAll('input'),
            document.getElementById(`cc-g-${mode}`).querySelectorAll('input'),
            document.getElementById(`cc-b-${mode}`).querySelectorAll('input'),
        ];

        const temp = document.getElementById(`cc-temp-${mode}`);

        const dot = temp.querySelector('img');
        dot.style.left = 'calc(50% - 12px)';
        dot.style.top = 'calc(50% - 12px)';
        dot.id = `cc-dot-${mode}`;

        container.appendChild(dot);
        temp.remove();

        VectorscopeCC.dot[mode] = dot;
        VectorscopeCC.registerPicker(wheel, sliders, dot);
    });

    const config = document.getElementById("setting_cc_no_defaults").querySelector('input[type=checkbox]');
    if (config.checked)
        return;

    setTimeout(() => {
        ['txt', 'img'].forEach((mode) => {
            const r = document.getElementById(`cc-r-${mode}`).querySelector("input").value;
            const g = document.getElementById(`cc-g-${mode}`).querySelector("input").value;
            const b = document.getElementById(`cc-b-${mode}`).querySelector("input").value;

            VectorscopeCC.updateCursor(r, g, b, mode);
        });
    }, 100);

});
