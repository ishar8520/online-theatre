from __future__ import annotations

import uuid

from quart import Blueprint, jsonify, Response, abort
from quart_schema import validate_request

from ....services.bookmark import BookmarkService
from ..models.bookmark import BookmarkAdd
from ....services.exceptions import NotFoundException, DuplicateKeyException

bookmark_blueprint = Blueprint('bookmark', __name__)


@bookmark_blueprint.route('/get_list/<uuid:user_id>', methods=["GET"])
async def get_list(user_id: uuid.UUID) -> Response:
    service = BookmarkService()
    bookmark_list = await service.get_list(user_id)
    result = [item.dict() for item in bookmark_list]

    return jsonify(result)


@bookmark_blueprint.route('/add', methods=["PUT"])
@validate_request(BookmarkAdd)
async def add(data: BookmarkAdd) -> Response:
    service = BookmarkService()
    try:
        new_uuid = await service.add(**data.model_dump())
    except DuplicateKeyException:
        abort(400)

    return jsonify({"uuid": str(new_uuid)})


@bookmark_blueprint.route('/delete/<uuid:uuid>', methods=["DELETE"])
async def delete(uuid: uuid.UUID) -> Response:
    service = BookmarkService()
    try:
        await service.delete(uuid)
    except NotFoundException:
        abort(404)

    return jsonify({"result": True})
