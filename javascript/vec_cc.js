onUiLoaded(async () => {

    const Modes = ['txt', 'img']

    Modes.forEach((mode) => {

        const container = document.getElementById('cc-colorwheel-' + mode)
        container.style.height = '200px'
        container.style.width = 'auto'

        container.querySelector('.float').remove()
        container.querySelector('.download').remove()

        const wheel = container.getElementsByTagName('img')[0]
        wheel.style.height = '100%'
        wheel.style.width = 'auto'
        wheel.style.margin = 'auto'

        const temp = document.getElementById('cc-temp-' + mode)

        const dot = temp.getElementsByTagName('img')[0]
        dot.id = 'cc-dot-' + mode

        container.appendChild(dot)
        dot.style.left = 'calc(50% - 12px)'
        dot.style.top = 'calc(50% - 12px)'

        temp.remove()

    })

})