from pathlib import Path

OUT = Path(__file__).parent
STYLE = """
text{font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;fill:#18334a}
.title{font-size:25px;font-weight:700}.label{font-size:18px;font-weight:700}.body{font-size:16px}.small{font-size:14px;fill:#52697a}.tiny{font-size:12px;fill:#52697a}
.box{stroke:#91a6b1;stroke-width:2;rx:15}.safe{fill:#e1f1ef;stroke:#167e83}.cloud{fill:#dcebf2;stroke:#477c9b}.warn{fill:#f6e7cc;stroke:#c18a3a}.bad{fill:#f6dddd;stroke:#b76464}.neutral{fill:#fff;stroke:#91a6b1}.line{stroke:#688091;stroke-width:3;fill:none}.dash{stroke-dasharray:8 7}
"""


def svg(name, body, height=560):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}">
<defs>
<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3z" fill="#688091"/></marker>
<marker id="teal" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3z" fill="#167e83"/></marker>
<marker id="red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3z" fill="#b76464"/></marker>
</defs><style>{STYLE}</style><rect width="1100" height="{height}" rx="20" fill="white"/>{body}</svg>'''
    (OUT / name).write_text(content, encoding="utf-8")


svg("estimate-to-bill.svg", '''
<text x="38" y="42" class="title">从 workload 结构推导费用，再用账单记录校正假设</text>
<rect x="38" y="105" width="230" height="205" class="box neutral"/>
<text x="61" y="145" class="label">1 · 架构与用量</text><text x="61" y="185" class="body">SKU · 区域 · 时长</text><text x="61" y="216" class="body">GiB · 请求 · 流量</text><text x="61" y="263" class="small">盘点依赖资源与保留</text>
<rect x="313" y="105" width="230" height="205" class="box cloud"/>
<text x="336" y="145" class="label">2 · Meter 与价格</text><text x="336" y="185" class="body">计费单位 × 单价</text><text x="336" y="216" class="body">价格日期 · 币种</text><text x="336" y="263" class="small">零售价 ≠ 合同价</text>
<rect x="588" y="105" width="230" height="205" class="box warn"/>
<text x="611" y="145" class="label">3 · 预测/实际用量</text><text x="611" y="185" class="body">数量 × 费率</text><text x="611" y="216" class="body">依赖费用求和</text><text x="611" y="263" class="small">估算不是账单事实</text>
<rect x="863" y="105" width="200" height="205" class="box safe"/>
<text x="886" y="145" class="label">4 · 对账</text><text x="886" y="185" class="body">Cost Management</text><text x="886" y="216" class="body">Export / 发票</text><text x="886" y="263" class="small">同一 scope 与期间</text>
<path d="M269 207H302" class="line" marker-end="url(#arrow)"/><path d="M544 207H577" class="line" marker-end="url(#arrow)"/><path d="M819 207H852" class="line" marker-end="url(#arrow)"/>
<rect x="127" y="378" width="846" height="99" class="box neutral"/>
<text x="160" y="419" class="label">随估价保存可复核输入</text><text x="160" y="453" class="body">resource list · unit · quantity · rate source/date · discounts · forecast window · currency · owner</text>
<text x="127" y="525" class="small">遗漏网关、磁盘、备份、日志保留或出口流量，会让 workload 总额偏离单项计算。</text>
''')

svg("cost-views-and-budgets.svg", '''
<text x="38" y="42" class="title">Actual 与 amortized 看同一承诺的两种时间表达</text>
<rect x="48" y="92" width="565" height="370" class="box neutral"/>
<text x="76" y="132" class="label">承诺购买：总费用 USD 300，期限三个月（演示值）</text>
<text x="77" y="188" class="body">Actual cost</text><rect x="245" y="157" width="295" height="53" rx="8" fill="#b76464"/><text x="266" y="191" class="label" fill="white">第 1 月记录 USD 300</text>
<text x="77" y="266" class="body">Amortized</text><rect x="245" y="233" width="95" height="53" rx="8" fill="#167e83"/><rect x="350" y="233" width="95" height="53" rx="8" fill="#167e83"/><rect x="455" y="233" width="95" height="53" rx="8" fill="#167e83"/><text x="263" y="267" class="small" fill="white">USD 100</text><text x="368" y="267" class="small" fill="white">USD 100</text><text x="473" y="267" class="small" fill="white">USD 100</text>
<text x="79" y="339" class="small">Actual：对账采购发生在哪天</text><text x="79" y="370" class="small">Amortized：观察承诺期间的资源归属</text>
<rect x="79" y="398" width="500" height="43" rx="9" class="box warn"/><text x="99" y="426" class="body">两者不可相加：是同一项 USD 300 承诺</text>
<rect x="655" y="92" width="400" height="370" class="box cloud"/>
<text x="684" y="132" class="label">预算是告警阈值</text><text x="684" y="178" class="body">阈值：USD 100</text>
<rect x="684" y="203" width="330" height="34" rx="8" fill="#d9e2e7"/><rect x="684" y="203" width="270" height="34" rx="8" fill="#c18a3a"/>
<text x="684" y="277" class="body">实际成本：USD 82</text><text x="684" y="311" class="body">预测成本：USD 125</text>
<path d="M742 346V390" class="line" marker-end="url(#red)"/><rect x="729" y="390" width="243" height="48" rx="9" class="box bad"/><text x="755" y="421" class="label">通知 owner</text>
<text x="684" y="487" class="small">阈值不会自动停止资源消费</text>
''')

svg("cost-allocation.svg", '''
<text x="38" y="42" class="title">直接归属、共享分摊与未知费用都要留在账本里</text>
<rect x="45" y="107" width="292" height="287" class="box cloud"/>
<text x="72" y="149" class="label">Azure usage records</text>
<rect x="72" y="181" width="238" height="72" rx="10" class="box neutral"/><text x="95" y="211" class="body">resource + meter + amount</text><text x="95" y="237" class="small">direct / inherited tags</text>
<rect x="72" y="276" width="238" height="75" rx="10" class="box warn"/><text x="95" y="306" class="body">shared service pool</text><text x="95" y="334" class="small">explicit period + driver</text>
<rect x="408" y="93" width="305" height="126" class="box safe"/><text x="435" y="137" class="label">Payments cost center</text><text x="435" y="175" class="body">direct charge + shared 70%</text>
<rect x="408" y="258" width="305" height="126" class="box safe"/><text x="435" y="302" class="label">Analytics cost center</text><text x="435" y="340" class="body">direct charge + shared 30%</text>
<rect x="783" y="162" width="270" height="150" class="box bad"/><text x="810" y="205" class="label">Unallocated queue</text><text x="810" y="242" class="body">missing owner / driver</text><text x="810" y="277" class="small">留待调查，不要丢弃</text>
<path d="M338 218H390V157H399" class="line" marker-end="url(#teal)"/><path d="M338 218H379V321H399" class="line" marker-end="url(#teal)"/>
<path d="M338 313H390V157H399" class="line dash" marker-end="url(#arrow)"/><path d="M338 313H399" class="line dash" marker-end="url(#arrow)"/>
<path d="M337 181H772V235" class="line dash" marker-end="url(#red)"/><path d="M337 315H772" class="line dash" marker-end="url(#red)"/>
<text x="435" y="448" class="small">记录分母、权重、来源和规则版本；分配额应与 shared pool 对平。</text>
<text x="73" y="497" class="tiny">Tag inheritance 影响成本记录；不能据此推断 Azure resource 本身已继承或被治理。</text>
''')

svg("idle-retained-costs.svg", '''
<text x="38" y="42" class="title">计算停止后仍要查依赖资源与保留策略</text>
<rect x="45" y="111" width="305" height="315" class="box warn"/>
<text x="72" y="153" class="label">VM：Stopped</text><text x="72" y="196" class="body">仍分配 host 资源</text><text x="72" y="232" class="body">compute 可能继续计费</text>
<path d="M100 270H293" class="line dash" marker-end="url(#arrow)"/><text x="72" y="317" class="small">确认业务是否可以</text><text x="72" y="343" class="small">由 owner 授权 deallocate</text><text x="72" y="390" class="small">不能用 guest OS shutdown</text><text x="72" y="413" class="small">代替云端 deallocation</text>
<rect x="398" y="111" width="305" height="315" class="box cloud"/>
<text x="425" y="153" class="label">VM：Deallocated</text><text x="425" y="196" class="body">compute 释放</text><text x="425" y="232" class="body">磁盘/网络可能仍计费</text>
<rect x="430" y="270" width="238" height="90" rx="12" class="box neutral"/><text x="450" y="307" class="body">disk · snapshot</text><text x="450" y="339" class="body">backup · public IP</text>
<text x="425" y="401" class="small">逐项确认 owner 与 retention</text>
<rect x="751" y="111" width="305" height="315" class="box bad"/>
<text x="778" y="153" class="label">VM：Deleted</text><text x="778" y="196" class="body">资源可能被 Detach</text><text x="778" y="232" class="body">backup 仍按策略保留</text>
<path d="M790 279H1017" class="line" marker-end="url(#arrow)"/><rect x="782" y="308" width="242" height="76" rx="12" class="box neutral"/><text x="807" y="340" class="body">残留资源清单</text><text x="807" y="367" class="small">经批准后再回收</text>
<path d="M351 269H388" class="line" marker-end="url(#arrow)"/><path d="M704 269H741" class="line" marker-end="url(#arrow)"/>
<text x="80" y="490" class="small">Resource delete 选项、保留义务和 recovery policy 会共同决定清理结果。</text>
''')

svg("verified-cost-recovery.svg", '''
<text x="38" y="42" class="title">成本回收需要批准、依赖核查、残留审计和账单复核</text>
<rect x="52" y="106" width="288" height="133" class="box cloud"/>
<text x="78" y="148" class="label">1 · 找到成本来源</text><text x="78" y="184" class="body">scope · meter · resource</text><text x="78" y="215" class="small">等待数据刷新再对账</text>
<rect x="407" y="106" width="288" height="133" class="box warn"/>
<text x="433" y="148" class="label">2 · Owner / retention gate</text><text x="433" y="184" class="body">依赖 · 备份 · 到期日</text><text x="433" y="215" class="small">没有批准则停止</text>
<rect x="762" y="106" width="288" height="133" class="box safe"/>
<text x="788" y="148" class="label">3 · 最小获批动作</text><text x="788" y="184" class="body">resize · deallocate · delete</text><text x="788" y="215" class="small">记录前后状态与时间</text>
<path d="M341 172H396" class="line" marker-end="url(#arrow)"/><path d="M696 172H751" class="line" marker-end="url(#teal)"/>
<rect x="762" y="321" width="288" height="133" class="box neutral"/>
<text x="788" y="363" class="label">4 · 检查残留资源</text><text x="788" y="399" class="body">disk · IP · backup</text><text x="788" y="430" class="small">每项标明 owner/retention</text>
<rect x="407" y="321" width="288" height="133" class="box cloud"/>
<text x="433" y="363" class="label">5 · 等待成本更新</text><text x="433" y="399" class="body">同 scope / meter / period</text><text x="433" y="430" class="small">必要时等账期收敛</text>
<rect x="52" y="321" width="288" height="133" class="box bad"/>
<text x="78" y="363" class="label">6 · 记录回收结论</text><text x="78" y="399" class="body">节省 / 保留 / 未核实</text><text x="78" y="430" class="small">不把删除等同于省钱</text>
<path d="M906 240V281H906V311" class="line" marker-end="url(#arrow)"/><path d="M761 387H705" class="line" marker-end="url(#arrow)"/><path d="M406 387H349" class="line" marker-end="url(#arrow)"/>
<path d="M52 387H22V173H43" class="line dash" marker-end="url(#red)"/><text x="74" y="510" class="small">若数据未下降或出现新 meter，保留差异并重开调查，不要自动删除更多资源。</text>
''')
