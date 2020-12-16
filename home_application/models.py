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

from django.db import models

# Create your models here.
class ScriptList(models.Model):
    script_id = models.IntegerField(verbose_name="脚本id")
    public = models.IntegerField(verbose_name="来源")
    script_type = models.IntegerField(verbose_name="类型")
    name = models.TextField(verbose_name="名字")
    content = models.TextField(verbose_name="内容", null=True)
    create_time = models.DateTimeField(verbose_name="完成时间")
    bk_biz_id = models.IntegerField(verbose_name="业务id", null=True)

class JobHistory(models.Model):
    bk_biz_id = models.IntegerField(verbose_name="业务ID")
    bk_biz_name = models.CharField(max_length=50, verbose_name="业务名称")
    job_instance_id = models.IntegerField(verbose_name="作业ID")
    job_instance_name = models.TextField(verbose_name="作业名称")
    ip_list = models.CharField(max_length=1000, verbose_name="主机列表")
    script_id = models.IntegerField(verbose_name="脚本")
    script_name = models.CharField(max_length=50, verbose_name="脚本名称")
    job_status = models.IntegerField(verbose_name="作业状态")
    execute_time = models.DateTimeField(verbose_name="执行时间")
    end_time = models.DateTimeField(verbose_name="完成时间")
    bk_job_log = models.TextField(verbose_name="日志", null=True)
