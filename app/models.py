import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Integer, Text, DateTime, Date, ForeignKey, JSON, Enum, Boolean, UniqueConstraint, event, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


AGENCIES: list[dict[str, str]] = [
    {"code": "MCI", "name": "Ministry of Communications and Information"},
    {"code": "MFA", "name": "Ministry of Foreign Affairs"},
    {"code": "MHA", "name": "Ministry of Home Affairs"},
    {"code": "MND", "name": "Ministry of National Development"},
    {"code": "MOD", "name": "Ministry of Defence (MINDEF)"},
    {"code": "MOE", "name": "Ministry of Education"},
    {"code": "MOF", "name": "Ministry of Finance"},
    {"code": "MOH", "name": "Ministry of Health"},
    {"code": "MOM", "name": "Ministry of Manpower"},
    {"code": "MOT", "name": "Ministry of Transport"},
    {"code": "MSE", "name": "Ministry of Sustainability and the Environment"},
    {"code": "MSF", "name": "Ministry of Social and Family Development"},
    {"code": "MTI", "name": "Ministry of Trade and Industry"},
    {"code": "MTO", "name": "HOMES MTO (System Admin)"},
    {"code": "PMO", "name": "Prime Minister's Office"},
    {"code": "BCA", "name": "Building and Construction Authority"},
    {"code": "CPFB", "name": "Central Provident Fund Board"},
    {"code": "ECDA", "name": "Early Childhood Development Agency"},
    {"code": "EDB", "name": "Economic Development Board"},
    {"code": "HDB", "name": "Housing and Development Board"},
    {"code": "HPB", "name": "Health Promotion Board"},
    {"code": "IRAS", "name": "Inland Revenue Authority of Singapore"},
    {"code": "IMDA", "name": "Infocomm Media Development Authority"},
    {"code": "LTA", "name": "Land Transport Authority"},
    {"code": "MAS", "name": "Monetary Authority of Singapore"},
    {"code": "MOH ILTC", "name": "MOH Office for Healthcare Transformation"},
    {"code": "NEA", "name": "National Environment Agency"},
    {"code": "NLB", "name": "National Library Board"},
    {"code": "NParks", "name": "National Parks Board"},
    {"code": "PA", "name": "People's Association"},
    {"code": "PUB", "name": "Public Utilities Board"},
    {"code": "SLA", "name": "Singapore Land Authority"},
    {"code": "SportSG", "name": "Sport Singapore"},
    {"code": "STB", "name": "Singapore Tourism Board"},
    {"code": "TOTE", "name": "Tote Board"},
    {"code": "URA", "name": "Urban Redevelopment Authority"},
]


class UserRole(str, enum.Enum):
    agency_creator = "agency_creator"
    agency_approver = "agency_approver"
    mto_admin = "mto_admin"


