from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.auth.dependencies import get_current_user
from backend.app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/export/{resource}")
def export_csv_report(
    resource: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download CSV report export for operational resource (§4.10 REQ-1).
    Supported resources: orders, shipments, inventory, suppliers, recommendations, audit.
    """
    res = resource.lower()

    if res == "orders":
        csv_content = report_service.export_orders_csv(db)
    elif res == "shipments":
        csv_content = report_service.export_shipments_csv(db)
    elif res == "inventory":
        csv_content = report_service.export_inventory_csv(db)
    elif res == "suppliers":
        csv_content = report_service.export_suppliers_csv(db)
    elif res == "recommendations":
        csv_content = report_service.export_recommendations_csv(db)
    elif res == "audit":
        csv_content = report_service.export_audit_csv(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported report resource '{resource}'. Supported: orders, shipments, inventory, suppliers, recommendations, audit"
        )

    filename = f"supplytwin_{res}_report.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
