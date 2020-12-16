# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import base64
from django.shortcuts import render
from blueking.component.shortcuts import get_client_by_request, get_client_by_user
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .task import get_job_status
from .models import ScriptList, JobHistory
from datetime import datetime
import json


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, "home_application/index.html")


def dev_guide(request):
    """
    开发指引
    """
    return render(request, "home_application/exec_script.html")


def contact(request):
    """
    联系页
    """
    return render(request, "home_application/script_job.html")

def res_fun(data=None, result=True, message="ok", code=200):
    return {"data": data, "result": result, "message": message, "code": code}


def search_business(request):
    """
    查找业务

    """
    client = get_client_by_request(request)
    res = client.cc.search_business()
    biz = []
    if res.get('result'):
        for info in res['data']['info']:
            biz.append({
                'id': info['bk_biz_id'] or info['bid'],
                'name': info['bk_biz_name']
            })
        return JsonResponse(res_fun(biz,res['result'], res['message'],200)) 
    else:
        return JsonResponse(res_fun(res['data'],res['result'], res['message'],res['code']))


def search_host(request):
    """
    查找主机
    """
    page = request.POST.get('page')
    pageSize = int(request.POST.get('pageSize'))
    bk_biz_id = request.POST.get("bk_biz_id")

    # if not all([bk_biz_id, bk_inst_id, bk_obj_id]):
    #     return JsonResponse({"error": "请求参数错误"})

    kwargs = {
        "bk_biz_id": bk_biz_id,
    }
    client = get_client_by_request(request)
    result = client.cc.search_host(kwargs)
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    paginator = Paginator(result, pageSize)
    response['total'] = paginator.count
    if not result["result"]:
        return JsonResponse({"error": "请求主机列表出现错误"})

    host_list = []
    for info in result["data"]["info"]:
        host_list.append(info["host"])
        response['data'] = host_list
    return JsonResponse(response)

def get_script_list(request):
    """
    查找脚本列表
    """
    page = request.POST.get('page')
    pageSize = int(request.POST.get('pageSize'))
    bk_biz_id = request.POST.get("bk_biz_id")
    scriptType = request.POST.get("type")
    name = request.POST.get("name")
    return_script_content = request.POST.get("return_script_content")

    # if not all([bk_biz_id, bk_inst_id, bk_obj_id]):
    #     return JsonResponse({"error": "请求参数错误"})

    kwargs = {
        "bk_biz_id": bk_biz_id,
        "return_script_content": return_script_content
    }
    client = get_client_by_request(request)
    result = client.job.get_script_list(kwargs)
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    paginator = Paginator(result, pageSize)
    response['total'] = paginator.count
    if not result["result"]:
        return JsonResponse({"error": "请求脚本列表出现错误"})
    host_list = []
    for info in result["data"]["data"]:
        host_list.append(info)
        response['data'] = host_list
    return JsonResponse(response)

def get_script_detail(request):
    """
    查找脚本详情
    """
    bk_biz_id = request.POST.get("bk_biz_id")
    script_id = request.POST.get("id")

    # if not all([bk_biz_id, bk_inst_id, bk_obj_id]):
    #     return JsonResponse({"error": "请求参数错误"})

    kwargs = {
        "bk_biz_id": bk_biz_id,
        "id": script_id
    }
    client = get_client_by_request(request)
    result = client.job.get_script_detail(kwargs)
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    if not result["result"]:
        return JsonResponse({"error": "请求脚本详情出现错误"})
        response['data'] =  result["data"]
    return JsonResponse(response)
def sync_local_db(request):
    """
    同步数据
    """
    page = request.POST.get('page')
    pageSize = int(request.POST.get('pageSize'))
    bk_biz_id = request.POST.get("bk_biz_id")
    return_script_content = request.POST.get("return_script_content")
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "return_script_content": return_script_content
    }
    client = get_client_by_request(request)
    result = client.job.get_script_list(kwargs)
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    paginator = Paginator(result, pageSize)
    response['total'] = paginator.count
    if not result["result"]:
        return JsonResponse({"error": "请求脚本列表出现错误"})
    host_list = []
    for info in result["data"]["data"]:
        script_list = ScriptList.objects.filter(script_id = info["id"])
        if script_list.exists():
            print("yes,we have this email")
        else:
            ScriptList.objects.create(
                    script_id=info["id"],
                    public=1,
                    script_type=info["type"],
                    name=info["name"],
                    content=info["content"],
                    create_time=info["create_time"],
                    bk_biz_id=info["bk_biz_id"]
                )
        response['data'] = ''
        response['message'] = '同步成功'
    return JsonResponse(response)

