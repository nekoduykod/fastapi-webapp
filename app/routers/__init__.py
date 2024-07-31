from fastapi import APIRouter


from .register import router as register_router
from .login import router as login_router
from .account import router as account_router
from .shortcut import router as shortcut_router
from .chatgpt import router as chatgpt_router


main_router = APIRouter()


main_router.include_router(register_router, tags=["register"])
main_router.include_router(login_router, tags=["login"])
main_router.include_router(account_router, tags=["account"])
main_router.include_router(shortcut_router, tags=["shortcut"])
main_router.include_router(chatgpt_router, tags=["chatgpt"])