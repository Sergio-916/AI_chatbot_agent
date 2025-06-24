from fastapi import APIRouter
import uuid


from schemas.schema import MessageCreate, Message

from services.google_service import get_llm_response_with_context
from services.google_service import validate_input

router = APIRouter()


@router.post("/ai", response_model=Message)
async def process_user_message(msg: MessageCreate):
    user_query = msg.message
    response_id = uuid.uuid4().hex
    if not validate_input(user_query):
        return {
            "message": "Invalid input. Please input related question.",
            "id": response_id,
            "process_time": None,
        }
    llm_response_text, process_time = get_llm_response_with_context(user_query)
    return {
        "message": llm_response_text,
        "id": response_id,
        "process_time": process_time,
    }
