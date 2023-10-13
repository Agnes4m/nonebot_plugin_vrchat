from datetime import date, datetime
from typing import Dict, List, Literal, Optional, Tuple, TypeVar

from pydantic import BaseModel, Field
from vrchatapi import LimitedUser

from .utils import patch_api_model_append_attr

TM = TypeVar("TM", bound=BaseModel)

DeveloperType = Literal["none", "trusted", "internal", "moderator"]
StatusType = Literal["active", "join me", "ask me", "busy", "offline"]
StateType = Literal["offline", "active", "online"]
GroupPrivacyType = Literal["default", "private"]
GroupJoinStateType = Literal["closed", "invite", "request", "open"]
GroupMemberStatusType = Literal["inactive", "member", "requested", "invited"]
ReleaseStatusType = Literal["public", "private", "hidden", "all"]

NormalizedStatusType = Literal[
    "online",
    "webonline",
    "joinme",
    "busy",
    "askme",
    "offline",
    "unknown",
]
TrustType = Literal[
    "visitor",
    "new",
    "user",
    "known",
    "trusted",
    "friend",
    "developer",
    "moderator",
]
LOCATION_PRIVACY = Literal["private", "public", "group_public"]

NORMALIZE_STATUS_MAP: Dict[StatusType, NormalizedStatusType] = {
    "active": "online",
    "join me": "joinme",
    "busy": "busy",
    "ask me": "askme",
}
NORMALIZE_TRUST_TAG_MAP: Dict[str, TrustType] = {
    "veteran": "trusted",
    "trusted": "known",
    "known": "user",
}
DEVELOPER_TRUST_TYPE_MAP: Dict[str, TrustType] = {
    "internal": "developer",
    "moderator": "moderator",
}
TRUST_TAG_PREFIX = "system_trust_"


def normalize_status(
    status: StatusType,
    location: Optional[str],
) -> NormalizedStatusType:
    if location == "offline":
        if status == "active":
            return "webonline"
        return "offline"
    return NORMALIZE_STATUS_MAP.get(status, "unknown")


def extract_trust_level(tags: List[str], developer_type: Optional[str]) -> TrustType:
    if developer_type in DEVELOPER_TRUST_TYPE_MAP:
        return DEVELOPER_TRUST_TYPE_MAP[developer_type]

    for suffix in NORMALIZE_TRUST_TAG_MAP:
        if f"{TRUST_TAG_PREFIX}{suffix}" in tags:
            return NORMALIZE_TRUST_TAG_MAP[suffix]

    return "visitor"


# region patches
patch_api_model_append_attr(LimitedUser, "last_login", "last_login", "datetime")
# endregion patches


class LimitedUserModel(BaseModel):
    user_id: str = Field(alias="id")
    current_avatar_image_url: str
    current_avatar_thumbnail_image_url: str
    developer_type: DeveloperType
    display_name: str
    is_friend: bool
    last_platform: str
    profile_pic_override: str
    original_status: StatusType = Field(alias="status")
    status_description: str
    tags: List[str]
    user_icon: str

    bio: Optional[str] = None
    fallback_avatar: Optional[str] = None
    location: Optional[str] = None
    friend_key: Optional[str] = None
    last_login: Optional[datetime] = None

    @property
    def status(self) -> NormalizedStatusType:
        return normalize_status(self.original_status, self.location)

    @property
    def trust(self) -> TrustType:
        return extract_trust_level(self.tags, self.developer_type)


class UserModel(BaseModel):
    user_id: str = Field(alias="id")
    bio: str
    bio_links: List[str]
    current_avatar_image_url: str
    current_avatar_thumbnail_image_url: str
    date_joined: date
    developer_type: DeveloperType
    display_name: str
    friend_key: str
    is_friend: bool
    last_activity: str
    last_login: str
    last_platform: str
    profile_pic_override: str
    state: StateType
    original_status: StatusType = Field(alias="status")
    status_description: str
    tags: List[str]
    user_icon: str

    allow_avatar_copying: bool = True
    instance_id: str = "offline"

    friend_request_status: Optional[str] = None
    note: Optional[str] = None
    location: Optional[str] = None
    traveling_to_instance: Optional[str] = None
    traveling_to_location: Optional[str] = None
    traveling_to_world: Optional[str] = None
    world_id: Optional[str] = None

    @property
    def status(self) -> NormalizedStatusType:
        return normalize_status(self.original_status, self.location)

    @property
    def trust(self) -> TrustType:
        return extract_trust_level(self.tags, self.developer_type)


