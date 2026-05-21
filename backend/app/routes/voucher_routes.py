from fastapi import APIRouter

from app.services.voucher_allocator_service import (
    allocate_vouchers
)


router = APIRouter()


# ==========================================
# ALLOCATE VOUCHERS
# ==========================================

@router.post(
    "/allocate-vouchers"
)

def allocate():

    result = allocate_vouchers()

    return result