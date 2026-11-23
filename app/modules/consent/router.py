import uuid

from fastapi import APIRouter, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.consent.schemas import ConsentCreate, ConsentResponse, ConsentWithdraw
from app.modules.consent.service import ConsentService

router = APIRouter()


@router.post("", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.CONSENT_MANAGE)])
async def record_consent(body: ConsentCreate, session: SessionDep):
    return await ConsentService(session).record(body)


@router.get("/participant/{participant_id}", response_model=list[ConsentResponse],
            dependencies=[require_permission(Permission.CONSENT_READ)])
async def participant_consents(participant_id: uuid.UUID, session: SessionDep):
    return await ConsentService(session).list_for_participant(participant_id)


@router.get("/{consent_id}", response_model=ConsentResponse,
            dependencies=[require_permission(Permission.CONSENT_READ)])
async def get_consent(consent_id: uuid.UUID, session: SessionDep):
    return await ConsentService(session).get(consent_id)


@router.post("/{consent_id}/withdraw", response_model=ConsentResponse,
             dependencies=[require_permission(Permission.CONSENT_MANAGE)])
async def withdraw_consent(consent_id: uuid.UUID, body: ConsentWithdraw, session: SessionDep):
    return await ConsentService(session).withdraw(consent_id, body)
