from pydantic import BaseModel, ConfigDict


class AutoReplyTemplateBase(BaseModel):
    name: str
    source_language: str
    subject_template: str
    body_template: str
    signature_template: str | None = None
    is_active: bool = True


class AutoReplyTemplateCreate(AutoReplyTemplateBase):
    pass


class AutoReplyTemplateUpdate(BaseModel):
    name: str | None = None
    source_language: str | None = None
    subject_template: str | None = None
    body_template: str | None = None
    signature_template: str | None = None
    is_active: bool | None = None


class AutoReplyTemplateRead(AutoReplyTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
