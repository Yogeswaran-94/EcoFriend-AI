from llama_cpp import Llama

# Load your model - make sure the path matches your .gguf file location
llm = Llama(
    model_path="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_gpu_layers=40,  # or adjust based on your GPU memory
    n_ctx=2048,
    use_mlock=False,
)

# Simple prompt
output = llm("Q: How can I reduce electricity usage at home?\nA:", max_tokens=200, stop=["Q:", "\n"])

print("AI Response:")
print(output["choices"][0]["text"].strip())
