from datetime import date, datetime
from typing import Dict, List, Literal, Optional, Tuple, TypeVar

from pydantic import BaseModel, Field
from vrchatapi import LimitedUser

from .utils import patch_api_model_append_attr

TM = TypeVar("TM", bound=BaseModel)

DeveloperType = Literal["none", "trusted", "internal", "moderator"]
"""用户开发等级"""
StatusType = Literal["active", "join me", "ask me", "busy", "offline"]
StateType = Literal["offline", "active", "online"]
GroupPrivacyType = Literal["default", "private"]
GroupJoinStateType = Literal["closed", "invite", "request", "open"]
GroupMemberStatusType = Literal["inactive", "member", "requested", "invited"]
ReleaseStatusType = Literal["public", "private", "hidden", "all"]
PlatfoemType = Literal

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
    """
    将 `StatusType` 转为 `NormalizedStatusType`

    Args:
        status: user.status
        location: user.location

    Returns:
        转换后的 `NormalizedStatusType`
    """

    if location == "offline":
        if status == "active":
            return "webonline"
        return "offline"
    return NORMALIZE_STATUS_MAP.get(status, "unknown")


def extract_trust_level(tags: List[str], developer_type: Optional[str]) -> TrustType:
    """
    从用户的 Tag 中提取用户的信任等级

    Args:
        tags: user.tags
            "system_no_captcha",  # 无验证
            "system_avatar_access",  # 头像接口
            "system_world_access",  # 世界接口
            "system_feedback_access",  # 反馈接口
            "system_trust_basic",  # 蓝名
            "system_trust_trusted",  # 绿名
            "system_trust_veteran",  # 橙名
            "system_trust_known",  # 紫名
            "show_social_rank",  # 排行榜
            # 语言
            "language_zho",  # 中文
            "language_yue",  # 粤语
            "language_jpn",  # 日语
            "language_eng",  # 英语
            "language_kor",  # 韩语
            "language_fra",  # 法语
            "language_vie",  # 越南语
            "language_rus",  # 俄语
        developer_type: user.developer_type

    Returns:
        用户的信任等级
    """

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
    """陌生人信息"""

    user_id: str = Field(alias="id")
    """用户id"""
    current_avatar_image_url: str
    """头像url"""
    developer_type: DeveloperType
    """开发者模式"""
    display_name: str
    """姓名"""
    is_friend: bool
    last_platform: str
    """
    - standalonewindows : 桌面端
    - android : 安卓
    - 其他unity版本 : 2019.3.1p2-845-Release
    """
    original_status: StatusType = Field(alias="status")
    status_description: str
    tags: List[str]

    current_avatar_thumbnail_image_url: Optional[str] = None
    """缩略图头像url"""
    bio: Optional[str] = None
    fallback_avatar: Optional[str] = None
    """备用着色器"""
    location: Optional[str] = None
    friend_key: Optional[str] = None
    last_login: Optional[datetime] = None
    profile_pic_override: str = ""
    user_icon: str = ""
    index: int = 0

    @property
    def status(self) -> NormalizedStatusType:
        return normalize_status(self.original_status, self.location)

    @property
    def trust(self) -> TrustType:
        return extract_trust_level(self.tags, self.developer_type)


class Badge(BaseModel):
    """徽章"""

    assigned_at: datetime
    badge_description: str
    badge_id: str
    badge_image_url: str
    badge_name: str
    hidden: bool
    showcased: bool
    updated_at: datetime


class UserModel(BaseModel):
    """信任用户信息"""

    user_id: str = Field(alias="id")

    age_verification_status: Literal["hidden"]
    """未知"""
    age_verified: bool
    """年龄验证状态"""
    allow_avatar_copying: bool = True
    """允许复制模型"""
    badges: Optional[List[Badge]] = None
    bio: str
    """用户简介"""
    bio_links: List[str]
    current_avatar_image_url: str
    current_avatar_thumbnail_image_url: str
    """当前头像缩略图url"""
    current_avatar_tags: List[str]
    date_joined: date
    """加入日期"""
    developer_type: DeveloperType
    """开发者模式"""
    display_name: str
    """用户名"""
    friend_key: str
    friend_request_status: str = "null"
    instance_id: Literal["offline", "private"]
    """非好友是离线,好友处于私人状态是私密"""
    is_friend: bool
    last_activity: str
    last_login: str
    last_mobile: Optional[str] = None
    last_platform: str
    """
    - standalonewindows : 桌面端
    - android : 安卓
    - 其他unity版本 : 2019.3.1p2-845-Release
    """
    location: Optional[str] = "offline"
    note: Optional[str] = None
    platform: Optional[str] = "offline"
    profile_pic_override: str
    profile_pic_override_thumbnail: str
    pronouns: str
    state: StateType
    status_description: str
    tags: List[str]
    original_status: StatusType = Field(alias="status")
    traveling_to_instance: Optional[str] = None
    traveling_to_location: Optional[str] = None
    traveling_to_world: Optional[str] = None
    user_icon: str
    # username: str 弃用
    world_id: str = "offline"

    @property
    def status(self) -> NormalizedStatusType:
        return normalize_status(self.original_status, self.location)

    @property
    def trust(self) -> TrustType:
        return extract_trust_level(self.tags, self.developer_type)


class GroupGalleryModel(BaseModel):
    """群组信息"""

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
    """信任群组信息"""

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
    """群组规则信息"""

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
    """群组信息"""

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
    """一般unity相关信息"""

    platform: str
    unity_version: str


class LimitedWorldModel(BaseModel):
    """一般世界信息"""

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
    """信任unity相关信息"""

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
    """信任世界信息"""

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
    namespace: Optional[str] = None
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
