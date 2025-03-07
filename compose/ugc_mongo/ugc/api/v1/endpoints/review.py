from __future__ import annotations

import uuid

from quart import Blueprint, jsonify, Response, abort
from quart_schema import validate_request

from ..models.review import ReviewAdd, ReviewUpdate
from ....services.review import ReviewService
from ....services.exceptions import NotFoundException

review_blueprint = Blueprint('review', __name__)


@review_blueprint.route('/get_list/<uuid:user_id>', methods=["GET"])
async def get_list(user_id: uuid.UUID) -> Response:
    service = ReviewService()
    review_list = await service.get_list(user_id)
    result = [item.dict() for item in review_list]

    return jsonify(result)


@review_blueprint.route('/add', methods=["PUT"])
@validate_request(ReviewAdd)
async def add(data: ReviewAdd) -> Response:
    service = ReviewService()
    new_uuid = await service.add(**data.model_dump())

    return jsonify({"uuid": str(new_uuid)})


@review_blueprint.route('/publish/<uuid:uuid>', methods=["POST"])
async def publish(uuid: uuid.UUID) -> Response:
    service = ReviewService()
    try:
        updated_uuid = await service.publish(uuid)
    except NotFoundException:
        abort(404)

    return jsonify({"uuid": str(updated_uuid)})


@review_blueprint.route('/update/<uuid:uuid>', methods=["POST"])
@validate_request(ReviewUpdate)
async def update(uuid: uuid.UUID, data: ReviewUpdate):
    service = ReviewService()
    try:
        updated_uuid = await service.update(uuid, **data.model_dump())
    except NotFoundException:
        abort(404)

    return jsonify({"uuid": str(updated_uuid)})


@review_blueprint.route('/delete/<uuid:uuid>', methods=["DELETE"])
async def delete(uuid: uuid.UUID) -> Response:
    service = ReviewService()
    try:
        await service.delete(uuid)
    except NotFoundException:
        abort(404)

    return jsonify({"result": True})
