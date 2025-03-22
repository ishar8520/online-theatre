from admin_panel.schemas import template as template_schemas
from admin_panel.services import template as template_services
from admin_panel.services.exceptions import (
    DatabaseError,
    SystemTemplateOperationNotAllowedError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params, paginate
from pydantic import ValidationError

router = APIRouter()


@router.post(
    "/",
    response_model=dict,
    summary="Создать шаблон",
)
async def create_template(
    template_data: template_schemas.CreateTemplateSchema,
    template_service: template_services.TemplateService = Depends(
        template_services.get_template_service
    ),
):
    try:
        await template_service.create_template(template_data=template_data)
        return {"detail": "success"}
    except DatabaseError as db_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(db_error),
        )
    except ValidationError as validation_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(validation_error),
        )
    except TemplateAlreadyExistsError as exists_error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exists_error),
        )


@router.get(
    "/",
    response_model=Page[template_schemas.GetTemplateSchema],
    summary="Получить список шаблонов",
)
async def get_templates(
    params: Params = Depends(),
    template_service: template_services.TemplateService = Depends(template_services.get_template_service),
) -> Page[template_schemas.GetTemplateSchema]:
    templates_list = await template_service.get_templates_list()
    return paginate(templates_list, params)


@router.patch(
    "/{template_id}",
    response_model=template_schemas.GetTemplateSchema,
    summary="Обновить шаблон",
)
async def update_template(
    template_id: str,
    template_data: template_schemas.UpdateTemplateSchema,
    template_service: template_services.TemplateService = Depends(
        template_services.get_template_service
    ),
):
    try:
        return await template_service.update_template(
            template_id=template_id, template_data=template_data
        )
    except TemplateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        )
    except SystemTemplateOperationNotAllowedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        )


@router.delete(
    "/{template_id}",
    response_model=dict,
    summary="Удалить шаблон",
)
async def delete_template(
    template_id: str,
    template_service: template_services.TemplateService = Depends(
        template_services.get_template_service
    ),
):
    try:
        await template_service.delete_template(template_id=template_id)
        return {"detail": "success"}
    except TemplateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        )
    except SystemTemplateOperationNotAllowedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        )


@router.get(
    "/{template_id}",
    response_model=template_schemas.GetTemplateSchema,
    summary="Получить шаблон по ID",
)
async def get_template_by_id(
    template_id: str,
    template_service: template_services.TemplateService = Depends(
        template_services.get_template_service
    ),
):
    try:
        template = await template_service.get_template_by_id(template_id)
        return template
    except TemplateNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/by-code/{code}",
    response_model=template_schemas.GetTemplateSchema,
    summary="Получить шаблон по коду",
)
async def get_template_by_code(
    code: str,
    template_service: template_services.TemplateService = Depends(
        template_services.get_template_service
    ),
):
    try:
        template = await template_service.get_template_by_code(code)
        return template
    except TemplateNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
