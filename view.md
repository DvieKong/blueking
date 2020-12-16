

# 安装pipenv

- 这一步是必要的 免得影响老版本框架的本地开发环境
- 安装 pipenv

- - `pip install pipenv`

- 创建虚拟环境

- - 删除 requirement.txt 的中文注释部分
  - 项目文件夹中 `pipenv install`
  - 上一步可能会比较慢 可以修改`Pipfile`文件中的链接为[`https://mirrors.aliyun.com/pypi/simple`](https://mirrors.aliyun.com/pypi/simple)

- 进入虚拟环境

- - `pipenv shell`

# 3.3.1.92框架

```python
dev.py

BROKER_URL = "redis://127.0.0.1:6379/0"

default.py

USE_TZ = False
DJANGO_CELERY_BEAT_TZ_AWARE = False

在if IS_USE_CELERY 增加如下配置
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = {'pickle'} 
```

# 启动celery

- worker **添加了一个参数(-P eventlet)**

- - `python manage.py celery worker -l info -P eventlet`

- beat 无改动

- - `python manage.py celery beat -l info`

# 查询业务

```python
class SearchBusiness(View):

    def get(self, request):
        """
        获取业务
        :param request:
        :return:
        """
        client = get_client_by_request(request)
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        kwargs = {
            "fields": [
                "bk_biz_id",
                "bk_biz_name"
            ],
        }
        res = client.cc.search_business(kwargs)
        if res.get('result', False):
            resp['data'] = res['data']['info']
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 查询拓扑

```python
class SearchBizInstTopo(View):

    def get(self, request):
        """
        获取拓扑
        :param request:
        :return:
        """
        client = get_client_by_request(request)
        bk_biz_id = request.GET.get('bk_biz_id')
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        kwargs = {
            "bk_biz_id": bk_biz_id,
        }
        res = client.cc.search_biz_inst_topo(kwargs)
        if res.get('result', False):
            resp['data'] = self.get_node(res['data'])
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
    
    def get_node(self, result):
        """
        处理节点信息，生成树结构
        :param result:
        :return:
        """
        bk_biz_tree = []
        for data in result:
            bk_biz_tree.append({
                'name': data['bk_inst_name'],
                'title': data['bk_inst_name'],
                'id': data['bk_inst_id'],
                'bk_obj_id': data['bk_obj_id'],
                "children": self.get_node(data['child']) if data['child'] and len(data['child']) > 0 else []
            })
        return bk_biz_tree
```

# 根据拓扑查询主机

```python

class SearchHost(View):

    def get(self, request):
        """
        获取主机
        :param request:
        :return:
        """
        client = get_client_by_request(request)
        bk_biz_id = request.GET.get('bk_biz_id')
        bk_inst_id = request.GET.get('bk_inst_id')
        bk_obj_id = request.GET.get('bk_obj_id')
        if not all([bk_biz_id,bk_inst_id,bk_obj_id]):
            resp['result'] = False
            resp['code'] = -1
            resp['message'] = u'缺少参数'
            return JsonResponse(resp)
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        kwargs = {
            'bk_biz_id': bk_biz_id,
            "condition": [
                {
                    "bk_obj_id": bk_obj_id,
                    "fields": [],
                    "condition": [
                        {
                            "field": "bk_{}_id".format(bk_obj_id),
                            "operator": "$eq",
                            "value": bk_inst_id
                        }
                    ]
                }]
        }
        res = client.cc.search_host(kwargs)
        if res.get('result', False):
            resp['data'] = [item['host'] for item in res['data']['info']]
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 根据脚本id-执行脚本

```python
class FastExecuteScript(View):
    """
    执行脚本
    """
    def post(self, request):
        # 脚本id
        id = 1357
        data = json.loads(request.body.decode())
        client = get_client_by_request(request)
        bk_biz_id = data.get('bk_biz_id')
        bk_biz_name = data.get('bk_biz_name')
        execute_way = data.get('execute_way')
        params = data.get('params')
        ip_list = data.get('ip_list')
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        script_param = execute_way + ' ' + params
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "script_id": id,
            "script_param": base64.b64encode(script_param.encode()).decode(),
            "script_timeout": 1000,
            "account": "root",
            "script_type": 1,
            "ip_list": ip_list,
        }
        res = client.job.fast_execute_script(kwargs)
        ips = ','.join([item['ip'] for item in ip_list])
        if res.get('result', False):
            job_instance_id = res['data']['job_instance_id']
            HistoryInfo.objects.create(
                bk_biz_name=bk_biz_name,
                bk_biz_id=bk_biz_id,
                script_param=script_param,
                job_instance_id=job_instance_id,
                ip_list=ips
            )
            save_execute_script_logs.delay(client, bk_biz_id, job_instance_id)
            resp['data'] = res['data']
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 查询脚本的 执行详情

```python
import json
import time
from celery import task
from home_application.models import HistoryInfo

@task()
def save_execute_script_logs(client, bk_biz_id, job_instance_id):
    """
    保存执行历史
    :param client:
    :param bk_biz_id:
    :param job_instance_id:
    :return:
    """
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "job_instance_id": job_instance_id
    }
    count = 0
    while count < 10:
        res = client.job.get_job_instance_log(kwargs)
        data = res.get('data')
        if data[0]['status'] == 3:
            logs = data[0]['step_results'][0]['ip_logs']
            HistoryInfo.objects.filter(job_instance_id=job_instance_id).update(
                logs=json.dumps(logs),
                job_is_finished=True
            )
        count += 1
        time.sleep(1)
