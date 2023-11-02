from .ping import router as ping_router
from .user import router as user_router
from .auth import router as auth_router
from .course import router as course_router


routers = [
    ping_router,
    user_router,
    auth_router,
    course_router,
]
