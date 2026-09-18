/* ============================================================
   ECharts 按需构建入口 —— 用于重建 public/javascripts/echarts.min.js
   ------------------------------------------------------------
   为什么不用官方全量包：全量 1006KB，而本站只用到 graph 与 sunburst 两种图，
   按需打包后 526KB（gzip 327KB → 179KB），少一半。

   重建命令（一次性，产物入库；仓库本身仍然零构建、零依赖）：

     mkdir -p /tmp/echarts-build && cd /tmp/echarts-build
     npm init -y && npm i --no-audit --no-fund echarts@5.6.0 esbuild
     node node_modules/esbuild/install.js          # 若 esbuild 二进制没装上
     cp <本文件> /tmp/echarts-build/entry.js
     node_modules/esbuild/bin/esbuild entry.js \
       --bundle --minify --format=iife --target=es2017 \
       --outfile=echarts.custom.min.js
     # 再把 Apache 许可头拼到文件开头，覆盖 public/javascripts/echarts.min.js

   ⚠️ 换版本或加图型时必须同步改两处：本文件与 NOTICE 的「第三方组件」段。
   ⚠️ 页面依赖 window.echarts 全局（见文件末尾），不要改成 ESM 导出。
   ============================================================ */
import * as echarts from 'echarts/core'
import { GraphChart, SunburstChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { LabelLayout } from 'echarts/features'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([GraphChart, SunburstChart, TooltipComponent, LegendComponent, LabelLayout, CanvasRenderer])

window.echarts = echarts
