from typing import Callable, Awaitable, Any
from core.types import LogLevel
from core import ProcessController
from core.chat_model import get_chat_model
from vision.ocr import VLM_OCR
from langgraph.prebuilt import create_react_agent
from .tools import create_assistant_tools


async def assistant_workflow(
    send_message: Callable[[str, LogLevel], Awaitable[None]],
    user_message: str,
    controller: ProcessController,
    ocr_engine: VLM_OCR,
) -> dict[str, Any]:
    """Assistant workflow that processes user messages using the AI assistant with LangGraph.

    Args:
        send_message: Function to send messages to the user
        user_message: The child's message/question
        controller: Process controller for managing workflows
        ocr_engine: OCR engine for reading blocks
    """
    try:
        await send_message(
            "👋 Hi! I received your message, let me help you with your TinkerBlocks programming!",
            LogLevel.ASSISTANT,
        )

        # Create the chat model
        chat_model = get_chat_model()

        # Use the tools factory to create tools with proper dependencies
        tools = create_assistant_tools(send_message, controller, ocr_engine)

        # Create the react agent
        agent = create_react_agent(chat_model, tools)

        await send_message(
            "🧠 Processing your request with AI assistant...", LogLevel.ASSISTANT
        )

        # Run the agent
        result = await agent.ainvoke({"messages": [("user", user_message)]})

        await send_message("✨ AI assistant completed processing!", LogLevel.SUCCESS)

        return {"status": "success", "result": result}

    except Exception as e:
        await send_message(f"❌ Error in assistant workflow: {str(e)}", LogLevel.ERROR)
        return {"status": "error", "error": str(e)}
