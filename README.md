# OmegaPoint

Toy project to try out a locally-running LLM. This uses the llm_qwen3_text_gen workflow running via ComfyUI as a local server (the server address and json filename of the API-exported workflow can be updated in ChatBot's __init__ function if needed).

The ChatBot class provides an interface that just requires a prompt to be given to the method get_query().

OmegaPoint is a first try at a self-improving version of ChatBot. It runs cycles of getting a response from a prompt, criticizing and scoring the output, and adjusting the prompt accordingly for the next iteration.

It uses a little structure in the input, requiring the user role, aim of the user, and information to be be specified. OmegaPoint1.py provides a template for a user research application.
