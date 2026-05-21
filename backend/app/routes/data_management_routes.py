from fastapi import APIRouter

from app.db.database import supabase


router = APIRouter()


# ==========================================
# GET TABLE DATA
# ==========================================

@router.get(
    "/table-data/{table_name}"
)

def get_table_data(

    table_name: str

):

    response = (

        supabase
        .table(table_name)

        .select("*")

        .execute()
    )

    return response.data


# ==========================================
# UPDATE RECORD
# ==========================================

@router.put(
    "/update-record/{table_name}/{record_id}"
)

def update_record(

    table_name: str,

    record_id: int,

    payload: dict

):

    response = (

        supabase
        .table(table_name)

        .update(payload)

        .eq(
            "id",
            record_id
        )

        .execute()
    )

    return {

        "success": True,

        "message":
            "Record updated",

        "data":
            response.data
    }


# ==========================================
# DELETE RECORD
# ==========================================

@router.delete(
    "/delete-record/{table_name}/{record_id}"
)

def delete_record(

    table_name: str,

    record_id: int

):

    supabase.table(
        table_name
    ).delete().eq(

        "id",

        record_id

    ).execute()

    return {

        "success": True,

        "message":
            "Record deleted"
    }