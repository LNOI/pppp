import io
import logging
import datetime

from minio import Minio
from minio.error import S3Error
from minio.datatypes import Object

from src.const.global_map import RESOURCE_MAP
from src.utils.redis_caching import redis_cache_str


logger = logging.getLogger('utils_logger')


@redis_cache_str(lambda x: 's3_presign_url:%s' % x, expire_secs=3600*12)
def raw_minio_s3_presign_url(s3_key: str):
    try:
        client = Minio(
            RESOURCE_MAP['s3_cred']['MINIO_END_POINT'],
            access_key=RESOURCE_MAP['s3_cred']['MINIO_ACCESS_KEY_ID'],
            secret_key=RESOURCE_MAP['s3_cred']['MINIO_SECRET_ACCESS_KEY'],
            secure=True
        )
        url = client.get_presigned_url(
            "GET",
            RESOURCE_MAP['s3_cred']['MINIO_STORAGE_BUCKET_NAME'],
            s3_key,
            expires=datetime.timedelta(days=4),
        )
        return url
    except Exception as e:
        logger.info('Presign url error for url "%s".' % s3_key, exc_info=True)
        raise RuntimeError('Presign url error for url "%s".' % s3_key) from e


def minio_s3_presign_url(s3_key: str, cache_refresh: bool = False) -> str:
    # secondary_s3 = False
    # if not s3_key.startswith('media/'):
    #     return s3_key
    # if cache_refresh:
    #     RESOURCE_MAP['redis_conn'].delete('s3_presign_url:%s' % s3_key)
    # return raw_minio_s3_presign_url(s3_key, secondary_s3=secondary_s3)
    if s3_key.startswith("https://lh3.googleusercontent.com") or s3_key.startswith("https://graph.facebook.com"):
        return s3_key

    public_url = "http://media.sssmarket.com/sss-market-product/" + s3_key
    return public_url


def minio_download_to_bytes(s3_key: str) -> bytes:
    try:
        client = Minio(
            RESOURCE_MAP['s3_cred']['MINIO_END_POINT'],
            access_key=RESOURCE_MAP['s3_cred']['MINIO_ACCESS_KEY_ID'],
            secret_key=RESOURCE_MAP['s3_cred']['MINIO_SECRET_ACCESS_KEY'],
            secure=True
        )
        response = client.get_object(
            bucket_name=RESOURCE_MAP['s3_cred']['MINIO_STORAGE_BUCKET_NAME'],
            object_name=s3_key)
        try:
            bytearr = io.BytesIO(response.data).read()
            return bytearr
        except Exception as e:
            raise RuntimeError('Other error when read from key "%s".' % s3_key) from e
        finally:
            response.close()
            response.release_conn()

    except S3Error as e:
        if e.code == 'NoSuchKey':
            raise RuntimeError('The input key "%s" does not exist.' % s3_key) from e
        else:
            raise RuntimeError('Other download error for key "%s": %s' % (s3_key, e)) from e
    except Exception as e:
        raise RuntimeError('Other error for key "%s".' % s3_key) from e


def minio_upload_file(content: io.BytesIO, s3_key: str):
    try:
        client = Minio(
            RESOURCE_MAP['s3_cred']['MINIO_END_POINT'],
            access_key=RESOURCE_MAP['s3_cred']['MINIO_ACCESS_KEY_ID'],
            secret_key=RESOURCE_MAP['s3_cred']['MINIO_SECRET_ACCESS_KEY'],
            secure=True
        )
        content.seek(0)
        client.put_object(RESOURCE_MAP['s3_cred']['MINIO_STORAGE_BUCKET_NAME'],
                          object_name=s3_key,
                          data=content,
                          length=-1,
                          part_size=10*1024*1024)
    except Exception as e:
        raise RuntimeError('Upload error for key "%s".' % s3_key) from e


def minio_list_file(s3_key: str) -> list[Object]:
    try:
        client = Minio(
            RESOURCE_MAP['s3_cred']['MINIO_END_POINT'],
            access_key=RESOURCE_MAP['s3_cred']['MINIO_ACCESS_KEY_ID'],
            secret_key=RESOURCE_MAP['s3_cred']['MINIO_SECRET_ACCESS_KEY'],
            secure=True
        )
        objs = client.list_objects(
            RESOURCE_MAP['s3_cred']['MINIO_STORAGE_BUCKET_NAME'],
            prefix=s3_key
        )
        return list(objs)
    except Exception as e:
        logger.info('Presign url error for url "%s".' % s3_key, exc_info=True)
        raise RuntimeError('Presign url error for url "%s".' % s3_key) from e
