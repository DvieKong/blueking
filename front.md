# 引入axios等

```python
<script src="https://cdn.bootcdn.net/ajax/libs/moment.js/2.29.1/moment.min.js"></script>
<script src="https://cdn.bootcdn.net/ajax/libs/moment.js/2.29.1/locale/zh-cn.min.js"></script>
<!-- axios -->
<script src="https://unpkg.com/axios/dist/axios.min.js"></script>
<!-- 这个是全局配置，如果需要在js中使用app_code和site_url,则这个javascript片段一定要保留 -->
<script type="text/javascript">
    var app_code = "{{ APP_CODE }}";         // 在蓝鲸系统里面注册的"应用编码"
    var site_url = "{{ SITE_URL }}";         // app的url前缀,在ajax调用的时候，应该加上该前缀
    var remote_static_url = "{{ REMOTE_STATIC_URL }}";   //远程资源链接，403页面需要，不要删除
    var debug_mode = JSON.parse("{{ DEBUG }}");    // 是否调试模式
    var csrftoken = "{{ csrf_token }}";
    axios.defaults.headers.common['X-CSRFToken'] = csrftoken;
    axios.defaults.headers.common['Content-Type'] = 'application/json;charset=utf-8';
    axios.interceptors.response.use(res => {
        return res.data
    })
</script>

引入moment和echarts
<script src="https://cdn.bootcdn.net/ajax/libs/moment.js/2.29.1/moment.min.js"></script>
<script src="https://cdn.bootcdn.net/ajax/libs/moment.js/2.29.1/locale/zh-cn.min.js"></script>
<script src="https://magicbox.bk.tencent.com/static_api/v3/assets/echarts-2.0/echarts-all.js"></script>

```

# 下拉框

```html
<bk-form form-type="inline">
    <bk-form-item label="选择业务">
        <bk-select v-model="selected_biz" style="width:200px" @change="select_biz">
            <bk-option v-for="biz in biz_list" :key="biz.bk_biz_id"
                       :id="biz.bk_biz_id"
                       :name="biz.bk_biz_name">
            </bk-option>
        </bk-select>
    </bk-form-item>
</bk-form>

select_biz(newValue, oldValue) {
    if (oldValue == '') return;
    this.selected_biz = newValue;
    this.search_host(newValue);
},
```

# table表单

```html
{% verbatim %}
<bk-table style="margin-top:15px;" :data="host_list" @selection-change="select_data">
    <bk-table-column type="selection" width="60"></bk-table-column>
    <bk-table-column prop="bk_host_id" label="id"></bk-table-column>
    <bk-table-column prop="bk_host_name" label="主机名"></bk-table-column>
    <bk-table-column prop="bk_host_innerip" label="内网IP"></bk-table-column>
    <bk-table-column label="在线状态">
    <template slot-scope="scope">
   		 {{ scope.row.bk_agent_alive == true ? '是' : '否'}}
    </template>
    </bk-table-column>
    <bk-table-column label="配置">
    	<template slot-scope="scope" v-if="scope.row.bk_cpu">
            <span>{{ scope.row.bk_cpu }}核</span>
            <span>{{ (scope.row.bk_mem/1024).toFixed(2) }}G,</span>
            <span>{{ (scope.row.bk_disk/1024).toFixed(2) }}G</span>
            </template>
    	</bk-table-column>
    <bk-table-column prop="bk_os_name" label="系统">
    	<template slot-scope="scope" v-if="scope.row.bk_cpu">
    		<span>{{ scope.row.bk_os_name }} {{ scope.row.bk_os_version }}</span>
    	</template>
    </bk-table-column>
    <bk-table-column label="操作" width="150">
    	<template slot-scope="props">
            <bk-button class="mr10" theme="primary" text @click="update_agent(props.row)">更新
             </bk-button>
    	</template>
    </bk-table-column>
</bk-table>
{% endverbatim %}


select_data(data) {
this.selected_host = data.map(value => {
    return {
        "bk_cloud_id": 0,
        "ip": value.bk_host_innerip
        }
    });
},
```

# 树

```html
<bk-tree
        ref="tree1"
        :data="treeListOne"
        :node-key="'id'"
        :has-border="true"
        @on-click="nodeClickOne"
        @on-expanded="nodeExpandedOne">
</bk-tree>

/* 树的点击事件 */
nodeClickOne(node) {
},
/* 树的展开事件 */
nodeExpandedOne(node, expanded) {
	if (expanded === true) {
		this.search_host(node)
    }
},
```

# 饼状图

