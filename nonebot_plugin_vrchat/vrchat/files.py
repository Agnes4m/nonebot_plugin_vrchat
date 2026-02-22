from typing import Awaitable, List, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, FilesApi

from .types import FileModel, FileVersionModel


async def create_file(
    client: ApiClient,
    create_file_request: dict,
) -> FileModel:
    """创建文件

    Args:
        client: ApiClient 实例
        create_file_request: 创建文件请求对象

    Returns:
        文件信息
    """
    from vrchatapi.models import CreateFileRequest

    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.create_file)(
            create_file_request=CreateFileRequest(**create_file_request),
        ),
    )
    return (
        FileModel(**result)
        if isinstance(result, dict)
        else FileModel.model_validate({})
    )


async def create_file_version(
    client: ApiClient,
    file_id: str,
    create_file_version_request: dict,
) -> FileVersionModel:
    """创建文件版本

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        create_file_version_request: 创建文件版本请求对象

    Returns:
        文件版本信息
    """
    from vrchatapi.models import CreateFileVersionRequest

    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.create_file_version)(
            file_id=file_id,
            create_file_version_request=CreateFileVersionRequest(
                **create_file_version_request,
            ),
        ),
    )
    return (
        FileVersionModel(**result)
        if isinstance(result, dict)
        else FileVersionModel.model_validate({})
    )


async def get_file(client: ApiClient, file_id: str) -> FileModel:
    """获取文件信息

    Args:
        client: ApiClient 实例
        file_id: 文件 ID

    Returns:
        文件信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_file)(file_id=file_id),
    )
    return (
        FileModel(**result)
        if isinstance(result, dict)
        else FileModel.model_validate({})
    )


async def get_files(
    client: ApiClient,
    n: int = 20,
    offset: int = 0,
) -> List[FileModel]:
    """获取文件列表

    Args:
        client: ApiClient 实例
        n: 返回数量
        offset: 偏移量

    Returns:
        文件列表
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_files)(n=n, offset=offset),
    )
    return [FileModel(**r.to_dict()) for r in result] if result else []


async def delete_file(client: ApiClient, file_id: str) -> bool:
    """删除文件

    Args:
        client: ApiClient 实例
        file_id: 文件 ID

    Returns:
        是否删除成功
    """
    api = FilesApi(client)
    await run_sync(api.delete_file)(file_id=file_id)
    return True


async def delete_file_version(
    client: ApiClient,
    file_id: str,
    version: int,
) -> bool:
    """删除文件版本

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号

    Returns:
        是否删除成功
    """
    api = FilesApi(client)
    await run_sync(api.delete_file_version)(
        file_id=file_id,
        version_id=version,
    )
    return True


async def get_file_analysis(
    client: ApiClient,
    file_id: str,
    version: int,
) -> dict:
    """获取文件分析信息

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号

    Returns:
        文件分析信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_file_analysis)(
            file_id=file_id,
            version_id=version,
        ),
    )
    return result if isinstance(result, dict) else {}


async def get_file_analysis_standard(
    client: ApiClient,
    file_id: str,
    version: int,
) -> dict:
    """获取文件标准分析信息

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号

    Returns:
        文件分析信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_file_analysis_standard)(
            file_id=file_id,
            version_id=version,
        ),
    )
    return result if isinstance(result, dict) else {}


async def get_file_analysis_security(
    client: ApiClient,
    file_id: str,
    version: int,
) -> dict:
    """获取文件安全分析信息

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号

    Returns:
        文件分析信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_file_analysis_security)(
            file_id=file_id,
            version_id=version,
        ),
    )
    return result if isinstance(result, dict) else {}


async def start_file_data_upload(
    client: ApiClient,
    file_id: str,
    version: int,
) -> dict:
    """开始文件数据上传

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号

    Returns:
        上传 URL 信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.start_file_data_upload)(
            file_id=file_id,
            version_id=version,
        ),
    )
    return result if isinstance(result, dict) else {}


async def finish_file_data_upload(
    client: ApiClient,
    file_id: str,
    version: int,
    finish_file_data_upload_request: dict,
) -> FileModel:
    """完成文件数据上传

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号
        finish_file_data_upload_request: 完成上传请求对象

    Returns:
        文件信息
    """
    from vrchatapi.models import FinishFileDataUploadRequest

    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.finish_file_data_upload)(
            file_id=file_id,
            version_id=version,
            finish_file_data_upload_request=FinishFileDataUploadRequest(
                **finish_file_data_upload_request,
            ),
        ),
    )
    return (
        FileModel(**result)
        if isinstance(result, dict)
        else FileModel.model_validate({})
    )


async def get_file_data_upload_status(
    client: ApiClient,
    file_id: str,
    version: int,
) -> dict:
    """获取文件数据上传状态

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        version: 版本号

    Returns:
        上传状态信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_file_data_upload_status)(
            file_id=file_id,
            version_id=version,
        ),
    )
    return result if isinstance(result, dict) else {}


async def upload_image(
    client: ApiClient,
    file_id: str,
    file_data: bytes,
    tag: str | None = None,
) -> FileModel:
    """上传图片文件

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        file_data: 文件数据
        tag: 标签

    Returns:
        文件信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.upload_image)(
            fileId=file_id,
            file=file_data,
            tag=tag,
        ),
    )
    return (
        FileModel(**result)
        if isinstance(result, dict)
        else FileModel.model_validate({})
    )


async def upload_icon(
    client: ApiClient,
    file_id: str,
    file_data: bytes,
) -> FileModel:
    """上传图标文件

    Args:
        client: ApiClient 实例
        file_id: 文件 ID
        file_data: 文件数据

    Returns:
        文件信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.upload_icon)(
            fileId=file_id,
            file=file_data,
        ),
    )
    return (
        FileModel(**result)
        if isinstance(result, dict)
        else FileModel.model_validate({})
    )


async def upload_gallery_image(
    client: ApiClient,
    group_id: str,
    gallery_id: str,
    file_data: bytes,
) -> FileModel:
    """上传画廊图片

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        gallery_id: 画廊 ID
        file_data: 文件数据

    Returns:
        文件信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.upload_gallery_image)(
            groupId=group_id,
            galleryId=gallery_id,
            file=file_data,
        ),
    )
    return (
        FileModel(**result)
        if isinstance(result, dict)
        else FileModel.model_validate({})
    )


async def get_content_agreement_status(client: ApiClient) -> dict:
    """获取内容协议状态

    Args:
        client: ApiClient 实例

    Returns:
        协议状态信息
    """
    api = FilesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_content_agreement_status)(),
    )
    return result if isinstance(result, dict) else {}


async def submit_content_agreement(client: ApiClient, agreed: bool) -> bool:
    """提交内容协议

    Args:
        client: ApiClient 实例
        agreed: 是否同意

    Returns:
        是否提交成功
    """
    api = FilesApi(client)
    await run_sync(api.submit_content_agreement)(agreed=agreed)
    return True
