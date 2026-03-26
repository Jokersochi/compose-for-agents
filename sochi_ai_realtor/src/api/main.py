from fastapi import FastAPI, BackgroundTasks, Depends, status

from src.core.logger import configure_logging, log
from src.agents.orchestrator import OrchestratorAgent
from src.agents.sales import SalesAgent
from src.infrastructure.database import get_session
from src.infrastructure.scraper import CompetitorScraper
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Request models for webhooks
class IncomingMessage(BaseModel):
    phone_number: str
    message: str
    channel: str = "whatsapp"

class ManualApproveRequest(BaseModel):
    property_id: int
    approved_price: float

app = FastAPI(title="Sochi AI Realtor API", description="Autonomous real estate multi-agent framework.")

# Setup logging on startup
@app.on_event("startup")
async def startup_event():
    configure_logging()
    log.info("system_startup", message="Initializing AI framework and connections...")
    # Initialize DB connection, Qdrant, etc here

# Core dependency injection
async def get_orchestrator():
    return OrchestratorAgent()

async def get_sales_agent():
    return SalesAgent()

# Endpoints

@app.post("/webhooks/message", status_code=status.HTTP_200_OK)
async def receive_message(
    payload: IncomingMessage,
    background_tasks: BackgroundTasks,
    sales_agent: SalesAgent = Depends(get_sales_agent),
    db: AsyncSession = Depends(get_session)
):
    """
    Webhook to receive messages from Green API (WhatsApp) or Telegram.
    Processes the message asynchronously through the Sales Agent.
    """
    log.info("incoming_message", phone=payload.phone_number, channel=payload.channel)

    # In reality, fetch lead and chat history from DB
    # For MVP, we pass dummy history
    chat_history: list = []

    async def process_in_background():
        result = await sales_agent.run(
            lead_id=1, # Mock ID
            chat_history=chat_history,
            new_message=payload.message
        )
        reply = result.get("reply_message")

        # Here we would send `reply` back via HTTP to WhatsApp/Telegram API
        log.info("message_processed", lead_id=1, reply_sent=reply)

    background_tasks.add_task(process_in_background)
    return {"status": "accepted"}

@app.post("/orchestrator/run/{property_id}")
async def run_orchestrator(
    property_id: int,
    background_tasks: BackgroundTasks,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session)
):
    """
    Manually trigger the Chief AI Architect to analyze market and update price.
    """
    # Fetch current property details from DB
    # current_price = db_property.price
    # min_price = db_property.min_price
    current_price = 20000000.0
    min_price = 18000000.0

    # Run RPA scraper to get market data
    scraper = CompetitorScraper(headless=True)

    async def analyze_and_decide():
        market_data = await scraper.scrape_avito_sochi(search_query="квартира Сочи бизнес класс")

        # Pass to Orchestrator
        decision_result = await orchestrator.run(
            property_id=property_id,
            current_price=current_price,
            min_price=min_price,
            market_data=market_data
        )

        decision = decision_result.get("decision", {})
        new_price = decision.get("new_price")

        log.info("orchestrator_decision_made", property_id=property_id, old_price=current_price, new_price=new_price, reason=decision.get("reasoning"))

        # In reality: update DB or send notification to human for approval (Human-in-the-loop)

    background_tasks.add_task(analyze_and_decide)
    return {"status": "analysis_started"}

@app.post("/admin/approve-price")
async def approve_price_change(request: ManualApproveRequest, db: AsyncSession = Depends(get_session)):
    """Human-in-the-loop endpoint. Used when the AI Director requests a price drop that needs manual approval."""
    log.info("price_change_approved", property_id=request.property_id, new_price=request.approved_price)
    # Update DB here
    return {"status": "price_updated"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