class SubmissionStatus(str, enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    pending_final = "pending_final"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # plain text for demo
    roles: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["agency_creator","agency_approver"]
    agency: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Convenience helpers
    def has_role(self, *role_names):
        return any(r in (self.roles or []) for r in role_names)

    def is_admin(self):
        return self.has_role("mto_admin")


class SchemeOverview(Base):
    __tablename__ = "scheme_overview"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agency: Mapped[str | None] = mapped_column(String(255))
    scheme_name: Mapped[str] = mapped_column(String(255))
    scheme_code: Mapped[str | None] = mapped_column(String(100))
    legislated_or_consent: Mapped[str | None] = mapped_column(String(50))
    consent_scope: Mapped[str | None] = mapped_column(Text)
    background_info: Mapped[dict | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SchemeSubmission(Base):
    __tablename__ = "scheme_submissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_overview_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("scheme_overview.id"))
    status: Mapped[str] = mapped_column(String(50), default=SubmissionStatus.draft.value)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    overview: Mapped["SchemeOverview | None"] = relationship(foreign_keys=[scheme_overview_id])
    creator: Mapped["User | None"] = relationship(foreign_keys=[created_by])
    mt_parameters: Mapped["SchemeMTParameters | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    transactions: Mapped["TransactionDetails | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    homes_functions: Mapped["HOMESFunctions | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    mt_bands: Mapped["MTBands | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    api_interfaces: Mapped["APIBatchInterfaces | None"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")
    change_logs: Mapped[list["ChangeLog"]] = relationship(back_populates="submission", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="submission", cascade="all, delete-orphan")
    onboarding_slots: Mapped[list["OnboardingSlot"]] = relationship(back_populates="submission", cascade="all, delete-orphan")


class SchemeMTParameters(Base):
    __tablename__ = "scheme_mt_parameters"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    data: Mapped[dict | None] = mapped_column(JSON)
    submission: Mapped["SchemeSubmission"] = relationship(back_populates="mt_parameters")


class TransactionDetails(Base):
    __tablename__ = "transaction_details"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    data: Mapped[dict | None] = mapped_column(JSON)
    submission: Mapped["SchemeSubmission"] = relationship(back_populates="transactions")


class HOMESFunctions(Base):
    __tablename__ = "homes_functions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    data: Mapped[dict | None] = mapped_column(JSON)
    submission: Mapped["SchemeSubmission"] = relationship(back_populates="homes_functions")


class MTBands(Base):
    __tablename__ = "mt_bands"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    data: Mapped[dict | None] = mapped_column(JSON)
    submission: Mapped["SchemeSubmission"] = relationship(back_populates="mt_bands")


class APIBatchInterfaces(Base):
    __tablename__ = "api_batch_interfaces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    data: Mapped[dict | None] = mapped_column(JSON)
    submission: Mapped["SchemeSubmission"] = relationship(back_populates="api_interfaces")


class ChangeLog(Base):
    __tablename__ = "change_log"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    changed_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    tab_name: Mapped[str | None] = mapped_column(String(100))
    changes: Mapped[list | None] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["SchemeSubmission"] = relationship(back_populates="change_logs")
    user: Mapped["User | None"] = relationship(foreign_keys=[changed_by])


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    stage: Mapped[str | None] = mapped_column(String(50))  # submitted/approved/rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["SchemeSubmission"] = relationship(back_populates="comments")
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])


class OnboardingSlot(Base):
    """Onboarding slot selection linked to a scheme submission.
    
    Each submission can select one primary slot + optional additional slots with justification.
    The slot captures year, quarter month (Jan/Apr/Jul/Nov), go-live dates, and approval status.
    """
    __tablename__ = "onboarding_slots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme_submissions.id"), unique=False)
    year: Mapped[int] = mapped_column(Integer)
    slot_month: Mapped[int] = mapped_column(Integer)  # 1=Jan, 4=Apr, 7=Jul, 11=Nov
    slot_month_name: Mapped[str] = mapped_column(String(20))  # "January", "April", "July", "November"
    is_additional: Mapped[bool] = mapped_column(Boolean, default=False)  # True if 2+ slots for same submission
    justification: Mapped[str | None] = mapped_column(Text)  # Required for additional slots
    technical_go_live: Mapped[date] = mapped_column(Date)
    business_go_live: Mapped[date] = mapped_column(Date)
    booked_by_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    booked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approval_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    approver_comment: Mapped[str | None] = mapped_column(Text)  # For rejection reasons, e.g. "Please pick Jul instead"
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submission: Mapped["SchemeSubmission"] = relationship(back_populates="onboarding_slots")
    booked_by: Mapped["User | None"] = relationship(foreign_keys=[booked_by_id])


@event.listens_for(User, "before_update")
def protect_mto_admin_on_update(mapper, connection, target: User):
    if target.username != "mto_admin":
        return

    state = inspect(target)
    if state.attrs.is_active.history.has_changes() and target.is_active is False:
        raise ValueError("mto_admin cannot be deactivated")


@event.listens_for(User, "before_delete")
def protect_mto_admin_on_delete(mapper, connection, target: User):
    if target.username == "mto_admin":
        raise ValueError("mto_admin cannot be deleted")
