from __future__ import annotations
from datetime import datetime
from enum import Enum
from jsonclasses import jsonclass, jsonenum, types
from jsonclasses_pymongo import pymongo
from jsonclasses_server import api, authorized, server



@jsonenum
class Sex(int, Enum):
    MALE = 1
    FEMALE = 2


@jsonenum
class HouseLevel(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3


@jsonenum
class Status(int, Enum):
    PENGDING = 1
    Processing = 2
    FINISHED = 3


@authorized
@api(enable='U')
@pymongo
@jsonclass(can_update=types.getop.isthis)
class Admin:
    id: str = types.readonly.str.primary.mongoid.required
    username: str = types.str.authidentity.writenonnull.required
    password: str = types.str.writeonly.writenonnull.salt.authbycheckpw.unqueryable.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@authorized
@api
@pymongo
@jsonclass(
    can_update=types.oneisvalid([
        types.getop.isthis,
        types.getop.isobjof('Admin')
    ]),
    can_delete=types.oneisvalid([
        types.getop.isthis,
        types.getop.isobjof('Admin')
    ]),
)
class User:
    id: str = types.readonly.str.primary.mongoid.required
    username: str = types.str.authidentity.writenonnull
    phone_number: str = types.str.unique.authidentity.writenonnull.required
    password: str = types.str.writeonly.writenonnull.salt.authbycheckpw.unqueryable.required
    sex: Sex | None = types.enum(Sex).writeonce
    house_levels: HouseLevel | None = types.enum(HouseLevel).canu(types.getop.isobjof('Admin'))
    review_material: ReviewMaterial | None = types.objof('ReviewMaterial').linkedby('author')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@api
@pymongo
@jsonclass(
    can_create=types.getop.isobjof('User'),
    can_update=types.oneisvalid([
        types.getop.isthis,
        types.getop.isobjof('Admin')
    ])
    )
class ReviewMaterial:
    id: str = types.readonly.str.primary.mongoid.required
    author: User = types.objof('User').linkto
    name: str = types.str.required
    phone_number: str = types.str.alnum.required
    id_number: str = types.str.length(18).required
    degree: str = types.uploader('image').str.url.required
    certification: str = types.uploader('image').str.url.required
    account_information: str = types.uploader('image').str.url.required
    status: Status = types.enum(Status).default(Status.PENGDING).canu(types.getop.isobjof('Admin'))
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@api
@pymongo
@jsonclass(can_create=types.getop.isobjof('Admin'))
class House:
    id: str = types.readonly.str.primary.mongoid.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required

Admin(username="admin", password='123456').save()

app = server()
