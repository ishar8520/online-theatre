from __future__ import annotations

import uuid

from beanie import PydanticObjectId
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

    result = []
    for item in bookmark_list:
        bookmark = item.dict()
        bookmark['id'] = str(bookmark['id'])
        result.append(bookmark)

    return jsonify(result)


@bookmark_blueprint.route('/add', methods=["PUT"])
@validate_request(BookmarkAdd)
async def add(data: BookmarkAdd) -> Response:
    service = BookmarkService()
    try:
        new_id = await service.add(**data.model_dump())
    except DuplicateKeyException:
        abort(400)

    return jsonify({"id": str(new_id)})


@bookmark_blueprint.route('/delete/<id>', methods=["DELETE"])
async def delete(id: str) -> Response:
    service = BookmarkService()
    try:
        object_id = PydanticObjectId(id)
        await service.delete(object_id)
    except NotFoundException:
        abort(404)

    return jsonify({"result": True})
