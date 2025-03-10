from __future__ import annotations

import uuid

from beanie import PydanticObjectId
from quart import Blueprint, jsonify, Response, abort
from quart_schema import validate_request

from ..models.review import ReviewAdd, ReviewUpdate
from ....services.review import ReviewService
from ....services.exceptions import (
    NotFoundException,
    DuplicateKeyException
)

review_blueprint = Blueprint('review', __name__)


@review_blueprint.route("/get_list/<uuid:user_id>", methods=["GET"])
async def get_list(user_id: uuid.UUID) -> Response:
    service = ReviewService()
    review_list = await service.get_list(user_id)

    result = []
    for item in review_list:
        review = item.dict()
        review["id"] = str(review["id"])
        result.append(review)

    return jsonify({"result": result})


@review_blueprint.route("/add", methods=["PUT"])
@validate_request(ReviewAdd)
async def add(data: ReviewAdd) -> Response:
    service = ReviewService()
    try:
        new_review = await service.add(**data.model_dump())
    except DuplicateKeyException:
        abort(400)

    item = new_review.model_dump()
    item["id"] = str(item["id"])

    return jsonify({"result": item})


@review_blueprint.route("/publish/<id>", methods=["POST"])
async def publish(id: PydanticObjectId) -> Response:
    service = ReviewService()
    try:
        review = await service.publish(id)
    except NotFoundException:
        abort(404)

    item = review.model_dump()
    item["id"] = str(item["id"])

    return jsonify({"result": item})


@review_blueprint.route("/update/<id>", methods=["POST"])
@validate_request(ReviewUpdate)
async def update(id: PydanticObjectId, data: ReviewUpdate):
    service = ReviewService()
    try:
        updated_id = await service.update(id, **data.model_dump())
    except NotFoundException:
        abort(404)

    return jsonify({"id": str(updated_id)})


@review_blueprint.route("/delete/<id>", methods=["DELETE"])
async def delete(id: PydanticObjectId) -> Response:
    service = ReviewService()
    try:
        await service.delete(id)
    except NotFoundException:
        abort(404)

    return jsonify({"result": True})
