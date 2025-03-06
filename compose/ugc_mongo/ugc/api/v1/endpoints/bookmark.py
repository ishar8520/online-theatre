from __future__ import annotations

import uuid

from quart import Blueprint, jsonify, Response
from quart_schema import validate_request

from ....services.bookmark import BookmarkService
from ..models.bookmark import BookmarkAdd, BookmarkDelete
from ....services.exceptions import NotFoundException

bookmark_blueprint = Blueprint('bookmark', __name__)


@bookmark_blueprint.route('/get_list', methods=["GET"])
async def get_list() -> Response:
    service = BookmarkService()
    bookmark_list = await service.get_list()
    result = [item.dict() for item in bookmark_list]

    return jsonify(result)


@bookmark_blueprint.route('/add', methods=["POST"])
@validate_request(BookmarkAdd)
async def add(data: BookmarkAdd) -> Response:
    service = BookmarkService()
    new_uuid = await service.add(**data.model_dump())

    return jsonify({"uuid": str(new_uuid)})


@bookmark_blueprint.route('/delete', methods=["POST"])
@validate_request(BookmarkDelete)
async def delete(data: BookmarkDelete) -> Response:
    service = BookmarkService()

    try:
        await service.delete(**data.model_dump())
    except NotFoundException:
        return jsonify({"result": False})

    return jsonify({"result": True})
