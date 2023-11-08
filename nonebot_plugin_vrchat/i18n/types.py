from pydantic import BaseModel


class I18NMetadata(BaseModel):
    name: str
    author: str


class I18NGeneral(BaseModel):
    help: str  # noqa: A003
    unknown_error: str
    server_error: str
    discard_select: str
    empty_search_keyword: str
    empty_message: str
    invalid_ordinal_format: str
    invalid_ordinal_range: str


class I18NLogin(BaseModel):
    not_logged_in: str
    login_expired: str
    overwrite_login_info: str
    send_login_info: str
    send_2fa_code: str
    use_cached_login_info: str
    discard_login: str
    invalid_account: str
    invalid_info_format: str
    invalid_2fa_format: str
    invalid_2fa_code: str
    logged_in: str


class I18NFriend(BaseModel):
    empty_friend_list: str


class I18NUser(BaseModel):
    send_user_name: str
    no_user_found: str
    searched_user_tip: str


class I18NWorld(BaseModel):
    send_world_name: str
    no_world_found: str
    searched_world_tip: str
    searched_world_info: str


class I18NLocale(BaseModel):
    available_locales_tip: str
    select_locale_tip: str
    locale_changed: str


class I18N(BaseModel):
    metadata: I18NMetadata
    general: I18NGeneral
    login: I18NLogin
    friend: I18NFriend
    user: I18NUser
    world: I18NWorld
    locale: I18NLocale
