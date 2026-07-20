import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config
from app.database import get_session, init_db
from app.models import Account, Tweet
from app.scheduler import start_scheduler, stop_scheduler
from app.scraper import scraper
from app.tracker_service import add_account, poll_all_accounts, remove_account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tracker.main")

templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic(auto_error=False)


def require_auth(credentials: HTTPBasicCredentials | None = Depends(security)) -> None:
    if not config.BASIC_AUTH_PASSWORD:
        return
    unauthorized = HTTPException(
        status_code=401, detail="Credenciales inválidas", headers={"WWW-Authenticate": "Basic"}
    )
    if credentials is None:
        raise unauthorized
    user_ok = secrets.compare_digest(credentials.username, config.BASIC_AUTH_USER)
    pass_ok = secrets.compare_digest(credentials.password, config.BASIC_AUTH_PASSWORD)
    if not (user_ok and pass_ok):
        raise unauthorized


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        await scraper.login()
    except Exception:
        logger.exception("No se pudo iniciar sesión en Twitter al arrancar. Revisa las credenciales en .env.")
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Twitter Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, _: None = Depends(require_auth)):
    session = get_session()
    try:
        accounts = session.query(Account).order_by(Account.username).all()
        recent_tweets = []
        for account in accounts:
            for tweet in account.tweets[:10]:
                recent_tweets.append((account, tweet))
        recent_tweets.sort(key=lambda pair: pair[1].tweet_created_at or pair[1].fetched_at, reverse=True)
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "accounts": accounts,
                "recent_tweets": recent_tweets[:50],
                "poll_interval": config.POLL_INTERVAL_MINUTES,
                "twitter_logged_in": scraper.is_logged_in,
                "twitter_login_error": scraper.last_login_error,
            },
        )
    finally:
        session.close()


@app.post("/accounts")
async def create_account(username: str = Form(...), _: None = Depends(require_auth)):
    try:
        await add_account(username)
    except Exception as exc:
        logger.exception("Error añadiendo la cuenta %s", username)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(url="/", status_code=303)


@app.post("/accounts/{account_id}/delete")
def delete_account(account_id: int, _: None = Depends(require_auth)):
    remove_account(account_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/check-now")
async def check_now(_: None = Depends(require_auth)):
    await poll_all_accounts()
    return RedirectResponse(url="/", status_code=303)


@app.post("/tweets/{tweet_id}/topic")
def update_tweet_topic(tweet_id: int, topic: str = Form(...), _: None = Depends(require_auth)):
    session = get_session()
    try:
        tweet = session.query(Tweet).filter_by(id=tweet_id).first()
        if tweet:
            tweet.topic = topic
            session.commit()
    finally:
        session.close()
    return RedirectResponse(url="/", status_code=303)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "twitter_login": "ok" if scraper.is_logged_in else "error"}
