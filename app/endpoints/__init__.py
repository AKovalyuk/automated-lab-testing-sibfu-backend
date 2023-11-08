from .ping import router as ping_router
from .user import router as user_router
from .auth import router as auth_router
from .course import router as course_router
from .task import router as task_router
from .practice import router as practice_router
from .language import router as lang_router


routers = [
    ping_router,
    user_router,
    auth_router,
    course_router,
    task_router,
    practice_router,
    lang_router,
]