```

# 通过流程模板创建任务

```python
class CreateTask(View):
    def post(self, request):
        """
        通过流程模板创建任务
        :param request:
        :return:
        """
        template_id = 25
        template_name = 'luoxi_task_test' # 自定义
        client = get_client_by_request(request)
        data = json.loads(request.body.decode())
        bk_biz_id = data.get('bk_biz_id')
        job_ip_list = data.get('job_ip_list')
        push_ip_list = data.get('push_ip_list')
        bk_biz_name = data.get('bk_biz_name')
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "name": template_name,
            "template_id": template_id,
            "constants": {
                "${job_ip_list}": job_ip_list,
                "${push_ip_list}": push_ip_list,
                "${job_script_param}": request.user.username,
                "${job_source_files}": [
                    {
                        "ip": job_ip_list,
                        "files": "/tem/test-" + request.user.username + '.txt',
                        "account": "root"
                    }
                ]
            }
        }
        res = client.sops.create_task(kwargs)
        if res.get('result', False):
            task_url = res['data']['task_url']
            # task_id = res['data']['task_id']
            task_id = 1441
            resp['data'] = {
                'task_id': task_id,
                'task_url': task_url
            }
            try:
                history = HistoryInfo.objects.create(
                    bk_biz_name=bk_biz_name,
                    bk_biz_id=bk_biz_id,
                    task_url=task_url,
                    task_name=template_name,
                    template_id=template_id,
                    task_id=task_id,
                )
            except Exception as err:
                print(err)
                resp['result'] = False
                resp['message'] = 'false'
            else:
                history.save()
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 查询模板列表

```python
# 查询模板列表
def get_template_list_views(request):
    if request.method == 'GET':
        bk_biz_id = request.GET.get('bk_biz_id')
        template_source = request.GET.get('template_source', 'business')  # 流程模板来源
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        if not bk_biz_id:
            resp['result'] = False
            resp['code'] = -1
            resp['message'] = u'缺少参数'
            return JsonResponse(resp)
        client = get_client_by_request(request)
        kwargs = {
            'bk_biz_id': bk_biz_id,
            'template_source': template_source,
        }
        res = client.sops.get_template_list(kwargs)
        if res['code'] == 0 and res['result']:
            bk_templates = []
            for item in res['data']:
                dic = {
                    'category': item['category'],  # 类型
                    'bk_biz_id': item['bk_biz_id'],  # 业务id
                    'bk_biz_name': item['bk_biz_name'],  # 业务名
                    'name': item['name'],  # 模板名
                    'creator': item['creator'],  # 创建者
                    'editor': item['editor'],  # 编辑者
                    'create_time': item['create_time'],  # 创建时间
                    'edit_time': item['edit_time'],  # 编辑时间
                    'id': item['id'],  # 模板id
                }
                bk_templates.append(dic)
            resp['data'] = bk_templates
        else:
            resp['result'] = False
            resp['code'] = -1
            resp['message'] = u'无权限操作'
        return JsonResponse(resp)
```

# 查询模板详情

```python
# 查询模板详情
def get_template_info_views(request):
    if request.method == 'GET':
        bk_biz_id = request.GET.get('bk_biz_id')
        template_id = request.GET.get('template_id')
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        if not all([bk_biz_id, template_id]):
            resp['result'] = False
            resp['code'] = -1
            resp['message'] = u'缺少参数'
            return JsonResponse(resp)
        client = get_client_by_request(request)
        kwargs = {
            'bk_biz_id': bk_biz_id,
            'template_id': template_id,
        }
        res = client.sops.get_template_info(kwargs)
        if res['result'] and res['code'] == 0:
            item = res['data']
            dic = {
                'category': item['category'],
                'edit_time': item['edit_time'],
                'create_time': item['create_time'],
                'name': item['name'],  # 模板名
                'bk_biz_id': item['bk_biz_id'],
                'creator': item['creator'],
                'bk_biz_name': item['bk_biz_name'],
                'template_id': item['id'],
                'editor': item['editor'],
            }
            resp['data'] = dic
        else:
            resp['result'] = False
            resp['code'] = -1
            resp['message'] = u'无权限操作'
        return JsonResponse(resp)
```

# choose的参数转换

```python
'state_desc': item.get_state_display(),  # TODO 学习这种用法
```

# 周期任务

```python
@periodic_task(run_every=crontab(minute='*/30', hour='*', day_of_week="*", day_of_month='*', month_of_year='*'))
```

# python时间格式化

```python
'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
```

# base64编码

```python
base64.b64encode(script.encode()).decode()
```

# 处理中文显示

```python
return JsonResponse(resp, json_dumps_params={'ensure_ascii': False})
```

