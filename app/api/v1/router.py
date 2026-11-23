from fastapi import APIRouter

from app.modules.analytics.router import router as analytics_router
from app.modules.bookings.router import router as bookings_router
from app.modules.bookings.router import router as bookings_router
from app.modules.applications.router import router as applications_router
from app.modules.assessments.router import router as assessments_router
from app.modules.attendance.router import router as attendance_router
from app.modules.audit.router import router as audit_router
from app.modules.certificates.router import router as certificates_router
from app.modules.classes.router import router as classes_router
from app.modules.cms.router import router as cms_router
from app.modules.community.router import router as community_router
from app.modules.consent.router import router as consent_router
from app.modules.courses.router import router as courses_router
from app.modules.creative_arts.router import router as creative_arts_router
from app.modules.discussions.router import router as discussions_router
from app.modules.donations.router import router as donations_router
from app.modules.education.router import router as education_router
from app.modules.enrolments.router import router as enrolments_router
from app.modules.events.router import router as events_router
from app.modules.expenses.router import router as expenses_router
from app.modules.finance.router import router as finance_router
from app.modules.guardians.router import router as guardians_router
from app.modules.identity.router import router as identity_router
from app.modules.instruments.router import router as instruments_router
from app.modules.library.router import router as library_router
from app.modules.media.router import router as media_router
from app.modules.messaging.router import router as messaging_router
from app.modules.moderation.router import router as moderation_router
from app.modules.navigation.router import router as navigation_router
from app.modules.notifications.router import router as notifications_router
from app.modules.organisation.router import router as organisation_router
from app.modules.participants.router import router as participants_router
from app.modules.payments.router import router as payments_router
from app.modules.programmes.router import router as programmes_router
from app.modules.projects.router import router as projects_router
from app.modules.publications.router import router as publications_router
from app.modules.referrals.router import router as referrals_router
from app.modules.reporting.router import router as reporting_router
from app.modules.research.router import router as research_router
from app.modules.roles_permissions.router import router as roles_router
from app.modules.safeguarding.router import router as safeguarding_router
from app.modules.staff.router import router as staff_router
from app.modules.users.router import router as users_router
from app.modules.vocational_training.router import router as vocational_router

v1_router = APIRouter()

v1_router.include_router(identity_router,       prefix="/auth",             tags=["Authentication"])
v1_router.include_router(users_router,          prefix="/users",            tags=["Users"])
v1_router.include_router(roles_router,          prefix="/roles",            tags=["Roles & Permissions"])
v1_router.include_router(organisation_router,   prefix="/organisation",     tags=["Organisation"])
v1_router.include_router(staff_router,          prefix="/staff",            tags=["Staff"])
v1_router.include_router(participants_router,   prefix="/participants",      tags=["Participants"])
v1_router.include_router(guardians_router,      prefix="/guardians",        tags=["Guardians"])
v1_router.include_router(programmes_router,     prefix="/programmes",       tags=["Programmes"])
v1_router.include_router(projects_router,       prefix="/projects",         tags=["Projects"])
v1_router.include_router(applications_router,   prefix="/applications",     tags=["Applications"])
v1_router.include_router(enrolments_router,     prefix="/enrolments",       tags=["Enrolments"])
v1_router.include_router(education_router,      prefix="/education",        tags=["Education"])
v1_router.include_router(courses_router,        prefix="/courses",          tags=["Courses"])
v1_router.include_router(classes_router,        prefix="/classes",          tags=["Classes"])
v1_router.include_router(attendance_router,     prefix="/attendance",       tags=["Attendance"])
v1_router.include_router(assessments_router,    prefix="/assessments",      tags=["Assessments"])
v1_router.include_router(certificates_router,   prefix="/certificates",     tags=["Certificates"])
v1_router.include_router(creative_arts_router,  prefix="/creative-arts",    tags=["Creative Arts"])
v1_router.include_router(vocational_router,     prefix="/vocational",       tags=["Vocational Training"])
v1_router.include_router(instruments_router,    prefix="/instruments",      tags=["Instruments"])
v1_router.include_router(events_router,         prefix="/events",           tags=["Events"])
v1_router.include_router(community_router,      prefix="/community",        tags=["Community"])
v1_router.include_router(discussions_router,    prefix="/discussions",      tags=["Discussions"])
v1_router.include_router(moderation_router,     prefix="/moderation",       tags=["Moderation"])
v1_router.include_router(safeguarding_router,   prefix="/safeguarding",     tags=["Safeguarding"])
v1_router.include_router(consent_router,        prefix="/consent",          tags=["Consent"])
v1_router.include_router(referrals_router,      prefix="/referrals",        tags=["Referrals"])
v1_router.include_router(research_router,       prefix="/research",         tags=["Research"])
v1_router.include_router(library_router,        prefix="/library",          tags=["Library"])
v1_router.include_router(publications_router,   prefix="/publications",     tags=["Publications"])
v1_router.include_router(cms_router,            prefix="/cms",              tags=["CMS"])
v1_router.include_router(media_router,          prefix="/media",            tags=["Media"])
v1_router.include_router(navigation_router,     prefix="/navigation",       tags=["Navigation"])
v1_router.include_router(finance_router,        prefix="/finance",          tags=["Finance"])
v1_router.include_router(donations_router,      prefix="/donations",        tags=["Donations"])
v1_router.include_router(payments_router,       prefix="/payments",         tags=["Payments"])
v1_router.include_router(expenses_router,       prefix="/expenses",         tags=["Expenses"])
v1_router.include_router(notifications_router,  prefix="/notifications",    tags=["Notifications"])
v1_router.include_router(messaging_router,      prefix="/messaging",        tags=["Messaging"])
v1_router.include_router(reporting_router,      prefix="/reporting",        tags=["Reporting"])
v1_router.include_router(analytics_router,      prefix="/analytics",        tags=["Analytics"])
v1_router.include_router(audit_router,          prefix="/audit",            tags=["Audit"])
v1_router.include_router(bookings_router,       prefix="/bookings",         tags=["Bookings"])
