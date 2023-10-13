from datetime import date, datetime
from typing import Dict, List, Literal, Optional, Tuple, TypeVar

from pydantic import BaseModel, Field

# 定义一个类型变量TM，这个类型变量只能接受BaseModel或者其子类作为输入
TM = TypeVar("TM", bound=BaseModel)

# 定义一些枚举类型常量
# 开发者类型，有"none", "trusted", "internal", "moderator"这四种可能
DeveloperType = Literal["none", "trusted", "internal", "moderator"]

# 状态类型，有"active", "join me", "ask me", "busy", "offline"这五种可能
StatusType = Literal["active", "join me", "ask me", "busy", "offline"]

# 一种可能的状态类型，有"offline", "active", "online"这三种可能
StateType = Literal["offline", "active", "online"]

# 群组隐私类型，有"default", "private"这两种可能
GroupPrivacyType = Literal["default", "private"]

# 群组加入状态类型，有"closed", "invite", "request", "open"这四种可能
GroupJoinStateType = Literal["closed", "invite", "request", "open"]

# 群组成员状态类型，有"inactive", "member", "requested", "invited"这四种可能
GroupMemberStatusType = Literal["inactive", "member", "requested", "invited"]

# 发布状态类型，有"public", "private", "hidden", "all"这四种可能
ReleaseStatusType = Literal["public", "private", "hidden", "all"]

# 定义一个状态类型的列表，包括"online", "webonline", "joinme", "busy", "askme", "offline", "unknown"这七种状态
NormalizedStatusType = Literal[
    "online",
    "webonline",
    "joinme",
    "busy",
    "askme",
    "offline",
    "unknown",
]

# 定义一个信任类型的列表，包括"visitor", "new", "user", "known", "trusted", "friend", "developer", "moderator"这八种信任状态
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

# 定义一个关于位置隐私的列表，包括"private", "public", "group_public"这三种可能
LOCATION_PRIVACY = Literal["private", "public", "group_public"]

# 定义一个映射字典，将一般状态类型映射到标准状态类型
NORMALIZE_STATUS_MAP: Dict[StatusType, NormalizedStatusType] = {
    "active": "online",
    "join me": "joinme",
    "busy": "busy",
    "ask me": "askme",
}

# 定义一个映射字典，将原始的信任标签映射到标准信任类型
NORMALIZE_TRUST_TAG_MAP: Dict[str, TrustType] = {
    "veteran": "trusted",
    "trusted": "known",
    "known": "user",
}

# 定义一个映射字典，将开发者类型标签映射到标准信任类型
DEVELOPER_TRUST_TYPE_MAP: Dict[str, TrustType] = {
    "internal": "developer",
    "moderator": "moderator",
}

# 定义一个信任标签的前缀字符串，用于标识系统信任的用户或消息等
TRUST_TAG_PREFIX = "system_trust_"


# 定义一个函数，用于将输入的状态类型进行标准化
def normalize_status(
    # 输入参数status，表示用户的状态类型，类型为StatusType（枚举类型）
    status: StatusType,
    # 输入参数location，表示用户的位置信息，类型为字符串（Optional[str]表示可以为空）
    location: Optional[str],
) -> NormalizedStatusType:
    # 如果位置信息为"offline"，则判断状态类型是否为"active"
    if location == "offline":
        if status == "active":
            # 如果状态类型为"active"，则返回"webonline"
            return "webonline"
        # 如果状态类型不为"active"，则返回"offline"
        return "offline"
    # 如果位置信息不为"offline"，则根据NORMALIZE_STATUS_MAP字典进行状态标准化，默认返回"unknown"
    return NORMALIZE_STATUS_MAP.get(status, "unknown")


# 定义一个函数，用于提取用户的信任等级
def extract_trust_level(tags: List[str], developer_type: Optional[str]) -> TrustType:
    # 如果开发者类型在DEVELOPER_TRUST_TYPE_MAP字典中存在，则返回对应的信任等级
    if developer_type in DEVELOPER_TRUST_TYPE_MAP:
        return DEVELOPER_TRUST_TYPE_MAP[developer_type]

    # 遍历NORMALIZE_TRUST_TAG_MAP字典中的后缀，判断是否存在以TRUST_TAG_PREFIX（信任标签前缀）开头的字符串
    for suffix in NORMALIZE_TRUST_TAG_MAP:
        if f"{TRUST_TAG_PREFIX}{suffix}" in tags:
            # 如果存在，则返回对应的信任等级
            return NORMALIZE_TRUST_TAG_MAP[suffix]

    # 如果以上条件都不满足，则返回默认的信任等级为"visitor"
    return "visitor"


