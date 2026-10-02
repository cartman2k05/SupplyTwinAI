from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.orders import router as orders_router
from backend.app.api.v1.shipments import router as shipments_router
from backend.app.api.v1.inventory import router as inventory_router
from backend.app.api.v1.suppliers import router as suppliers_router
from backend.app.api.v1.etl import router as etl_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.simulation import router as simulation_router
from backend.app.api.v1.graph import router as graph_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.agents import router as agents_router
from backend.app.api.v1.recommendations import router as recommendations_router
from backend.app.api.v1.reports import router as reports_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(shipments_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(suppliers_router)
api_v1_router.include_router(etl_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(simulation_router)
api_v1_router.include_router(graph_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(reports_router)
