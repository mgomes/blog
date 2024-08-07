Date: August 7, 2024
Tags: ai, quantization

# Selecting a Llama 3.1 Model (what is a q4_K_S anyway??)

You're ready to give Meta's new Llama 3.1 model a try, but do you download `405b-instruct-q4_K_S`, `8b-instruct-q3_K_L`, or `70b-instruct-q5_0-taylors-version`?

{{more}}

If you're staring at [Ollama's Llama 3.1 model page](https://ollama.com/library/llama3.1/tags), you will see almost 90 different versions of the model. Let's break down the naming convention to help you select the right one for your use case.

## Instruct vs Text

The first choice is between the base model (text) and the version fine-tuned for handling instructions (instruct). If you intend to use the model for chatbot-style interactions (common), you should choose the instruct version.

The base model is useful if you intend to fine-tune the model against your own dataset(s).

## Parameters

The next part of the model name is the number of parameters (weights and biases). This is a rough indicator of the model's size and complexity. The larger the number, the more powerful the model, but also the more resources it will consume. For the Llama 3.1 herd of models, the models are offered in 8b, 70b, and 405b sizes ("b" as in billion).

## GPU Memory Napkin Math Detour

AI models are typically trained in 32-bit or 16-bit floating point precision. That is, each model parameter can be represented as a 32 or 16-bit floating point number.

In the case of 16-bit floating point numbers, there are two common flavors: fp16 and bf16. The former refers to IEEE 754 [half precision floats](https://en.wikipedia.org/wiki/Half-precision_floating-point_format) and the latter refers to ["brain" float16](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format) -- a format developed by the Google Brain team. Both fp16 and bf16 consume 16 bits (or 2 bytes) of memory, and they only differ in how many bits are reserved for the exponent portion versus the fraction portion of the floating point number.

With some napkin math, we estimate that the Llama 3.1 8b model at fp16 precision will need at least 16GB of GPU memory (8 billion * 2 bytes). In reality, it will need more in order to store things like the model's KV cache. Llama 3.1 models aren't offered in fp32 -- but if they were, the 8b model would require at least 32GB of GPU memory (8 billion * 4 bytes).

Using the same math, we can estimate that the 405b version of the model would require ~900GB of GPU memory (VRAM) at fp16. For reference, NVIDIA's flagship H100 accelerator card only has 80GB of memory. In order to run these larger models, accelerators have to be linked together using ultra high-speed networking fabrics such as NVIDIA's own [NVLink](https://en.wikipedia.org/wiki/NVLink).

## Quantization

With those eye popping VRAM requirements out of the way, we can begin to appreciate the role quantization plays. Quantization is the process of reducing the precision of the model's parameters in order to reduce the requirements for running the model. You’ll encounter many strategies for quantization: round-to-nearest (RTN), k-quantization, AWQ, GPTQ, and more. We’ll cover RTN and k-quantization very briefly as they are the two most commonly found in [GGUF](https://huggingface.co/docs/hub/en/gguf) models.

RTN is a very fast, albeit less accurate, quantization strategy. It takes groups of floating point parameters and uses discrete levels (or bins) to approximate the values using lower precision numbers. It’s very similar to how analog audio is transformed to MP3s in digital signal processing. 

RTN is represented as `q_<num>`. The `num` in this case represents the precision of the integer in bits. So for example, the Llama 3.1 model `8b-instruct-q4_0` is an 8 billion parameter model, fine-tuned for instructions, and quantized using RTN at 4-bit integer precision.

We’re getting there!

The second number (0) in the `q4_0` label refers to the the extra bits used for the block for this quantization strategy. In the case of `q4_0` it is not using any extra bits.

A more popular approach that strikes a better balance between performance and quality is k-quantization. With this method, values are grouped into k-clusters. Each cluster has a centroid and the distance between the points in the cluster and the centroids are calculated. Centroids are then re-calculated as the mean distance between all the points in the cluster. As you might imagine, the higher number of clusters, the higher the accuracy.

So in the case of `405b-instruct-q4_K_S` we have the 405 billion parameter version, fine-tuned for instructions, using k-quantization, 4-bit integer precision, and the “S” variant. 

In order to explain that last letter, we should first point out that there are three variants: “S”, “M”, and “L”. These may mean small, medium, and large -- but I am not sure. What I do know is that these variants refer to [how different types of tensors are quantized](https://github.com/ggerganov/llama.cpp/pull/1684#issue-1739619305). So for example, `Q5_K_S` means all tensors are reduced to 5-bit integers. `Q5_K_M` uses 6-bit integers for the attention and feed-forward tensors and 5-bit integers for all other tensors.

## So, which one do you pick?

When comparing quantization levels, you will hear the term “perplexity”. It’s technically defined as the exponential of the entropy of the model -- but you can think of it as how perplexed/confused a model becomes. The higher the perplexity compared to the un-quantized version of the model, the worse the model has become.

For most models, you will find that 8-bit quantized versions perform almost identically to their full-precision counterparts. Using our napkin math from before we calculate the 8b Llama 3.1 model to require only 8GB of GPU memory (8 billion * 1 byte) when using 8-bit quantization.

Which quantized version you end up using therefore depends entirely on your use case and hardware. I’ll leave you with these rules of thumb:

1. Use a k-quantized version over RTN when selecting a GGUF model
2. Staying close to 8 bits is best if you have the hardware
3. Use the “M” variant for balance but drop to “S” before dropping down in bits
4. Watch out for non-standard sizes such as q3 and q5 as it may slow down calculations as your accelerator attempts to pad the values to make them computable. If you absolutely need to, do some performance tests to compare
5. Avoid q2, you are likely better using a smaller model instead

Happy inferencing! 🤓