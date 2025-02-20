from fastapi import FastAPI, Request, Form, Path, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
import mysql.connector
from mysql.connector import pooling
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# 初始化 FastAPI
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# 設定模板引擎與靜態文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 建立 MySQL 連線池
db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "12345678"),
    database=os.getenv("DB_NAME", "website"),
)

# 密碼加密設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_db_connection():
    """從連線池獲取 MySQL 連線"""
    return db_pool.get_connection()


def get_session_user(request: Request):
    """獲取當前登入用戶的資訊"""
    return {
        "SIGNED_IN": request.session.get("SIGNED_IN"),
        "USER_ID": request.session.get("USER_ID"),
        "USER_NAME": request.session.get("USER_NAME"),
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if get_session_user(request)["SIGNED_IN"]:
        return RedirectResponse("/member", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/signup")
async def signup(name: str = Form(...), username: str = Form(...), password: str = Form(...)):
    if not all([name.strip(), username.strip(), password.strip()]):
        return RedirectResponse("/error?message=所有欄位皆為必填", status_code=status.HTTP_302_FOUND)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM member WHERE username = %s", (username,))
        if cursor.fetchone():
            return RedirectResponse("/error?message=帳號已經被註冊", status_code=status.HTTP_302_FOUND)

        cursor.execute("INSERT INTO member (name, username, password) VALUES (%s, %s, %s)",
                       (name, username, hash_password(password)))
        conn.commit()

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/signin")
async def signin(request: Request, username: str = Form(...), password: str = Form(...)):
    if not all([username.strip(), password.strip()]):
        return RedirectResponse("/error?message=所有欄位皆為必填", status_code=status.HTTP_302_FOUND)

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, password FROM member WHERE username = %s", (username,))
        user = cursor.fetchone()

    if not user or not verify_password(password, user["password"]):
        return RedirectResponse("/error?message=帳號或密碼錯誤", status_code=status.HTTP_302_FOUND)

    request.session.update({"SIGNED_IN": True, "USER_ID": user["id"], "USER_NAME": user["name"]})
    return RedirectResponse("/member", status_code=status.HTTP_302_FOUND)


@app.get("/member", response_class=HTMLResponse)
async def member(request: Request):
    session_user = get_session_user(request)
    if not session_user["SIGNED_IN"]:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT message.id, message.content, message.member_id, member.name "
            "FROM message JOIN member ON message.member_id = member.id"
        )
        messages = cursor.fetchall()

    return templates.TemplateResponse("member.html", {
        "request": request,
        "name": session_user["USER_NAME"],
        "messages": messages,
        "USER_ID": session_user["USER_ID"]
    })


@app.get("/error", response_class=HTMLResponse)
async def error(request: Request, message: str = "發生未知錯誤"):
    """顯示錯誤頁面，錯誤訊息來自 URL Query String"""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "message": message
    })


@app.get("/signout")
async def signout(request: Request):
    request.session.clear()
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session_id")  # 確保 Cookie 被刪除
    return response


@app.post("/createMessage")
async def create_message(request: Request, content: str = Form(...)):
    session_user = get_session_user(request)
    if not session_user["SIGNED_IN"]:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    if not content.strip():
        return RedirectResponse("/error?message=留言不能為空", status_code=status.HTTP_302_FOUND)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO message (member_id, content) VALUES (%s, %s)",
                       (session_user["USER_ID"], content))
        conn.commit()

    return RedirectResponse("/member", status_code=status.HTTP_302_FOUND)


@app.post("/deleteMessage/{message_id}")
async def delete_message(request: Request, message_id: int = Path(..., gt=0)):
    session_user = get_session_user(request)

    if not session_user["SIGNED_IN"]:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT member_id FROM message WHERE id = %s", (message_id,))
        message = cursor.fetchone()

        if not message or message["member_id"] != session_user["USER_ID"]:
            return RedirectResponse("/error?message=無權刪除此留言", status_code=status.HTTP_302_FOUND)

        cursor.execute("DELETE FROM message WHERE id = %s", (message_id,))
        conn.commit()

    return RedirectResponse("/member", status_code=status.HTTP_302_FOUND)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
