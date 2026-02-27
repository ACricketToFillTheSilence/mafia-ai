from typing import List, Optional
from ai.anthropic import AnthropicAPI
import ai.ai_constants

def _get_provider():
    return AnthropicAPI()

def get_provider_response(
    user_id: str,
    prompt: str,
    context: Optional[List] = [],
    system_content=ai.ai_constants.GAME_MASTER_SYSTEM_CONTENT,
):
    formatted_context = "\n".join([f"{msg['user']}: {msg['text']}" for msg in context])
    full_prompt = f"Prompt: {prompt}\nContext: {formatted_context}"
    try:
        model_name = "claude-haiku-4-5-20251001"
        #provider_name, model_name = get_user_state(user_id, False)
        provider = _get_provider()
        provider.set_model(model_name)
        response = provider.generate_response(full_prompt, system_content)
        return response
    except Exception as e:
        raise e
