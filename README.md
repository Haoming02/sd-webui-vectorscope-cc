# SD Webui Vectorscope CC
This is an Extension for the [Automatic1111 Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui), which performs *a kind of* **Offset Noise**[*](#offset-noise-tldr) natively. 

> *This Extension is the result of my numerous trial and error[\*](#what-is-under-the-hood)*

## How to Use
After installing this Extension, you will see a new section in both **txt2img** and **img2img** tabs, 
refer to the parameters and sample images below and play around with the values.

**Note:** Since this modifies the underlying latent noise, the composition may change drastically.

**Note:** Due to my scaling implementations, lower steps *(`< 10`)* causes the effects to be way stronger 

#### Parameters
- **Enable:** Turn on & off this Extension
- **Alt:** Modify an alternative Tensor instead. The effects are significantly stronger when this is enabled.
- **Brightness:** Adjust the overall brightness of the image
- **Contrast:** Adjust the overall contrast of the image
- **Saturation:** Adjust the overall saturation of the image
- **Skip:** Skip the last few percentage of steps and only process the first few

<p align="center"><img src="samples/Skip.jpg" width=512></p>
<p align="center"><i>Notice the noises on the faces</i></p>

##### Color Channels
<table>
    <thead align="center">
        <tr>
            <td><b>Channel</b></td>
            <td><b>Lower</b></td>
            <td><b>Higher</b></td>
        </tr>
    </thead>
    <tbody align="center">
        <tr>
            <td><b>R</b></td>
            <td>Cyan</td>
            <td>Red</td>
        </tr>
        <tr>
            <td><b>G</b></td>
            <td>Magenta</td>
            <td>Green</td>
        </tr>
        <tr>
            <td><b>B</b></td>
            <td>Yellow</td>
            <td>Blue</td>
        </tr>
    </tbody>
</table>

##### Advanced Settings

- **Process Hires. fix:** By default, this Extension only functions during the **txt2img** phase, so that **Hires. fix** may "fix" the artifacts introduced during **txt2img**. Enable this to process **Hires. fix** phase too.
  - This option does not affect **img2img**
  - **Note:** Make sure your **txt2img** has higher `steps` than **Hires. fix** if you enable this
- **Noise Settings:** Currently does **nothing** *(To be implemented...)*

## Sample Images
- **Checkpoint:** [UHD-23](https://civitai.com/models/22371/uhd-23)
- **Pos. Prompt:** `(masterpiece, best quality), 1girl, solo, night, street, city, neon_lights`
- **Neg. Prompt:** `(low quality, worst quality:1.2)`, [`EasyNegative`](https://huggingface.co/datasets/gsdf/EasyNegative/tree/main), [`EasyNegativeV2`](https://huggingface.co/gsdf/Counterfeit-V3.0/tree/main/embedding)
- `Euler a`; `20 steps`; `7.5 CFG`; `Hires. fix`; `Latent (nearest)`; `16 H.steps`; `0.6 D.Str.`; `Seed:`**`3814649974`**
- *No offset noise models were used*

<p align="center">
<b>Base</b><br>
<code>Extension Disabled</code><br>
<img src="samples/00.png" width=512>
</p>

<p align="center">
<b>Dark</b><br>
<code><b>Brightness:</b> -2; <b>Contrast:</b> 1</code><br>
<img src="samples/01.png" width=512>
</p>

<p align="center">
<b>Bright</b><br>
<code><b>Brightness:</b> 1; <b>Contrast:</b> -0.5; <b>Alt:</b> Enabled</code><br>
<img src="samples/02.png" width=512>
</p>

<p align="center">
<b>Chill</b><br>
<code><b>Brightness:</b> -2.5; <b>Contrast:</b> 1.5</code><br>
<code><b>R:</b> -0.5; <b>B:</b> 1</code><br>
<img src="samples/03.png" width=512>
</p>

<p align="center">
<b><s>Mexican Movie</s></b><br>
<code><b>Brightness:</b> 3; <b>Contrast:</b> -1.5; <b>Saturation:</b> 1</code><br>
<code><b>R:</b> 1; <b>G:</b> 0.5; <b>B:</b> -2</code><br>
<img src="samples/04.png" width=512>
</p>

<p align="center"><i>Notice the significant differences even when using the same seed</i></p>

## Roadmap
- [X] Extension Released
- [X] Add Support for **X/Y/Z Plot**
- [ ] Add Support for **Inpaint**
- [ ] Implement different Noise functions
- [ ] Implement better scaling algorithm
- [ ] Add Gradient feature
- [ ] Fix the Brightness issues
- [ ] Append Parameters onto Metadata

<p align="center"><img src="samples/XYZ.jpg" width=512></p>
<p align="center"><code><b>X/Y/Z Plot</b> Support</code></p>

## Known Issues
- Does not work with `DDIM` sampler
- Has little effect when used with certain **LoRA**s
- Too high **Brightness** causes the image to be blurry; Too low **Brightness** causes the image to be noisy
- Values too extreme can cause distortions

<hr>

#### Offset Noise TL;DR
The most common *version* of **Offset Noise** you may have heard of is from this [blog post](https://www.crosslabs.org/blog/diffusion-with-offset-noise), 
where it was discovered that the noise functions used during **training** were flawed, causing `Stable Diffusion` to always generate images with an average of `0.5`.

> **ie.** Even if you prompt for dark/night or bright/snow, the overall image still looks "grey"

> [Technical Explanations](https://youtu.be/cVxQmbf3q7Q)

However, this Extension instead tries to offset the latent noise during the **inference** phase. 
Therefore, you do not need to use models that were specially trained, as this can work on any model.
Though, the results may not be as good as using properly trained models.

<hr>

#### What is Under the Hood
After reading through and messing around with the code, 
I found out that it is possible to directly modify the Tensors 
representing the latent noise used by the Stable Diffusion process.

The dimentions of the Tensors is `(X, 4, H / 8, W / 8)`, which can be thought of like this:

> **X** batch of noise images, with **4** channels, each with **(W / 8) x (H / 8)** values

> **eg.** Generating a 512x768 image will create a Tensor of size (1, 4, 96, 64)

Then, I tried to play around with the values of each channel and ended up discovering these relationships.
Essentially, the 4 channels correspond to the **CMYK** color format, 
hence why you can control the brightness as well as the colors.

<hr>

#### Vectorscope?
The Extension is named this way because the color interactions remind me of the `Vectorscope` found in **Premiere Pro**'s **Lumetri Color**.
Those who are experienced in Color Correction should be rather familiar with this Extension.

<p align="center"><img src="samples/Vectorscope.png" width=256></p>

<sup>~~Yes. I'm aware that it's just how digital colors work in general.~~</sup>