# 定义一个LimitedUserModel类，继承自BaseModel
class LimitedUserModel(BaseModel):
    # 定义用户ID字段，并设置别名"id"
    user_id: str = Field(alias="id")
    # 定义用户当前头像的URL
    current_avatar_image_url: str
    # 定义用户当前头像缩略图的URL
    current_avatar_thumbnail_image_url: str
    # 定义开发者类型，类型为DeveloperType（枚举类型）
    developer_type: DeveloperType
    # 定义用户展示名称
    display_name: str
    # 定义是否为好友关系，类型为布尔型
    is_friend: bool
    # 定义用户最后登录的平台
    last_platform: str
    # 定义用户资料图片的URL
    profile_pic_override: str
    # 定义用户原始状态类型，并设置别名"status"
    original_status: StatusType = Field(alias="status")
    # 定义用户状态的描述信息
    status_description: str
    # 定义用户的标签列表，类型为字符串列表
    tags: List[str]
    # 定义用户的图标URL
    user_icon: str

    # 定义用户的个人简介信息，类型为字符串，可以为空
    bio: Optional[str] = None
    # 定义用户的备用头像URL，类型为字符串，可以为空
    fallback_avatar: Optional[str] = None
    # 定义用户的位置信息，类型为字符串，可以为空
    location: Optional[str] = None
    # 定义用户的友好关系key，类型为字符串，可以为空
    friend_key: Optional[str] = None
    # 定义用户最后登录的时间，类型为datetime，可以为空
    last_login: Optional[datetime] = None


# 定义一个装饰器，将状态属性进行重命名，不再使用原始的"original_status"属性名
@property
def status(self) -> NormalizedStatusType:
    return normalize_status(self.original_status, self.location)


# 定义一个装饰器，提取用户的信任等级，不再使用原始的"tags"和"developer_type"属性名
@property
def trust(self) -> TrustType:
    return extract_trust_level(self.tags, self.developer_type)


# 定义一个用户模型类，继承自BaseModel基类
class UserModel(BaseModel):
    # 用户ID，作为主键, 使用Field装饰器可能表示该字段在数据库中的别名是"id"
    user_id: str = Field(alias="id")

    # 用户的个性化描述信息，可能是文本形式
    bio: str

    # 用户提供的链接列表，可能是文本形式的URL
    bio_links: List[str]

    # 用户当前头像的URL
    # 这个字段的类型是字符串，表示图片的URL
    current_avatar_image_url: str

    # 用户当前头像缩略图的URL
    # 这个字段的类型也是字符串，表示缩略图的URL
    current_avatar_thumbnail_image_url: str

    # 用户加入日期，数据类型为date，可能是datetime的别名
    date_joined: date

    # 用户开发者类型，可能是一个枚举类型，具体定义在DeveloperType中
    developer_type: DeveloperType

    # 用户的展示名称，可能是一个字符串
    display_name: str

    # 用户的友好关系key，可能是一个字符串
    friend_key: str

    # 表示用户之间是否为好友关系的布尔值, True表示是好友, False表示不是
    is_friend: bool

    # 用户最近一次活跃的日期和时间信息，可能是字符串形式的时间戳
    last_activity: str

    # 用户最近登录的日期和时间信息，可能是字符串形式的时间戳
    last_login: str

    # 用户最后登录的平台，可能是一个字符串，比如"web","android"等等
    last_platform: str

    # 用户资料图片的URL，可能是一个字符串
    profile_pic_override: str

    # 用户的当前状态，可能是一个枚举类型，具体定义在StateType中
    state: StateType

    # 用户的原始状态，状态信息的具体字段别名是'status'，与status字段相同作用。可以用于多字段状态的具体表示。
    original_status: StatusType = Field(alias="status")

    # status_description是用来描述用户状态的字符串
    status_description: str

    # tags是存储用户标签的字符串列表
    tags: List[str]

    # user_icon是存储用户图标URL的字符串
    user_icon: str

    # allow_avatar_copying是一个布尔值，表示是否允许复制用户头像，默认为True
    allow_avatar_copying: bool = True

    # instance_id是一个字符串，表示实例的ID，默认为"offline"
    instance_id: str = "offline"

    # friend_request_status表示朋友请求的状态，默认为None，可能为'accepted', 'pending', 'rejected'等
    friend_request_status: Optional[str] = None

    # note是用户的备注信息，默认为None
    note: Optional[str] = None

    # location是用户的地理位置信息，默认为None
    location: Optional[str] = None

    # traveling_to_instance表示用户正在旅行的目的地的实例ID，默认为None
    traveling_to_instance: Optional[str] = None

    # traveling_to_location表示用户正在旅行的位置信息，默认为None
    traveling_to_location: Optional[str] = None

    # traveling_to_world表示用户正在旅行的世界的ID信息，默认为None
    traveling_to_world: Optional[str] = None

    # world_id表示用户所在世界的ID信息，默认为None
    world_id: Optional[str] = None

    # 定义一个名为status的只读属性，返回的是self.original_status和self.location经过normalize_status函数处理后的结果，具体类型为NormalizedStatusType
    @property
    def status(self) -> NormalizedStatusType:
        return normalize_status(self.original_status, self.location)

    # 定义一个名为trust的只读属性，返回的是self.tags和self.developer_type经过extract_trust_level函数处理后的结果，具体类型为TrustType
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
