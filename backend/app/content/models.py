from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ContentStatus(str, Enum):
    draft = 'draft'
    edited = 'edited'
    graphic_requested = 'graphic_requested'
    graphic_ready = 'graphic_ready'
    scheduled = 'scheduled'
    approved = 'approved'
    posted = 'posted'
    failed = 'failed'
    rejected = 'rejected'


class ContentPlatform(str, Enum):
    x = 'x'
    tiktok = 'tiktok'
    facebook = 'facebook'
    instagram = 'instagram'
    linkedin = 'linkedin'
    blog = 'blog'
    generic = 'generic'


class ContentType(str, Enum):
    text_post = 'text_post'
    image_post = 'image_post'
    short_video_script = 'short_video_script'
    thread = 'thread'
    blog_outline = 'blog_outline'
    announcement = 'announcement'
    market_note = 'market_note'
    educational = 'educational'


class ContentItem(BaseModel):
    id: str
    title: str
    content_type: ContentType
    status: ContentStatus = ContentStatus.draft
    brand: str
    language: str
    tone: str
    topic: str
    draft_text: str | None = None
    edited_text: str | None = None
    graphic_prompt: str | None = None
    graphic_asset_url: str | None = None
    platforms: list[ContentPlatform] = Field(default_factory=lambda: [ContentPlatform.generic])
    scheduled_at: datetime | None = None
    approved_at: datetime | None = None
    posted_at: datetime | None = None
    policy_passed: bool = False
    policy_notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateContentRequest(BaseModel):
    topic: str
    content_type: ContentType = ContentType.text_post
    brand: str | None = None
    language: str | None = None
    tone: str | None = None
    platforms: list[ContentPlatform] = Field(default_factory=lambda: [ContentPlatform.generic])
    context: dict[str, Any] = Field(default_factory=dict)

    @field_validator('topic')
    @classmethod
    def topic_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError('topic must not be empty')
        return value.strip()

    @field_validator('platforms')
    @classmethod
    def platforms_not_empty(cls, value: list[ContentPlatform]) -> list[ContentPlatform]:
        if not value:
            raise ValueError('platforms must not be empty')
        return value


class EditContentRequest(BaseModel):
    content_id: str
    instructions: str | None = None
    tone: str | None = None
    language: str | None = None


class GraphicRequest(BaseModel):
    content_id: str
    style: str = 'clean professional dashboard visual'
    aspect_ratio: str = '16:9'
    instructions: str | None = None


class ScheduleContentRequest(BaseModel):
    content_id: str
    scheduled_at: datetime
    platforms: list[ContentPlatform] | None = None


class ApproveContentRequest(BaseModel):
    content_id: str
    approved_by: str = 'operator'
    notes: str | None = None


class PublishContentRequest(BaseModel):
    content_id: str
    platforms: list[ContentPlatform] | None = None
    confirmation: bool = False


class SocialPostResult(BaseModel):
    platform: ContentPlatform
    ok: bool
    dry_run: bool
    external_id: str | None = None
    message: str
    output: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineRunResult(BaseModel):
    id: str
    content_id: str
    ok: bool
    status: ContentStatus
    steps: list[dict[str, Any]] = Field(default_factory=list)
    message: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
