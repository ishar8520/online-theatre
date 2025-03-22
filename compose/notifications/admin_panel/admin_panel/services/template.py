from functools import lru_cache

from admin_panel.db.postgres import get_postgres_session
from admin_panel.models.admin_notification import Template
from admin_panel.models.enums import TemplateTypeEnum
from admin_panel.schemas import template as template_schemas
from admin_panel.services import exceptions as exc
from admin_panel.services.exceptions import (
    DatabaseError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
    TemplateTypeNotFoundError,
)
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class TemplateService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_template(
            self, template_data: template_schemas.CreateTemplateSchema
    ) -> Template:
        try:
            template_type = TemplateTypeEnum(template_data.type)
        except ValueError:
            raise TemplateTypeNotFoundError("Template type not found")

        async with self.postgres_session as session:
            result = await session.scalars(
                select(Template).filter_by(code=template_data.code)
            )
            existing_template = result.first()
            if existing_template is not None:
                raise TemplateAlreadyExistsError("Template with this code already exists")

            template = Template(
                code=template_data.code,
                subject=template_data.subject,
                body=template_data.body,
                type=template_type,
            )
            session.add(template)
            try:
                await session.commit()
            except IntegrityError:
                raise DatabaseError("Database integrity error occurred")
            await session.refresh(template)
            return template

    async def get_template_by_id(self, template_id: str) -> Template:
        async with self.postgres_session as session:
            result = await session.scalars(select(Template).filter_by(id=template_id))
            template = result.first()
            if template is None:
                raise exc.TemplateNotFoundError("Template not found")
            return template

    async def get_template_by_code(self, code: str) -> Template:
        async with self.postgres_session as session:
            result = await session.scalars(select(Template).filter_by(code=code))
            template = result.first()
            if template is None:
                raise exc.TemplateNotFoundError("Template not found")
            return template

    async def get_templates_list(self) -> list[Template]:
        async with self.postgres_session as session:
            templates = await session.scalars(select(Template))
            return templates.all()

    async def update_template(
            self, template_id: str, template_data: template_schemas.UpdateTemplateSchema
    ) -> Template:
        async with self.postgres_session as session:
            result = await session.scalars(select(Template).filter_by(id=template_id))
            template = result.first()
            if template is None:
                raise TemplateNotFoundError("Template not found")

            if template_data.type is not None:
                try:
                    template.type = TemplateTypeEnum(template_data.type)
                except ValueError:
                    raise TemplateTypeNotFoundError("Template type not found")

            for field in template_data.model_fields_set - {"type"}:
                setattr(template, field, getattr(template_data, field))

            try:
                await session.commit()
                await session.refresh(template)
            except IntegrityError:
                raise DatabaseError("Database integrity error occurred")
            return template

    async def delete_template(self, template_id: str):
        async with self.postgres_session as session:
            result = await session.scalars(select(Template).filter_by(id=template_id))
            template = result.first()
            if template is None:
                raise exc.TemplateNotFoundError("Template not found")
            await session.delete(template)
            await session.commit()


@lru_cache()
def get_template_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> TemplateService:
    return TemplateService(postgres_session)
