from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse
from Services.UserService import UserService

user_router = APIRouter()
user_service = UserService()

@user_router.get("/api/user/get", summary="Получить данные пользователя", description="",
                      tags=["Пользователи"])
async def get_user(
    login: str = Query(..., description="Имя пользователя")):

    if not login:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Логин не предоставлен"})
    
    response = await user_service.get_user(login)
    return JSONResponse(status_code=200, content=response.model_dump())


@user_router.post("/api/user/register", summary="Зарегистрировать нового пользователя", description="",
                      tags=["Пользователи"])
async def register(
    login: str = Query(..., description="Имя пользователя"), 
    password: str = Query(..., description="Пароль")):
    
    if not login or not password:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Логин или пароль не предоставлены"})
    
    await user_service.register_user(login, password)
    return JSONResponse(content={"status": "success", "message": "Пользователь успешно зарегистрирован", "userId": login})


@user_router.post("/api/user/login", summary="Залогиниться в приложении", description="",
                      tags=["Пользователи"])
async def login(
    login: str = Query(..., description="Имя пользователя"), 
    password: str = Query(..., description="Пароль")):
    
    if not login or not password:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Логин или пароль не предоставлены"})
    
    response = await user_service.login_user(login, password)
    return JSONResponse(content=response)


@user_router.patch("/api/user/update", summary="Обновить данные пользователя", description="",
                      tags=["Пользователи"])
async def update_user(
    login: str = Query(..., description="Имя пользователя"), 
    old_password: str = Query(..., description="Старый пароль"),
    new_password: str = Query(..., description="Новый пароль")):
    
    if not login or not new_password or not old_password:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Не предоставлены необходимые параметры"})
    
    response = await user_service.update_user_password(login, new_password, old_password)
    return JSONResponse(content=response)


@user_router.delete("/api/user/delete", summary="Удалить пользователя", description="",
                      tags=["Пользователи"])
async def delete_user(
    login: str = Query(..., description="Имя пользователя"), 
    password: str = Query(..., description="Пароль")):
    
    if not login or not password:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Логин или пароль не предоставлены"})
    
    response = await user_service.delete_user(login, password)
    return JSONResponse(content=response)
