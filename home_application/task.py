import time
from celery import task
from celery.schedules import crontab
from .models import JobHistory
from django.utils import timezone
import json
import requests
import re
def find_num(find_str):
    """
    查询字符串中的数字
    """
    return re.findall(r"\b\d+\b", find_str)


@task(ignore_result=True)
def get_job_status(client, bk_biz_id, job_instance_id):
    kw = {
        "bk_biz_id": bk_biz_id,
        "job_instance_id": job_instance_id
    }
    num = 1
    sqls = JobHistory.objects.filter(job_instance_id=job_instance_id)
    while True:
        if num >= 10:
            break
        res = client.job.get_job_instance_status(kw)
        if not res["result"]:
            time.sleep(3)
            num += 1
            continue
        
        if res["data"]["job_instance"]["status"] == 3:
            # 执行成功
            res = client.job.get_job_instance_log(kw)
            sqls.update(job_status=3)
            sqls.update(bk_job_log=json.dumps(res))
            sqls.update(end_time=timezone.now())
            break
        if not res["data"]["job_instance"]["status"] in (1, 2):
            # 执行失败
            sqls.update(job_status=2)
            sqls.update(end_time=timezone.now())
            break
        time.sleep(3)
        num += 1


# @task.periodic_task(run_every=crontab(minute="*/5"))
# def periodic_task():
#     res = requests.get("http://paas.guodong.com/t/saas-demo-fcy/random_data")

#     content = res.content
#     if content is None:
#         return

#     json_data = json.loads(content.decode())

#     chart.objects.create(
#         cpu=json_data["cpu"],
#         mem=json_data["mem"],
#         disk=json_data["disk"]
#     )
