from fastapi import APIRouter

router = APIRouter(prefix="/{task_id}/comments", tags=["Comments"])
