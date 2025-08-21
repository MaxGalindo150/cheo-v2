"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import UTC, datetime
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from react_agent.context import Context
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model


def _generate_state_summary(state: State) -> str:
    """Generate a summary of the current state for the prompt."""
    summary_parts = []
    
    # Authentication status
    if state.user_email and state.user_cedula:
        if state.is_authenticated:
            summary_parts.append(f"✅ USUARIO AUTENTICADO: {state.user_email} (Cédula: {state.user_cedula})")
        else:
            summary_parts.append(f"⚠️ CREDENCIALES DISPONIBLES: {state.user_email} (Cédula: {state.user_cedula}) - NECESITA AUTENTICACIÓN")
    else:
        summary_parts.append("❌ AUTENTICACIÓN PENDIENTE: Email y cédula requeridos")
    
    # Receipt validation status
    if state.payment_receipt_validated:
        summary_parts.append("✅ COMPROBANTE VALIDADO: Imagen del comprobante verificada")
    else:
        summary_parts.append("❌ COMPROBANTE PENDIENTE: Requiere imagen del comprobante")
    
    # Bank validation status
    if state.bank_validated and state.payment_bank:
        summary_parts.append(f"✅ BANCO VALIDADO: {state.payment_bank}")
    else:
        summary_parts.append("❌ BANCO PENDIENTE: Requiere validación del banco")
    
    # Payment data extraction status
    if state.payment_amount > 0 and state.payment_reference and state.payment_date:
        summary_parts.append(f"✅ DATOS EXTRAÍDOS: Monto: ${state.payment_amount}, Referencia: {state.payment_reference}, Fecha: {state.payment_date}")
    else:
        summary_parts.append("❌ EXTRACCIÓN DE DATOS PENDIENTE: Requiere monto, referencia y fecha")
    
    # Order validation status
    if state.order_validated and state.payment_order:
        summary_parts.append(f"✅ ORDEN VALIDADA: {state.payment_order}")
    else:
        summary_parts.append("❌ ORDEN PENDIENTE: Requiere número de orden")
    
    # Payment search status
    if state.payment_found and state.payment_status:
        summary_parts.append(f"✅ PAGO ENCONTRADO: Estado: {state.payment_status}")
    else:
        summary_parts.append("❌ BÚSQUEDA DE PAGO PENDIENTE: Requiere búsqueda en el sistema")
    
    # Escalation status
    if state.needs_escalation:
        if state.sent_to_team_id:
            summary_parts.append(f"🚨 CASO ESCALADO: Enviado al equipo {state.sent_to_team_id}. Razón: {state.escalation_reason}")
        else:
            summary_parts.append(f"⚠️ ESCALACIÓN REQUERIDA: {state.escalation_reason}")
    
    return "\n".join(summary_parts)


# Define the function that calls the model


async def call_model(
    state: State, runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(runtime.context.model).bind_tools(TOOLS)

    # Generate state summary for the prompt
    state_summary = _generate_state_summary(state)
    
    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = runtime.context.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat(),
        state_summary=state_summary
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}


# Define a new graph

builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# Define the two nodes we will cycle between
builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS))

# Set the entrypoint as `call_model`
# This means that this node is the first one called
builder.add_edge("__start__", "call_model")


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"


# Add a conditional edge to determine the next step after `call_model`
builder.add_conditional_edges(
    "call_model",
    # After call_model finishes running, the next node(s) are scheduled
    # based on the output from route_model_output
    route_model_output,
)

# Add a normal edge from `tools` to `call_model`
# This creates a cycle: after using tools, we always return to the model
builder.add_edge("tools", "call_model")

# Compile the builder into an executable graph
graph = builder.compile(name="ReAct Agent")
