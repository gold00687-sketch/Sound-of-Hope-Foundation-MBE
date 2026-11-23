import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import require_permission
from app.modules.courses.schemas import (
    CourseCreate, CourseResponse, CourseUpdate,
    LessonCreate, LessonResponse,
    ModuleCreate, ModuleResponse,
)
from app.modules.courses.service import CourseService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.get("", response_model=Page[CourseResponse], dependencies=[require_permission(Permission.COURSE_READ)])
async def list_courses(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    programme_id: uuid.UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
):
    items, total = await CourseService(session).list_courses(
        pagination.limit, pagination.offset, programme_id, is_active
    )
    return Page.create(items, pagination, total)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.COURSE_MANAGE)])
async def create_course(body: CourseCreate, session: SessionDep):
    return await CourseService(session).create(body)


@router.get("/{course_id}", response_model=CourseResponse, dependencies=[require_permission(Permission.COURSE_READ)])
async def get_course(course_id: uuid.UUID, session: SessionDep):
    return await CourseService(session).get(course_id)


@router.patch("/{course_id}", response_model=CourseResponse, dependencies=[require_permission(Permission.COURSE_MANAGE)])
async def update_course(course_id: uuid.UUID, body: CourseUpdate, session: SessionDep):
    return await CourseService(session).update(course_id, body)


@router.post("/{course_id}/modules", response_model=ModuleResponse,
             status_code=status.HTTP_201_CREATED, dependencies=[require_permission(Permission.COURSE_MANAGE)])
async def add_module(course_id: uuid.UUID, body: ModuleCreate, session: SessionDep):
    return await CourseService(session).add_module(course_id, body)


@router.post("/modules/{module_id}/lessons", response_model=LessonResponse,
             status_code=status.HTTP_201_CREATED, dependencies=[require_permission(Permission.COURSE_MANAGE)])
async def add_lesson(module_id: uuid.UUID, body: LessonCreate, session: SessionDep):
    return await CourseService(session).add_lesson(module_id, body)


@router.post("/lessons/{lesson_id}/publish", response_model=LessonResponse,
             dependencies=[require_permission(Permission.COURSE_MANAGE)])
async def publish_lesson(lesson_id: uuid.UUID, session: SessionDep):
    return await CourseService(session).publish_lesson(lesson_id)
