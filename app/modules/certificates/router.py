import uuid

from fastapi import APIRouter, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.certificates.schemas import CertificateIssue, CertificateResponse, RevokeRequest
from app.modules.certificates.service import CertificateService

router = APIRouter()


@router.post("", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.CERTIFICATE_ISSUE)])
async def issue_certificate(body: CertificateIssue, session: SessionDep, current_user: CurrentUser):
    return await CertificateService(session).issue(body, current_user.id)


@router.get("/verify/{certificate_number}", response_model=CertificateResponse)
async def verify_certificate(certificate_number: str, session: SessionDep):
    return await CertificateService(session).verify(certificate_number)


@router.get("/{cert_id}", response_model=CertificateResponse,
            dependencies=[require_permission(Permission.ASSESSMENT_READ)])
async def get_certificate(cert_id: uuid.UUID, session: SessionDep):
    return await CertificateService(session).get(cert_id)


@router.get("/participant/{participant_id}", response_model=list[CertificateResponse],
            dependencies=[require_permission(Permission.ASSESSMENT_READ)])
async def participant_certificates(participant_id: uuid.UUID, session: SessionDep):
    return await CertificateService(session).list_for_participant(participant_id)


@router.post("/{cert_id}/revoke", response_model=CertificateResponse,
             dependencies=[require_permission(Permission.CERTIFICATE_ISSUE)])
async def revoke_certificate(cert_id: uuid.UUID, body: RevokeRequest, session: SessionDep):
    return await CertificateService(session).revoke(cert_id, body.reason)
