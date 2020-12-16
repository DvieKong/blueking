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

from django.conf.urls import url

from . import views

urlpatterns = (
    url(r"^$", views.home),
    url(r"^exec_script$", views.dev_guide),
    url(r"^script_job$", views.contact),
    url(r'^api/search_business/$', views.search_business),
    url(r'^api/search_host/$', views.search_host),
    url(r'^api/get_script_list/$', views.get_script_list),
    url(r'^api/sync_local_db/$', views.sync_local_db),
    url(r'^api/fast_execute_script/$', views.fast_execute_script),
    url(r'^api/get_local_list/$', views.get_local_list),
    url(r'^api/get_add/$', views.get_add),
    url(r'^api/remove_list/$', views.remove_list),
    url(r'^api/update_list/$', views.update_list),
    url(r'^api/get_history/$', views.get_history),

)
