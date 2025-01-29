# Diffusion6S183FinalProject
Diffusion illusions:
- https://diffusionillusions.com/
- https://dangeng.github.io/visual_anagrams/#misc_examples
- https://en.wikipedia.org/wiki/List_of_optical_illusions (inspiration)

We are trying to get it to generate reasonably-looking text.

This may or may not also be something that we consider submitting to ICML.

The abstract I submitted is the following:
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
3. Can black-box diffusion models actually do better than ARTIST and these other methods if we just scale enough and get better data? Maybe our paper can be about synthetic data? I would like to avoid training too much though ngl.
4. Can StableDiffusion generate any character roughly ok? It's imporant to know this because if it cannot, then I don't think we can CoT for compositionality.

# Text and CoT Generation using LLMs + Diffusion Models:
- https://arxiv.org/pdf/2501.13926
- https://arxiv.org/pdf/2305.10855
- https://arxiv.org/pdf/2311.16465
- https://arxiv.org/abs/2406.12044
- https://github.com/microsoft/unilm/tree/master
- Adding SDEdit here since it's likely the paradigm I will use: https://github.com/ermongroup/SDEdit?tab=readme-ov-file. It allows the usage of diffusion on guiding images. This is one of the ideas I had before so it looks good to see that this works and is done already.

Key ideas: mostly written in my paper notes. It seems like the high level idea is usually the same here, however: to train a text localization model in addition to the diffusion model and then combine them to make a text-generation SYSTEM that is better than just having a black-box diffusion model.

# How to do researcher better/write better papers:
TLDR: you should have on deliverable per day. A good sign is if you overwhelm the weekly check-in and have a result per day.
- https://ethanperez.net/easy-paper-writing-tips/
- https://www.alignmentforum.org/posts/dZFpEdKyb9Bf4xYn7/tips-for-empirical-alignment-research
- Keep a log, look here: https://docs.google.com/document/d/1grG2ua929j_X5dA5bdX26kS6YkddnCDHUa8CstQcoCM/edit?pli=1&tab=t.0
- TONS of great tools, really look into this: https://www.alignmentforum.org/posts/6P8GYb4AjtPXx6LLB/tips-and-code-for-empirical-research-workflows

# 2024-01-27 Text-Diffuser
NEW IDEA: just start by reproducing ARTIST to get some baseline results. We cannot find the code so this will be a good exercise. We start with going through text-diffuser: https://github.com/microsoft/unilm/tree/master.
- https://arxiv.org/pdf/2305.10855
- https://arxiv.org/pdf/2311.16465

TODOs:
1. Derisk the idea that StableDiffusion 3 can generate ANY character OK (i.e. generate on image per character): it seems like this does not even work. I guess the question then becomes, can Text-Diffuser or artist do this all-right? If not, then we need to drop the agency and actually get a model that can do basic things I guess.
2. Think, but probably reproduce/run Text-Diffusion; OK next step is to be able to load and RUN text-diffuser and ALSO to see if it is indeed able to generate characters/text or not. Seems like Text-Diffusion is sort of biased to put text into the image, but it doesn't always do it. It also seems not fully able to just generate the desired text. It's also immediately apparent that this model does not work out of the box. It seems like hte language modedl gets closer to the language than the image model. It seems like the language model cannot do random strings though.
3. Think, but probably reproduce/run ARTIST

I think my paper might actually be about the beavior of these models out of distribution because none of these models seems capable of generating the desired text/images in the way that I want.

Generally TextDiffuser seems really bad at generating this shit. It's really hard to control it to behave exactly how you want. Could this be a data problem? The models used by OpenAI and anthropic honestly seem to make it closer to the desired text than TextDiffuser.

random ideas: what about 3D perturbations?

random ideas: more guidance will probably make it better; if you never tell it in the dataset what the font is, for example, then it will never be able to learn to create that specific font when you try to describe it