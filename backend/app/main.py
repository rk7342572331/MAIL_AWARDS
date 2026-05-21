from fastapi import FastAPI


# ==========================================
# IMPORT ROUTERS
# ==========================================

from app.routes.email_routes import (
    router as email_router
)

from app.routes.approval_routes import (
    router as approval_router
)

from app.routes.voucher_routes import (
    router as voucher_router
)

from app.routes.certificate_routes import (
    router as certificate_router
)
from app.routes.mail_routes import router as mail_router
from app.routes.data_management_routes import router as data_management_router
from app.routes.dashboard_routes import router as dashboard_router

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(

    title="Mail Awards System"

)


# ==========================================
# INCLUDE ROUTERS
# ==========================================

app.include_router(
    email_router
)

app.include_router(
    approval_router
)

app.include_router(
    voucher_router
)

app.include_router(
    certificate_router
)

app.include_router(
    mail_router
)

app.include_router(
    data_management_router
)

app.include_router(
    dashboard_router
)

# ==========================================
# ROOT
# ==========================================

@app.get("/")

def root():

    return {

        "message":
            "Mail Awards Backend Running"

    }