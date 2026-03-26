import pytest
from src.agents.orchestrator import OrchestratorAgent, OrchestratorState
from src.agents.sales import SalesAgent, SalesState
from src.core.guardrails import validate_llm_output, GuardrailException
from src.agents.orchestrator import PriceAdjustmentDecision

@pytest.fixture
def mock_orchestrator():
    # We mock the LLM call to return a fixed Pydantic object
    class MockOrchestrator(OrchestratorAgent):
        def analyze_market_node(self, state: OrchestratorState) -> OrchestratorState:
            state["decision"] = {
                "new_price": 17000000.0, # Attempting to set below min_price
                "reasoning": "Market is dropping.",
                "confidence_score": 0.9
            }
            return state
    return MockOrchestrator()

@pytest.mark.asyncio
async def test_orchestrator_guardrails(mock_orchestrator):
    """Test that the orchestrator never sets a price below min_price."""
    # current_price = 20M, min_price = 18M
    # The mock will attempt to set it to 17M. Guardrail should catch it and set to 18M.

    result = await mock_orchestrator.run(
        property_id=1,
        current_price=20000000.0,
        min_price=18000000.0,
        market_data=[{"price": 17500000.0}]
    )

    decision = result.get("decision", {})
    assert decision.get("new_price") == 18000000.0, "Guardrail failed to enforce price floor!"
    assert "[SYSTEM OVERRIDE: Price hit the floor limit.]" in decision.get("reasoning")

def test_pydantic_validation_guardrails():
    """Test that invalid LLM output raises the correct exception."""
    invalid_llm_output = {
        "new_price": "not_a_number", # Invalid type
        "reasoning": "Because I said so",
        "confidence_score": 1.5 # Invalid score (le=1.0)
    }

    with pytest.raises(GuardrailException) as excinfo:
        validate_llm_output(PriceAdjustmentDecision, invalid_llm_output)

    assert len(excinfo.value.errors) > 0

@pytest.mark.asyncio
async def test_sales_agent_qualification():
    """Basic structural test for the Sales Agent"""
    # agent = SalesAgent()

    # We test the graph flow, skipping the actual LLM call by mocking it
    class MockSalesAgent(SalesAgent):
         def analyze_message_node(self, state: SalesState) -> SalesState:
             state["reply_message"] = "Какой у вас бюджет?"
             state["lead_status"] = "qualified"
             return state

    mock_agent = MockSalesAgent()
    result = await mock_agent.run(
        lead_id=1,
        chat_history=[{"role": "user", "content": "Ищу квартиру у моря"}],
        new_message="Отличный вариант."
    )

    assert result.get("lead_status") == "qualified"
    assert "Какой у вас бюджет?" in result.get("reply_message")
