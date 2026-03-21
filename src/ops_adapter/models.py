from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)


class ActionResponse(BaseModel):
    status: str
    result: dict[str, Any] | None = None
    approval_id: str | None = None
    reason: str | None = None


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
    commit: str | None = None


class EmployeeOnboardParams(BaseModel):
    userPrincipalName: str
    displayName: str | None = None


class EmailSendIndividualParams(BaseModel):
    to: str
    subject: str | None = None
    body: str | None = None


class LicensesAssignParams(BaseModel):
    userPrincipalName: str
    licenses: list[str]  # license aliases, skuPartNumbers, or skuIds
    disabledPlans: dict[str, list[str]] | None = (
        None  # map license key -> list of servicePlanIds to disable
    )