def fast_execute_script(request):
    """
    执行脚本
    """
    script_id = request.POST.get("script_id")
    script_name = request.POST.get("script_name")
    bk_biz_id = request.POST.get("bk_biz_id")
    scipt_param = request.POST.get("scipt_param")
    ips = request.POST.get("ips")
    ip_list = []
    # str(base64.b64encode(scipt_param.encode("utf-8")), "utf-8")
    for ip in ips.split(','):
        ip_list.append({"bk_cloud_id": 0, "ip": ip})
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "script_id": script_id,
        "account": "root",
        # "script_param": str(base64.b64encode(scipt_param.encode("utf-8")), "utf-8"),
        "ip_list": ip_list
    }
    client = get_client_by_request(request)
    result = client.job.fast_execute_script(kwargs)
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    if not result["result"]:
        return JsonResponse({"error": "执行脚本列表出现错误"})
    JobHistory.objects.create(
        bk_biz_id= bk_biz_id, # 业务ID
        bk_biz_name='考试',
        ip_list=ips, # 主机列表
        job_instance_id = result["data"]["job_instance_id"],
        job_instance_name = result["data"]["job_instance_name"],
        script_id = script_id,
        script_name = script_name,
        job_status = 0,
        execute_time=timezone.now(),
        end_time=timezone.now()
    )
    get_job_status.apply_async(args=(client, bk_biz_id, result["data"]["job_instance_id"]))
    response["data"] = result['data']
    response['message'] = '执行成功'
    return JsonResponse(response)

def get_local_list(request):
    page = request.POST.get('page')
    pageSize = int(request.POST.get('pageSize'))
    nme_script = request.POST.get('name')
    script_type = request.POST.get('souceScript')
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    if not all([script_type]):
        response['message'] = '查询条件错误！'
        response['code'] = -1
        return JsonResponse(response)
    book_list = ScriptList.objects.filter(public=script_type, name__contains=nme_script).order_by('-id')
    paginator = Paginator(book_list.all(), pageSize)
    response['total'] = paginator.count
    lst = []
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    for item in books:
        dic = {
            "script_id": item.id,
            "public":item.public,
            "type":item.script_type,
            "name":item.name,
            "content":item.content,
            "create_time":item.create_time,
            "bk_biz_id":item.bk_biz_id
        }
        lst.append(dic)
        response['data'] = lst
    return JsonResponse(response)

def get_add(request):
    name = request.POST.get('name')
    content_script = request.POST.get('content')
    typeScript = request.POST.get('type')
    response = {
            "result": True,
            "message": "",
            "code": 200,
            "data": []
            }
    ScriptList.objects.create(
                    script_id=0,
                    public=1,
                    script_type=typeScript,
                    name=name,
                    content=content_script,
                    create_time=timezone.now(),
                    bk_biz_id=4
                )
    response['message'] = '新增成功！'
    return JsonResponse(response)
def remove_list(request):
    removeId = request.POST.get('id')
    response = {'code': 1, 'message': '删除成功!'}
    script_list = ScriptList.objects.get(id = removeId).delete()
    return JsonResponse(response)
def update_list(request):
    getId = request.POST.get('id')
    name = request.POST.get('name')
    content_script = request.POST.get('content')
    typeScript = request.POST.get('type')
    response = {'code': 1, 'message': '修改成功!'}
    detail_list = ScriptList.objects.filter(id = getId).update(script_id=0,
                    public=1,
                    script_type=typeScript,
                    name=name,
                    content=content_script,
                    create_time=timezone.now(),
                    bk_biz_id=4)
    return JsonResponse(response)

def get_history(request):
    page = request.POST.get('page')
    pageSize = int(request.POST.get('pageSize'))
    endTime = request.POST.get('endTime')
    startTime = request.POST.get('startTime')
    bk_biz_id = request.POST.get('bk_biz_id')
    response = {}
    history_list = JobHistory.objects.filter(execute_time__range = [startTime, endTime], bk_biz_id= bk_biz_id).order_by('-id')
    paginator = Paginator(history_list, pageSize)
    response['total'] = paginator.count
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    result = []
    for row in books:
        r = {
            'id':  row.id,
            'bk_biz_name': row.bk_biz_name,
            'script_name': row.script_name,
            'ip_list': row.ip_list,
            'job_instance_id': row.job_instance_id,
            'job_instance_name': row.job_instance_name,
            'create_time': row.execute_time,
            'job_status': row.job_status,
            'finish_time': row.end_time,
            'bk_job_log': row.bk_job_log,
            "results": []
        }
        result.append(r)
    return JsonResponse(res_fun(result,True, '操作成功',200))