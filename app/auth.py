import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config import get_db
from app.models import User, AGENCIES, sg_now

SECRET_KEY = "homes-demo-secret-key-2026-extended!"
ALGORITHM = "HS256"

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str | None = None
    password: str
    display_name: str
    agency: str
    roles: list[str] = []

class UserUpdate(BaseModel):
    display_name: str | None = None
    email: str | None = None
    agency: str | None = None
    roles: list[str] | None = None
    is_active: bool | None = None
    password: str | None = None


def _user_dict(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "roles": u.roles or [],
        "agency": u.agency,
        "display_name": u.display_name,
        "is_active": u.is_active,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        "last_logout_at": u.last_logout_at.isoformat() if u.last_logout_at else None,
    }


VALID_ROLE_SET = {"agency_creator", "agency_approver", "mto_admin"}
VALID_AGENCY_CODES = {a["code"] for a in AGENCIES}


def _validate_roles(roles: list[str]):
    if not roles:
        raise HTTPException(status_code=400, detail="At least one role is required")
    unknown = [r for r in (roles or []) if r not in VALID_ROLE_SET]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Invalid role(s): {unknown}")


def _validate_agency(agency: str | None, required: bool = False):
    if required and not agency:
        raise HTTPException(status_code=400, detail="Agency is required")
    if agency and agency not in VALID_AGENCY_CODES:
        raise HTTPException(status_code=400, detail="Invalid agency code")


def _normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    val = str(email).strip().lower()
    if not val:
        return None
    if "@" not in val or val.startswith("@") or val.endswith("@"):
        raise HTTPException(status_code=400, detail="Email must be a valid address")
    return val


def _validate_required_email_for_approval_roles(roles: list[str], email: str | None):
    if any(r in ("agency_approver", "mto_admin") for r in (roles or [])) and not email:
        raise HTTPException(status_code=400, detail="Email is required for approver/admin roles")


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "username": user.username,
        "roles": user.roles or [],
        "agency": user.agency,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["sub"]
    except (jwt.ExpiredSignatureError, jwt.DecodeError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or user.password_hash != req.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")
    user.last_login_at = sg_now()
    await db.commit()
    token = create_token(user)
    return {"token": token, "user": _user_dict(user)}


@router.post("/logout")
async def logout(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user.last_logout_at = sg_now()
    await db.commit()
    return {"ok": True, "last_logout_at": user.last_logout_at.isoformat() if user.last_logout_at else None}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return _user_dict(user)


@router.get("/agencies")
async def list_agencies():
    return AGENCIES


# ── User Management (mto_admin only) ──

def _require_admin(user: User):
    if not user.has_role("mto_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MTO admin access required")


@router.get("/users")
async def list_users(
    agency: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_admin(user)
    if agency:
        _validate_agency(agency)
    q = select(User)
    if agency:
        q = q.where(User.agency == agency)
    q = q.order_by(User.agency, User.username)
    result = await db.execute(q)
    return [_user_dict(u) for u in result.scalars().all()]


@router.post("/users", status_code=201)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_admin(user)
    if body.username == "mto_admin":
        raise HTTPException(400, "mto_admin is a reserved system account")
    _validate_roles(body.roles)
    _validate_agency(body.agency, required=True)
    normalized_email = _normalize_email(body.email)
    _validate_required_email_for_approval_roles(body.roles, normalized_email)
    exists = await db.execute(select(User).where(User.username == body.username))
    if exists.scalar_one_or_none():
        raise HTTPException(400, "Username already exists")
    if normalized_email:
        email_exists = await db.execute(select(User).where(User.email == normalized_email))
        if email_exists.scalar_one_or_none():
            raise HTTPException(400, "Email already exists")
    new_user = User(
        username=body.username, password_hash=body.password, display_name=body.display_name,
        agency=body.agency, roles=body.roles, is_active=True, email=normalized_email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return _user_dict(new_user)


@router.put("/users/{user_id}")
async def update_user(user_id: str, body: UserUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    _require_admin(user)
    target = await db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    if target.username == "mto_admin":
        if body.is_active is False:
            raise HTTPException(400, "mto_admin cannot be deactivated")
        if body.roles is not None and "mto_admin" not in body.roles:
            raise HTTPException(400, "mto_admin role cannot be removed")
    if body.display_name is not None:
        target.display_name = body.display_name
    if body.email is not None:
        normalized_email = _normalize_email(body.email)
        if normalized_email:
            email_exists = await db.execute(select(User).where(User.email == normalized_email, User.id != target.id))
            if email_exists.scalar_one_or_none():
                raise HTTPException(400, "Email already exists")
        target.email = normalized_email
    if body.agency is not None:
        _validate_agency(body.agency)
        target.agency = body.agency
    if body.roles is not None:
        _validate_roles(body.roles)
        target.roles = body.roles
    if body.is_active is not None:
        target.is_active = body.is_active
    if body.password is not None:
        target.password_hash = body.password
    _validate_required_email_for_approval_roles(target.roles or [], target.email)
    await db.commit()
    return _user_dict(target)


# ── Seed Demo Users ──

DEMO_USERS = [
    {"username": "moh_creator", "email": "moh_creator@homes.local", "password_hash": "password", "roles": ["agency_creator"], "agency": "MOH", "display_name": "MOH Creator"},
    {"username": "moh_approver", "email": "moh_approver@homes.local", "password_hash": "password", "roles": ["agency_approver"], "agency": "MOH", "display_name": "MOH Approver"},
    {"username": "mse_creator", "email": "mse_creator@homes.local", "password_hash": "password", "roles": ["agency_creator"], "agency": "MSE", "display_name": "MSE Creator"},
    {"username": "mse_approver", "email": "mse_approver@homes.local", "password_hash": "password", "roles": ["agency_approver"], "agency": "MSE", "display_name": "MSE Approver"},
    {"username": "moe_user", "email": "moe_user@homes.local", "password_hash": "password", "roles": ["agency_creator", "agency_approver"], "agency": "MOE", "display_name": "MOE User"},
    {"username": "mto_admin", "email": "mto_admin@homes.local", "password_hash": "password", "roles": ["mto_admin"], "agency": "MTO", "display_name": "MTO Admin"},
]


async def seed_demo_users(db: AsyncSession):
    for u in DEMO_USERS:
        result = await db.execute(select(User).where(User.username == u["username"]))
        existing = result.scalar_one_or_none()
        if not existing:
            db.add(User(**u))
        else:
            existing.password_hash = u["password_hash"]
            existing.email = u.get("email")
            existing.roles = u["roles"]
            existing.agency = u["agency"]
            existing.display_name = u["display_name"]
            existing.is_active = True
    await db.commit()
