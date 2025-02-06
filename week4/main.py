from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

app = FastAPI()

# 設定 SessionMiddleware（管理使用者狀態）
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",  # 加密 Session
    session_cookie="session_id"  # 設定 Cookie 名稱
)

# 設定模板引擎與靜態文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# 驗證使用者函數
def verify_user(username: str, password: str):
    if not username or not password:
        return False, "請輸入帳號與密碼"
    if username == "test" and password == "test":
        return True, ""
    return False, "帳號或密碼錯誤"


# 首頁
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 登入 API
@app.post("/signin")
async def signin(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    valid, msg = verify_user(username, password)
    if not valid:
        return RedirectResponse(f"/error?message={msg}", status_code=status.HTTP_302_FOUND)

    request.session["SIGNED_IN"] = True
    return RedirectResponse("/member", status_code=status.HTTP_302_FOUND)


# 會員專區
@app.get("/member")
async def member(request: Request):
    if not request.session.get("SIGNED_IN"):
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("member.html", {"request": request})


# 錯誤頁面
@app.get("/error")
async def error(request: Request, message: str):
    return templates.TemplateResponse("error.html", {"request": request, "message": message})


# 登出
@app.get("/signout")
async def signout(request: Request):
    request.session["SIGNED_IN"] = False
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


# 計算平方數
@app.get("/square/{number}")
async def square(request: Request, number: int):
    squared = number ** 2
    return templates.TemplateResponse("square.html", {"request": request, "number": number, "squared": squared})


# 啟動伺服器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
