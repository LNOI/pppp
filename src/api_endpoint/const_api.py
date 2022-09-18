import os
import io

import json
import sys

from fastapi import Request

from src.const.global_map import RESOURCE_MAP
from src.utils.s3_utils import minio_download_to_bytes, minio_upload_file
from src.const import const_map as CONST_MAP
from src.utils.basemodel.response_schemas import create_response


app = RESOURCE_MAP['fastapi_app']


@app.get('/const')
async def get_const():
    """
    Input: CONST_MAP
    Process: get key in CONST_MAP
    :return: value of key
    """
    answer = {}
    for key in CONST_MAP.__dir__():
        if not str(key).startswith('__'):
            value = getattr(CONST_MAP, key)
            if type(value) is not type(sys):
                answer[key] = value
    return create_response(status=200, content=json.dumps(answer))


@app.get("/const_reload")
async def reload_const():
    try:
        res = minio_download_to_bytes(CONST_MAP.config_file_key)
        input_map = json.loads(res.decode(encoding='utf-8'))
        answer = {}
        for key in input_map:
            setattr(CONST_MAP, key, input_map[key])
            answer[key] = getattr(CONST_MAP, key)
        return create_response(status=200, content=json.dumps(answer))
    except RuntimeError as e:
        return create_response(status=500, content=json.dumps(str(e)))
    

@app.get("/const_store")
async def store_const():
    try:
        answer = {}
        for key in CONST_MAP.__dir__():
            if not str(key).startswith('__'):
                value = getattr(CONST_MAP, key)
                if type(value) is not type(sys):
                    answer[key] = value
        with open('temp.json', 'w') as f:
            json.dump(answer, f, indent=4, ensure_ascii=False)
        with open('temp.json', 'rb') as bf:
            bio = io.BytesIO()
            bio.write(bf.read())
        minio_upload_file(bio, 'media/server_config_file/fashion_config.json')
        os.remove('temp.json')
        return create_response(status=200,content=json.dumps("Oke"))
    except RuntimeError as e:
        return create_response(status=500,content=json.dumps(str(e)))

@app.post('/const_update')
async def update_const(request: Request):
    """
    Input: Request key
    Process: Update new value for key in CONST_MAP
    :return: new key-value
    """
    input_map = await request.json()
    answer = {}
    for key in input_map:
        setattr(CONST_MAP, key, input_map[key])
        answer[key] = getattr(CONST_MAP, key)
    return create_response(status=200, content=json.dumps(answer))
