# OmegaPoint

Toy project to try out a locally-running LLM. This uses the llm_qwen3_text_gen workflow running via ComfyUI as a local server (the server address and json filename of the API-exported workflow can be updated in ChatBot's __init__ function if needed).

The ChatBot class provides an interface that just requires a prompt to be given to the method get_query().

OmegaPoint is a first try at a self-improving version of ChatBot. It runs cycles of getting a response from a prompt, criticizing and scoring the output, and adjusting the prompt accordingly for the next iteration. A "hate-versus-hype" parameter can be used to emphasize a focus on what's good versus what's bad about the outputs.

This was an application that I felt was suited to a locally-running LLM since it involves a lot of calls to the Chatbot and iteration so it could get expensive pretty quickly if you're trying things out using a paid service... It uses a little structure in the input, requiring the user role, aim of the user, and information to be be specified. OmegaPoint1.py provides an example illustrating a user research application.
