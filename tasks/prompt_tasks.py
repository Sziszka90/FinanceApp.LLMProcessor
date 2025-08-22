from fastapi import BackgroundTasks
from services.llm_service import get_llm_response, get_llm_response_with_tools
from rabbitmq_publisher import publish_async

async def handle_prompt(
        prompt: str, 
        correlation_id: str, 
        exchange: str, 
        user_id: str = None,
        routing_key: str = None):
    try:
        response = await get_llm_response(prompt)
        message = {
            "correlation_id": correlation_id,
            "success": True,
            "user_id": user_id,
            "prompt": prompt,
            "response": response
        }
        await publish_async(exchange, routing_key, message)

    except Exception as e:
        error_message = {
            "correlation_id": correlation_id,
            "success": False,
            "user_id": user_id,
            "prompt": prompt,
            "error": str(e)
        }
        await publish_async(exchange, routing_key, error_message)
        print(f"[ERROR] Failed to process LLM request {correlation_id}: {e}")

async def process_prompt_async(
        prompt: str, 
        user_id: str, 
        correlation_id: str, 
        routing_key: str,
        exchange: str,
        background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(
            handle_prompt, 
            prompt, 
            correlation_id, 
            exchange,
            user_id, 
            routing_key,      
        )

        return {"status": "success", "correlation_id": correlation_id, "message": "Request received and will be processed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
async def process_prompt(
        prompt: str, 
        user_id: str, 
        correlation_id: str):
    try:
        response = await get_llm_response_with_tools(prompt, user_id=user_id)

        return {"status": "success", "correlation_id": correlation_id, "message": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}