# 将数组转为，分割字符串

```python
 ips = ','.join([item['ip'] for item in ip_list])
```

# 查询集群

```python

class SearchSet(View):

    def get(self, request):
        """
        根据业务id获取集群
        :param request:
        :return:
        """
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        bk_biz_id = request.GET.get('bk_biz_id')
        if not bk_biz_id:
            resp['result'] = False
            resp['message'] = u'缺少参数'
            return JsonResponse(resp, json_dumps_params={'ensure_ascii': False})
        client = get_client_by_request(request)
        kwargs = {
            "bk_biz_id": bk_biz_id,
        }
        res = client.cc.search_set(kwargs)
        if res.get('result', False):
            resp['data'] = res['data']['info']
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 查询模块

```python

class SearchModule(View):

    def get(self, request):
        """
        根据业务id和集群id获取模块
        :param request:
        :return:
        """
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        bk_biz_id = request.GET.get('bk_biz_id')
        bk_set_id = request.GET.get('bk_set_id')
        if not all([bk_biz_id, bk_set_id]):
            resp['result'] = False
            resp['message'] = u'缺少参数'
            return JsonResponse(resp, json_dumps_params={'ensure_ascii': False})
        client = get_client_by_request(request)
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "bk_set_id": bk_set_id
        }
        res = client.cc.search_module(kwargs)
        if res.get('result', False):
            resp['data'] = res['data']['info']
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 执行脚本

```python
class FastExecuteScript(View):
    """
    执行脚本
    """

    def post(self, request):
        # 脚本id
        id = 1357
        data = json.loads(request.body.decode())
        client = get_client_by_request(request)
        bk_biz_id = data.get('bk_biz_id')
        bk_biz_name = data.get('bk_biz_name')
        execute_way = data.get('execute_way')
        params = data.get('params')
        ip_list = data.get('ip_list')
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        script_param = execute_way + ' ' + params
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "script_id": id,
            "script_param": base64.b64encode(script_param.encode()).decode(),
            "script_timeout": 1000,
            "account": "root",
            "script_type": 1,
            "ip_list": ip_list,
        }
        res = client.job.fast_execute_script(kwargs)
        ips = ','.join([item['ip'] for item in ip_list])
        if res.get('result', False):
            job_instance_id = res['data']['job_instance_id']
            HistoryInfo.objects.create(
                bk_biz_name=bk_biz_name,
                bk_biz_id=bk_biz_id,
                script_param=script_param,
                job_instance_id=job_instance_id,
                ip_list=ips
            )
            save_execute_script_logs.delay(client, bk_biz_id, job_instance_id)
            resp['data'] = res['data']
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 创建流程任务-标准运维

```python
class CreateTask(View):
    def post(self, request):
        """
        通过流程模板创建任务
        :param request:
        :return:
        """
        template_id = 25
        template_name = 'luoxi_task_test'
        client = get_client_by_request(request)
        data = json.loads(request.body.decode())
        bk_biz_id = data.get('bk_biz_id')
        job_ip_list = data.get('job_ip_list')
        push_ip_list = data.get('push_ip_list')
        bk_biz_name = data.get('bk_biz_name')
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "name": template_name,
            "template_id": template_id,
            "constants": {
                "${job_ip_list}": job_ip_list,
                "${push_ip_list}": push_ip_list,
                "${job_script_param}": request.user.username,
                "${job_source_files}": [
                    {
                        "ip": job_ip_list,
                        "files": "/tem/test-" + request.user.username + '.txt',
                        "account": "root"
                    }
                ]
            }
        }
        res = client.sops.create_task(kwargs)
        if res.get('result', False):
            task_url = res['data']['task_url']
            # task_id = res['data']['task_id']
            task_id = 1441
            resp['data'] = {
                'task_id': task_id,
                'task_url': task_url
            }
            try:
                history = HistoryInfo.objects.create(
                    bk_biz_name=bk_biz_name,
                    bk_biz_id=bk_biz_id,
                    task_url=task_url,
                    task_name=template_name,
                    template_id=template_id,
                    task_id=task_id,
                )
            except Exception as err:
                print(err)
                resp['result'] = False
                resp['message'] = 'false'
            else:
                history.save()
        else:
            resp['result'] = False
            resp['message'] = 'false'
        return JsonResponse(resp)
```

# 执行任务

```python
class StartTask(View):

    def get(self, request):
        """
        开始执行任务
        :param request:
        :return:
        """
        client = get_client_by_request(request)
        bk_biz_id = request.GET.get('bk_biz_id')
        # task_id = request.GET.get('task_id')
        task_id = 1441
        resp = {
            'result': True,
            'code': 0,
            'message': 'success',
            'data': [],
            'request_id': str(uuid.uuid4()).replace('-', '')
        }
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "task_id": task_id
        }
        res = client.sops.start_task(kwargs)
        if res.get('result', False):
            resp['data'] = res['data']
        else:
            resp['result'] = False
            resp['message'] = 'false'
        get_task_status.delay(client, bk_biz_id, task_id)
        get_task_detail.delay(client, bk_biz_id, task_id)
        return JsonResponse(resp)

```

