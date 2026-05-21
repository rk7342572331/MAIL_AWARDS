from fastapi import APIRouter

from app.services.certificate_service import (
    generate_all_certificates
)


router = APIRouter()


# ==========================================
# GENERATE CERTIFICATES
# ==========================================

@router.post(
    "/generate-certificates"
)

def generate_certificates():

    result = (
        generate_all_certificates()
    )

    return result