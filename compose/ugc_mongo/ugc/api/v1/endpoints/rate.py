from __future__ import annotations

import uuid

from beanie import PydanticObjectId
from quart import Blueprint, jsonify, Response, abort
from quart_schema import validate_request

from ..models.rate import RateAdd
from ....services.rate import RateService
from ....services.exceptions import (
    NotFoundException,
    DuplicateKeyException
)

rate_blueprint = Blueprint('rate', __name__)


@rate_blueprint.route('/get_list/<uuid:user_id>', methods=["GET"])
async def get_list(user_id: uuid.UUID) -> Response:
    service = RateService()
    rate_list = await service.get_list(user_id)

    result = []
    for item in rate_list:
        rate = item.dict()
        rate['id'] = str(rate['id'])
        result.append(rate)

    return jsonify(result)


@rate_blueprint.route('/add', methods=["PUT"])
@validate_request(RateAdd)
async def add(data: RateAdd) -> Response:
    service = RateService()
    try:
        new_id = await service.add(**data.model_dump())
    except DuplicateKeyException:
        abort(400)

    return jsonify({"id": str(new_id)})


@rate_blueprint.route('/delete/<id>', methods=["DELETE"])
async def delete(id: PydanticObjectId) -> Response:
    service = RateService()
    try:
        await service.delete(id)
    except NotFoundException:
        abort(404)

    return jsonify({"result": True})
