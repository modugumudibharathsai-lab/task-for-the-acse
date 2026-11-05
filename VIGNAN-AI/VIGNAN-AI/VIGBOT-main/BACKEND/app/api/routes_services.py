from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import ServiceRequestCreate, ServiceRequestResponse
from app.database import DataRepository, DatabaseSession
from app.security import get_current_student

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])

@router.post("", response_model=ServiceRequestResponse)
async def create_service_request(
    req: ServiceRequestCreate,
    current_student: dict = Depends(get_current_student)
):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    record = DataRepository.create_service_request(session, req.model_dump())
    return ServiceRequestResponse(**record)

@router.get("", response_model=List[ServiceRequestResponse])
async def list_my_service_requests(current_student: dict = Depends(get_current_student)):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    requests = DataRepository.list_service_requests(session)
    return [ServiceRequestResponse(**r) for r in requests]
