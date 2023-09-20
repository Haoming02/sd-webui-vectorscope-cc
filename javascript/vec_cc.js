function registerPicker(wheel, sliders, mode) {
    for (const event of ['mousemove', 'click']) {
        wheel.addEventListener(event, (e) => {
            e.preventDefault();

            const rect = e.target.getBoundingClientRect();

            if (e.type != 'click') {
                if (e.buttons != 1) {
                    return;
                }

                const dot = e.target.parentElement.querySelector('#cc-dot-' + mode);
                dot.style.position = 'fixed';
                dot.style.left = e.x - (dot.width / 2) + 'px';
                dot.style.top = e.y - (dot.height / 2) + 'px';
            }

            x = ((e.clientX - rect.left) - 100.0) / 25;
            y = ((e.clientY - rect.top) - 100.0) / 25;

            const zeta = Math.atan(y / x)
            var degree = 0

            if (x >= 0) {
                if (y >= 0)
                    degree = zeta * 180 / Math.PI
                else
                    degree = 360 + zeta * 180 / Math.PI
            }
            else if (x < 0) {
                degree = 180 + zeta * 180 / Math.PI
            }

            // -0.5r - 0.5g + b = x
            // -0.866r + 0.866g = y
            // 240r + 120g = z * rgb

            // g = (1 / 0.866)y + r
            // -0.5r - 0.5((1 / 0.866)y + r) + b = x
            // b = x + 0.5r + 0.5((1 / 0.866)y + r)

            // 240r + 120(1 / 0.866)y + r = z * r((1 / 0.866)y + r)(x + 0.5r + 0.5((1 / 0.866)y + r))

            var r = -(0.00077 * (433 * x * degree + 750 * y * degree) / degree)
            var g = y / 0.866 + r
            var b = x + 0.5 * r + 0.5 * g

            const mag = Math.sqrt(r * r + g * g + b * b)
            const len = Math.abs(r) + Math.abs(g) + Math.abs(b)

            r = r / mag * len
            g = g / mag * len
            b = b / mag * len

            sliders[0].value = r.toFixed(2)
            sliders[0].closest('.gradio-slider').querySelector('input[type=range]').value = r.toFixed(2)
            sliders[1].value = g.toFixed(2)
            sliders[1].closest('.gradio-slider').querySelector('input[type=range]').value = g.toFixed(2)
            sliders[2].value = b.toFixed(2)
            sliders[2].closest('.gradio-slider').querySelector('input[type=range]').value = b.toFixed(2)

            if (e.type == 'click') {
                updateInput(sliders[0])
                updateInput(sliders[1])
                updateInput(sliders[2])
            }
        })
    }

    wheel.addEventListener('mouseup', (e) => {
        const dot = e.target.parentElement.querySelector('#cc-dot-' + mode);
        dot.style.position = 'absolute';
        updateInput(sliders[0])
        updateInput(sliders[1])
        updateInput(sliders[2])
    })
}

onUiLoaded(async () => {

    ['txt', 'img'].forEach((mode) => {

        const container = document.getElementById('cc-colorwheel-' + mode)
        container.style.height = '200px'
        container.style.width = 'auto'

        container.querySelector('.float')?.remove()
        container.querySelector('.download')?.remove()
        for (const downloadButton of container.querySelectorAll('[download]')) {
            downloadButton.parentElement.remove()
        }

        const wheel = container.getElementsByTagName('img')[0]
        wheel.style.height = '100%'
        wheel.style.width = 'auto'
        wheel.style.margin = 'auto'
        wheel.id = 'cc-img-' + mode

        wheel.ondragstart = (e) => { e.preventDefault(); }

        sliders = [
            document.getElementById('cc-r-' + mode).querySelector('input'),
            document.getElementById('cc-g-' + mode).querySelector('input'),
            document.getElementById('cc-b-' + mode).querySelector('input')
        ]

        registerPicker(wheel, sliders, mode)

        const temp = document.getElementById('cc-temp-' + mode)

        const dot = temp.getElementsByTagName('img')[0]
        dot.id = 'cc-dot-' + mode

        container.appendChild(dot)
        dot.style.left = 'calc(50% - 12px)'
        dot.style.top = 'calc(50% - 12px)'

        temp.remove()

        const row1 = document.getElementById('cc-apply-' + mode).parentNode
        const row2 = document.getElementById('cc-save-' + mode).parentNode

        row1.style.alignItems = 'end'
        row1.style.gap = '1em'
        row2.style.alignItems = 'end'
        row2.style.gap = '1em'

        // ----- HDR UIs -----
        const hdr_settings = document.getElementById('vec-hdr-' + mode)
        const buttons = hdr_settings.getElementsByTagName('label')

        for (let i = 0; i < buttons.length; i++)
            buttons[i].style.borderRadius = '0.5em'
    })
})