```js
 <div id="charts" style="width: 100%; height: 500px;"></div>

createEPieChart(conf) {
    var myChart = echarts.init(document.getElementById(conf.selector));
    var aLegend = [];
    var series = conf.data.series;
    for (var i = 0; i < series.length; i++) {
        aLegend[i] = series[i].name;
    }
    // 填入数据
    myChart.setOption({
        title: {
            text: conf.data.title,
            subtext: '',
            x: 'center'
        },
        legend: {
            // x : 'left',
            y: 'bottom',
            data: aLegend
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        toolbox: {
            show: true,
            feature: {
                mark: {show: true},
                dataView: {show: true, readOnly: false},
                magicType: {
                    show: true,
                    type: ['pie', 'funnel'],
                    option: {
                        funnel: {
                            x: '25%',
                            width: '50%',
                            funnelAlign: 'left',
                            max: 1548
                        }
                    }
                },
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        calculable: true,
        series: [{
            // 根据名字对应到相应的系列
            name: '访问来源',
            type: 'pie',
            data: series
        }]
    });
},
initEPieChartData(conf) {
    let that = this;
    $.ajax({
        url: conf.url,
        type: 'GET',
        dataType: conf.dataType,
        success: function (res) {
            //获取数据成功
            if (res.result) {
                var data = res.data;
                that.createEPieChart({
                    selector: conf.containerId, // 图表容器
                    data: data, // 图表数据
                });
            }
        }
    });
},
initEPieChart() {
    let that = this;
    $(function () {
        that.initEPieChartData({
            url: 'https://magicbox.bk.tencent.com/static_api/v3/components/chart4/demo.json',
            dataType: 'json',
            containerId: 'charts'
        });
    });
}
```

# 时间格式化

```js
start_time: moment(this.date_time_range[0]).format("yyyy-MM-DD HH:mm:ss"),
end_time: moment(this.date_time_range[1]).format("yyyy-MM-DD HH:mm:ss"),
```

# 弹出框

```js
<bk-dialog v-model="task_detail_visible" title="任务详情"
:header-position="dialog_position"
:width="template_width">
    <bk-table style="margin-top: 15px;"
    :data="task_detail_data"
    :size="size">
        <bk-table-column label="模板ID" prop="template_id" width="80"></bk-table-column>
        <bk-table-column label="类型" prop="category" width="100"></bk-table-column>
        <bk-table-column label="名称" prop="name"></bk-table-column>
        <bk-table-column label="创建者" prop="creator" width="100"></bk-table-column>
        <bk-table-column label="创建时间" prop="create_time" width="200"></bk-table-column>
        <bk-table-column label="编辑时间" prop="edit_time" width="200"></bk-table-column>
    </bk-table>
</bk-dialog>

data:
    task_detail_visible: false,
    dialog_position: 'left',
    template_width: '1000',
```

# 加载中

```js
  showLoading() {
      const h = this.$createElement
      this.$bkLoading({
          title: h('span', {
              style: {
                  color: 'red'
              }
          }, '加载中')
      })
  },
      // 获取主机
      async get_host(bk_biz_id, bk_obj_id, bk_inst_id, bk_inst_name) {
          this.showLoading();
          const res = await axios({
              url: site_url + 'search_host/',
              methods: 'GET',
              params: {
                  bk_biz_id, bk_obj_id, bk_inst_id, bk_inst_name
              }
          });
          if (res.result) {
              this.formData.ipList = res.data.join(',');
              this.$bkLoading.hide()
          }
      },
```

# 信息提示

```js
// 弹窗错误提示
handleError (config){
    config.offsetY = 80;
    this.$bkMessage(config);
}
this.handleError({theme: 'error', delay: 3000, message: res.data.msg});
// 弹窗成功提示
handleSuccess (config) {
    config.offsetY = 80;
    this.$bkMessage(config)
}
this.handleSuccess({theme: 'success', delay: 1500, message: res.data.msg});
```

# 弹出确认之后再执行

```js
  async fast_execute_script() {
      let bk_biz_name = this.biz_list.find(value => {
          return value.bk_biz_id == this.selected_biz
      })['bk_biz_name'];
      let execute_way = this.execute_way.find(value => {
          return value.id = this.selected_execute_way;
      });
      this.$bkInfo({
          title: '确认要执行？',
          confirmLoading: true,
          confirmFn: async () => {
              try {
                  const res = await axios({
                      url: site_url + 'fast_execute_script/',
                      method: 'POST',
                      data: {
                          'bk_biz_id': this.selected_biz,
                          'ip_list': this.selected_host,
                          "bk_biz_name": bk_biz_name,
                          "execute_way": execute_way.name,
                          "params": this.params
                      }
                  });
                  if (res.result) {
                      console.log(res)
                      this.$bkMessage({
                          message: '执行成功',
                          theme: 'success'
                      });
                  }
                  return true
              } catch (e) {
                  console.log('err', e);
                  this.$bkMessage({
                      message: '服务器错误',
                      theme: 'error'
                  });
                  return true
              }
          }
      })
  },
```

