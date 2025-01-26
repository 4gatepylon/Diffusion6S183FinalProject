# Diffusion6S183FinalProject
Diffusion illusions:
- https://diffusionillusions.com/
- https://dangeng.github.io/visual_anagrams/#misc_examples
- https://en.wikipedia.org/wiki/List_of_optical_illusions (inspiration)

We are trying to get it to generate reasonably-looking text.

This may or may not also be something that we consider submitting to ICML.

The abstractI submitted is the following:
```
Improvements in the image-generation capabilities of diffusion models has been stunning over the last four years. However, they still lag behind in generating images that have coherent text within them. Specifically, while state of the art models are able to generate simple phrases in high-resource languages, they struggle to generate strings with unusual character combinations, even when those strings are as short as two characters. Our first contribution is to provide an improved benchmark to measure the text-rendering capabilities of diffusion models by coupling them with discriminative multi-modal models that feature OCR-like capabilities. Our second contribution is to provide a simple training and inference agentic scaffold to utilize these discriminative models for guidance during the image generation process to iteratively tweak sections of the image that do not match the desired text to render. Our system can be used with most off-the-shelf diffusion models, enabling them to render text they could not previously, with only minor changes. Our last contribution is to connect the text-rendering problem to the generation of compositional images in general. Analogously to their inability to render unusual strings of text, we also observe that diffusion models struggle to generate images that combine easy-to-render objects in unusual relations. We show that in a more general sense, iterative generation of an image with guidance from a stronger discriminative model can lift the capabilities of said generative diffusion model to be on-par to that of the discriminative abilities of the discriminative model.
```

So the proposed contribution is:
1. The ability to measure and optimize rendering of text quality (and potentially the positioning of objects in pre-defined relations)
2. Agentic and iterative drawing loop using discriminative models for guidance
3. Superior performance on text-rendering and compositional image generation

I also have some questions/ideas as of `2025-01-24` that may or may not be applicable:
1. Overlay text and then diffuse/tool-use to pastiche existing images (i.e. use the language model to list out what components need to be rendered, then use the vision model to render each one, then mix them **either in latent space or in the image space**; for latent space we could, for example, take a weighted average of the different latents). Question format: can diffusion models pastiche images/concepts either in latent or image space?
2. Question: can diffusion models as they stand fill in patches? Even if those patches are not gaussian noise?

TODO let's answer these questions and then move to google docs because it'll allow for commenting etc... and make for a generally better log