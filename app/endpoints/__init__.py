from .ping import router as ping_router
from .user import router as user_router
from .auth import router as auth_router
from .course import router as course_router
from .practice import router as practice_router
from .language import router as lang_router
from .attempt import router as attempt_router
from .callback_server import router as callback_server_router
from .testcase import router as testcase_router
from .image import router as image_router


routers = [
    ping_router,
    user_router,
    auth_router,
    course_router,
    practice_router,
    lang_router,
    attempt_router,
    testcase_router,
    image_router,
]
