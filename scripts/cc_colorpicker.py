import modules.scripts as scripts
import gradio as gr

WHEEL = scripts.basedir() + '/samples/Vectorscope.png'
DOT = scripts.basedir() + '/scripts/dot.png'

def create_colorpicker(is_img):
	gr.Image(WHEEL, type='filepath', interactive=False, container=False, elem_id='cc-colorwheel-' + ('img' if is_img else 'txt'))
	gr.Image(DOT, type='filepath', interactive=False, container=False, elem_id='cc-temp-' + ('img' if is_img else 'txt'))

def horizontal_js(is_img):
	mag = '(Math.abs(r) + Math.abs(g) + Math.abs(b))'
	calc = '25 * Math.sqrt(r*r+g*g+b*b) * (r * -0.5 + g * -0.5 + b * 1.0) / ' + mag
	cond = '(' + mag + ' === 0 ? 0 : ' + calc + ')'

	return "(r, g, b) => {document.getElementById('cc-dot-" + ('img' if is_img else 'txt') + "').style.left = 'calc(50% + ' +(" + cond + "- 12) + 'px)'}"

def vertical_js(is_img):
	mag = '(Math.abs(r) + Math.abs(g) + Math.abs(b))'
	calc = '25 * Math.sqrt(r*r+g*g+b*b) * (r * -0.866 + g * 0.866 + b * 0.0) / ' + mag
	cond = '(' + mag + ' === 0 ? 0 : ' + calc + ')'

	return "(r, g, b) => {document.getElementById('cc-dot-" + ('img' if is_img else 'txt') + "').style.top = 'calc(50% + ' +(" + cond + "- 12) + 'px)'}"