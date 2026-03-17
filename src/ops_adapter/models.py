from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)


class ActionResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    approval_id: Optional[str] = None
    reason: Optional[str] = None


class UsersReadParams(BaseModel):
    userPrincipalName: str


class UsersCreateParams(BaseModel):
    userPrincipalName: str
    displayName: str
    mailNickname: str | None = None
    password: str | None = None
    accountEnabled: bool = True
    jobTitle: str | None = None
    department: str | None = None


class UsersUpdateParams(BaseModel):
    userPrincipalName: str
    displayName: str | None = None
    jobTitle: str | None = None
    department: str | None = None
    accountEnabled: bool | None = None


class UsersDisableParams(BaseModel):
    userPrincipalName: str


class DeploymentParams(BaseModel):
    env: str = Field(pattern=r"^(preview|production)$")
    commit: Optional[str] = None


class EmployeeOnboardParams(BaseModel):
    userPrincipalName: str
    displayName: Optional[str] = None


class EmailSendIndividualParams(BaseModel):
    to: str
    subject: Optional[str] = None
    body: Optional[str] = None


class LicensesAssignParams(BaseModel):
    userPrincipalName: str
    licenses: list[str]  # license aliases, skuPartNumbers, or skuIds
    disabledPlans: Optional[dict[str, list[str]]] = None  # map license key -> list of servicePlanIds to disable