class GroupGalleryModel(BaseModel):
    gallery_id: str = Field(alias="id")
    name: str
    description: str
    role_ids_to_view: List[str]
    role_ids_to_submit: List[str]
    role_ids_to_auto_approve: List[str]
    role_ids_to_manage: List[str]
    created_at: datetime
    updated_at: datetime

    members_only: bool = False


class GroupMyMemberModel(BaseModel):
    my_member_id: str = Field(alias="id")
    group_id: str
    user_id: str
    role_ids: List[str]
    manager_notes: str
    membership_status: str
    visibility: str
    joined_at: datetime
    permissions: List[str]

    is_subscribed_to_announcements: bool = True
    is_representing: bool = False
    has2_fa: bool = False

    banned_at: Optional[str] = None


class GroupRoleModel(BaseModel):
    role_id: str = Field(alias="id")
    group_id: str
    name: str
    description: str
    permissions: List[str]
    order: int
    created_at: datetime
    updated_at: datetime

    is_self_assignable: bool = False
    is_management_role: bool = False
    requires_two_factor: bool = False
    requires_purchase: bool = False


class GroupModel(BaseModel):
    group_id: str = Field(alias="id")
    name: str
    short_code: str
    discriminator: str
    description: str
    owner_id: str
    links: List[str]
    languages: List[str]
    member_count: int
    member_count_synced_at: datetime
    tags: List[str]
    galleries: List[GroupGalleryModel]
    created_at: datetime
    online_member_count: int
    my_member: GroupMyMemberModel
    roles: List[GroupRoleModel]

    privacy: GroupPrivacyType = "default"
    is_verified: bool = False
    join_state: GroupJoinStateType = "open"
    membership_status: GroupMemberStatusType = "inactive"

    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    rules: Optional[str] = None
    icon_id: Optional[str] = None
    banner_id: Optional[str] = None


class LimitedUnityPackage(BaseModel):
    platform: str
    unity_version: str


class LimitedWorldModel(BaseModel):
    world_id: str = Field(alias="id")
    author_id: str
    author_name: str
    capacity: int
    created_at: datetime
    image_url: str
    labs_publication_date: str
    name: str
    organization: str
    publication_date: str
    tags: List[str]
    thumbnail_image_url: str
    unity_packages: List[LimitedUnityPackage]
    updated_at: datetime

    favorites: int = 0
    heat: int = 0
    occupants: int = 0
    popularity: int = 0
    release_status: ReleaseStatusType = "public"


class UnityPackage(BaseModel):
    package_id: str = Field(alias="id")
    asset_version: int
    platform: str
    unity_version: str

    asset_url: Optional[str] = None
    asset_url_object: Optional[dict] = None
    created_at: Optional[datetime] = None
    plugin_url: Optional[str] = None
    plugin_url_object: Optional[dict] = None
    unity_sort_number: Optional[int] = None


class WorldModel(BaseModel):
    world_id: str = Field(alias="id")
    author_id: str
    author_name: str
    capacity: int
    recommended_capacity: int
    created_at: datetime
    description: str
    image_url: str
    labs_publication_date: str
    name: str
    namespace: str
    publication_date: str
    tags: List[str]
    thumbnail_image_url: str
    unity_packages: List[UnityPackage]
    updated_at: datetime

    favorites: int = 0
    featured: bool = False
    heat: int = 0
    occupants: int = 0
    organization: str = "vrchat"
    popularity: int = 0
    private_occupants: int = 0
    public_occupants: int = 0
    release_status: ReleaseStatusType = "public"
    version: int = 0
    visits: int = 0

    instances: Optional[List[Tuple[str, int]]] = None
    preview_youtube_id: Optional[str] = None
