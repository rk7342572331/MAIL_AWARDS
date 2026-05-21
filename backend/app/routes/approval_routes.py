from fastapi import APIRouter

from pydantic import BaseModel

from app.services.approval_service import (

    get_pending_approvals,

    approve_employee,

    reject_employee

)


router = APIRouter()


# ==========================================
# REJECTION MODEL
# ==========================================

class RejectRequest(BaseModel):

    record_id: int

    rejection_reason: str


# ==========================================
# GET PENDING APPROVALS
# ==========================================

@router.get(
    "/pending-approvals"
)

def fetch_pending_approvals():

    data = get_pending_approvals()

    return {

        "success": True,

        "data": data
    }


# ==========================================
# APPROVE EMPLOYEE
# ==========================================

@router.post(
    "/approve/{record_id}"
)

def approve(record_id: int):

    response = approve_employee(
        record_id
    )

    return {

        "success": True,

        "message":
            "Employee Approved",

        "data":
            response
    }


# ==========================================
# REJECT EMPLOYEE
# ==========================================

@router.post(
    "/reject"
)

def reject(

    request: RejectRequest

):

    response = reject_employee(

        request.record_id,

        request.rejection_reason

    )

    return {

        "success": True,

        "message":
            "Employee Rejected",

        "data":
            response
    }