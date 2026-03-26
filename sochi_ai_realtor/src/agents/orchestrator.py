from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

import os

# Define the state for the Orchestrator
class OrchestratorState(TypedDict):
    property_id: int
    current_price: float
    min_price: float
    market_data: List[Dict[str, Any]] # e.g., [{"price": 100, "area": 50}, ...]
    decision: Dict[str, Any] # The final decision made by the agent
    logs: List[str]

# Define the expected output format using Pydantic (Guardrails)
class PriceAdjustmentDecision(BaseModel):
    new_price: float = Field(description="The newly decided price for the property. Must not be below min_price.")
    reasoning: str = Field(description="Detailed explanation of why the price was changed or kept the same based on market data.")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the decision, from 0 to 1")

# The Orchestrator Agent logic
class OrchestratorAgent:
    def __init__(self):
        # Fallback to a fake key for testing if OPENAI_API_KEY is not set
        api_key = os.environ.get("OPENAI_API_KEY", "sk-fake-key-for-testing")

        # Using GPT-4o as requested, parsing Pydantic natively
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=api_key)

        self.parser = PydanticOutputParser(pydantic_object=PriceAdjustmentDecision)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты — Главный ИИ-Директор (Orchestrator) агенства недвижимости в Сочи.\n"
                       "Твоя задача — анализировать рынок конкурентов и управлять ценой нашего объекта.\n"
                       "Никогда не ставь цену ниже {min_price} руб.\n\n"
                       "Формат ответа:\n{format_instructions}"),
            ("user", "Текущая цена объекта: {current_price} руб.\n"
                     "Данные конкурентов (похожие объекты в Сочи):\n{market_data}\n"
                     "Прими решение о новой цене.")
        ])

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        builder = StateGraph(OrchestratorState)

        # Nodes
        builder.add_node("analyze_market", self.analyze_market_node)
        builder.add_node("apply_guardrails", self.apply_guardrails_node)

        # Edges
        builder.add_edge(START, "analyze_market")
        builder.add_edge("analyze_market", "apply_guardrails")
        builder.add_edge("apply_guardrails", END)

        return builder.compile()

    def analyze_market_node(self, state: OrchestratorState) -> OrchestratorState:
        """Analyzes market data and uses LLM to decide on a new price."""
        chain = self.prompt | self.llm | self.parser

        try:
            decision: PriceAdjustmentDecision = chain.invoke({
                "current_price": state["current_price"],
                "min_price": state["min_price"],
                "market_data": state["market_data"],
                "format_instructions": self.parser.get_format_instructions()
            })

            state["decision"] = decision.model_dump()
            state["logs"].append(f"LLM proposed new price: {decision.new_price}")
        except Exception as e:
            # Fallback in case of LLM error
            state["logs"].append(f"Error during market analysis: {str(e)}")
            state["decision"] = {
                "new_price": state["current_price"],
                "reasoning": "Fallback to current price due to LLM error.",
                "confidence_score": 0.0
            }

        return state

    def apply_guardrails_node(self, state: OrchestratorState) -> OrchestratorState:
        """Enforces hard business rules (e.g., price floor) overriding LLM if necessary."""
        decision = state.get("decision", {})
        proposed_price = decision.get("new_price", state["current_price"])

        if proposed_price < state["min_price"]:
            state["logs"].append(f"Guardrail triggered! Proposed price {proposed_price} is below min_price {state['min_price']}. Reverting to min_price.")
            decision["new_price"] = state["min_price"]
            decision["reasoning"] += " [SYSTEM OVERRIDE: Price hit the floor limit.]"
            state["decision"] = decision

        return state

    async def run(self, property_id: int, current_price: float, min_price: float, market_data: List[Dict]) -> Dict:
        """Entry point to execute the orchestrator logic for a specific property."""
        initial_state: OrchestratorState = {
            "property_id": property_id,
            "current_price": current_price,
            "min_price": min_price,
            "market_data": market_data,
            "decision": {},
            "logs": ["Orchestrator run started."]
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
