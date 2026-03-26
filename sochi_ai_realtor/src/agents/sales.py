import os
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# State definition
class SalesState(TypedDict):
    lead_id: int
    chat_history: List[Dict[str, str]] # e.g., [{"role": "user", "content": "Привет, ищу квартиру"}, {"role": "assistant", "content": "..."}]
    new_message: str
    reply_message: str
    lead_status: str # "new", "qualified", "lost"
    logs: List[str]

# Define expected output format (Guardrails)
class ReplyDecision(BaseModel):
    reply_text: str = Field(description="The response to send to the user on WhatsApp or Telegram.")
    action: str = Field(description="Action to take: 'reply', 'qualify_lead', 'close_deal', or 'escalate_to_human'.")
    confidence: float = Field(ge=0.0, le=1.0)

# The Sales Agent logic
class SalesAgent:
    def __init__(self):
        # Fallback to a fake key for testing if OPENAI_API_KEY is not set
        api_key = os.environ.get("OPENAI_API_KEY", "sk-fake-key-for-testing")

        # Claude 3.5 Sonnet is better for human-like dialog, but we'll use GPT-4o as default
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=api_key)

        self.parser = PydanticOutputParser(pydantic_object=ReplyDecision)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты — лучший в мире ИИ-Брокер (Sales Agent) по продаже элитной недвижимости в Сочи.\n"
                       "Твоя задача — общаться с потенциальными клиентами в WhatsApp, квалифицировать их и назначать показы.\n"
                       "Если не знаешь ответа на вопрос о документах или ЖК, отвечай, что уточнишь у застройщика или юриста.\n\n"
                       "Формат ответа:\n{format_instructions}"),
            ("user", "История диалога:\n{chat_history}\n\n"
                     "Новое сообщение от клиента:\n{new_message}\n\n"
                     "Твой ответ и действие:")
        ])

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        builder = StateGraph(SalesState)

        # Nodes
        builder.add_node("analyze_message", self.analyze_message_node)
        builder.add_node("format_reply", self.format_reply_node)

        # Edges
        builder.add_edge(START, "analyze_message")
        builder.add_edge("analyze_message", "format_reply")
        builder.add_edge("format_reply", END)

        return builder.compile()

    def analyze_message_node(self, state: SalesState) -> SalesState:
        """Analyzes incoming message and history to generate a response via LLM."""
        chain = self.prompt | self.llm | self.parser

        # Format chat history
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state["chat_history"]])

        try:
            decision: ReplyDecision = chain.invoke({
                "chat_history": history_str,
                "new_message": state["new_message"],
                "format_instructions": self.parser.get_format_instructions()
            })

            state["reply_message"] = decision.reply_text
            state["logs"].append(f"LLM Action: {decision.action}, Confidence: {decision.confidence}")

            if decision.action == "qualify_lead":
                state["lead_status"] = "qualified"
            elif decision.action == "close_deal":
                state["lead_status"] = "deal_closed"

        except Exception as e:
            # Fallback
            state["logs"].append(f"Error during message analysis: {str(e)}")
            state["reply_message"] = "Извините, сейчас я уточняю информацию. Вернусь к вам через пару минут!"
            state["lead_status"] = state.get("lead_status", "new")

        return state

    def format_reply_node(self, state: SalesState) -> SalesState:
        """Final formatting and safety checks before sending to user."""
        # Simple safety check: do not send empty messages
        if not state.get("reply_message"):
            state["reply_message"] = "Секунду, проверяю информацию по базе..."

        state["chat_history"].append({"role": "user", "content": state["new_message"]})
        state["chat_history"].append({"role": "assistant", "content": state["reply_message"]})

        return state

    async def run(self, lead_id: int, chat_history: List[Dict], new_message: str) -> Dict:
        """Entry point to execute the sales logic for a specific lead."""
        initial_state: SalesState = {
            "lead_id": lead_id,
            "chat_history": chat_history,
            "new_message": new_message,
            "reply_message": "",
            "lead_status": "new", # Default to new, will be updated by agent
            "logs": ["Sales run started."]
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
