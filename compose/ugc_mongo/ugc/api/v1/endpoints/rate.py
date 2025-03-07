from __future__ import annotations

import uuid

from quart import Blueprint, jsonify, Response, abort
from quart_schema import validate_request

from ..models.rate import RateAdd
from ....services.rate import RateService
from ....services.exceptions import NotFoundException

rate_blueprint = Blueprint('rate', __name__)


@rate_blueprint.route('/get_list/<uuid:user_id>', methods=["GET"])
async def get_list(user_id: uuid.UUID) -> Response:
    service = RateService()
    rate_list = await service.get_list(user_id)
    result = [item.dict() for item in rate_list]

    return jsonify(result)


@rate_blueprint.route('/add', methods=["PUT"])
@validate_request(RateAdd)
async def add(data: RateAdd) -> Response:
    service = RateService()
    new_uuid = await service.add(**data.model_dump())

    return jsonify({"uuid": str(new_uuid)})


@rate_blueprint.route('/delete/<uuid:uuid>', methods=["DELETE"])
async def delete(uuid: uuid.UUID) -> Response:
    service = RateService()
    try:
        await service.delete(uuid)
    except NotFoundException:
        abort(404)

    return jsonify({"result": True})
