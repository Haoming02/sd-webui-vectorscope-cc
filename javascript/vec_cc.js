class VectorscopeCC {

    static dot = { 'txt': null, 'img': null };

    static updateCursor(r, g, b, mode) {
        const mag = Math.abs(r) + Math.abs(g) + Math.abs(b);
        var condX, condY;

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

                const zeta = Math.atan(y / x);
                var degree = 0;

                if (x >= 0) {
                    if (y >= 0)
                        degree = zeta * 180 / Math.PI;
                    else
                        degree = 360 + zeta * 180 / Math.PI;
                }
                else if (x < 0) {
                    degree = 180 + zeta * 180 / Math.PI;
                }

                var r = -(0.00077 * (433 * x * degree + 750 * y * degree) / degree);
                var g = y / 0.866 + r;
                var b = x + 0.5 * r + 0.5 * g;

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
            [
                document.getElementById(`cc-r-${mode}`).querySelector('input[type=number]'),
                document.getElementById(`cc-r-${mode}`).querySelector('input[type=range]')
            ],
            [
                document.getElementById(`cc-g-${mode}`).querySelector('input[type=number]'),
                document.getElementById(`cc-g-${mode}`).querySelector('input[type=range]')
            ],
            [
                document.getElementById(`cc-b-${mode}`).querySelector('input[type=number]'),
                document.getElementById(`cc-b-${mode}`).querySelector('input[type=range]')
            ]
        ];

        const temp = document.getElementById(`cc-temp-${mode}`);

        const dot = temp.querySelector('img');
        dot.id = `cc-dot-${mode}`;
        dot.style.left = 'calc(50% - 12px)';
        dot.style.top = 'calc(50% - 12px)';

        container.appendChild(dot);
        temp.remove();

        VectorscopeCC.dot[mode] = dot;
        VectorscopeCC.registerPicker(wheel, sliders, dot);
    });

});
