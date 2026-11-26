from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
STYLE = """
:root{--ink:#18334a;--muted:#52697a;--teal:#167e83;--blue:#dcebf2;--tealbg:#e1f1ef;--amber:#f6e7cc;--red:#f6dddd;--paper:#ffffff;--line:#688091;--pale:#f5f8fa}
text{font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;fill:var(--ink)}
.title{font-size:25px;font-weight:700}.label{font-size:20px;font-weight:700}.body{font-size:16px}.small{font-size:14px;fill:var(--muted)}.tiny{font-size:12px;fill:var(--muted)}
.box{stroke:#9aaeb9;stroke-width:2;rx:15}.line{stroke:var(--line);stroke-width:3;fill:none}.dash{stroke-dasharray:9 7}.safe{fill:var(--tealbg);stroke:var(--teal)}.cloud{fill:var(--blue);stroke:#477c9b}.warn{fill:var(--amber);stroke:#c18a3a}.bad{fill:var(--red);stroke:#b76464}.neutral{fill:var(--paper);stroke:#8fa2ad}
"""
def svg(name, body, height=520):
    content=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}">
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#688091"/></marker><marker id="tealArrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#167e83"/></marker><marker id="redArrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#b76464"/></marker></defs>
<style>{STYLE}</style><rect width="1100" height="{height}" rx="22" fill="#fff"/>{body}</svg>'''
    (OUT/name).write_text(content,encoding='utf-8')

svg('backend-boundaries.svg', '''
<text x="40" y="42" class="title">后端锁住的是一个 Blob 状态对象</text>
<rect x="38" y="70" width="485" height="405" rx="20" fill="#f5f8fa" stroke="#b3c2ca" stroke-width="2"/>
<text x="60" y="104" class="label">Terraform runner</text>
<rect x="66" y="128" width="425" height="125" class="box neutral"/>
<text x="90" y="163" class="label">Terraform Core + azurerm backend</text>
<text x="90" y="195" class="body">配置 / State / Plan / 后端协议</text>
<text x="90" y="225" class="small">backend 身份与 AzureRM resource provider 分开</text>
<rect x="67" y="300" width="195" height="105" class="box safe"/>
<text x="86" y="337" class="label">Entra 身份</text><text x="86" y="368" class="body">OIDC / CLI 等认证</text>
<rect x="294" y="300" width="197" height="105" class="box warn"/>
<text x="311" y="337" class="label">数据面权限</text><text x="311" y="368" class="body">容器范围 Blob 读写</text>
<path d="M260 351 H286" class="line" marker-end="url(#arrow)"/>
<path d="M485 254 V279 H165 V292" class="line" marker-end="url(#arrow)"/>
<text x="310" y="280" class="small">获取可访问 Blob 的 token</text>
<rect x="577" y="92" width="480" height="250" rx="20" fill="#eaf3f7" stroke="#477c9b" stroke-width="2"/>
<text x="604" y="130" class="label">Azure Storage · Blob data plane</text>
<rect x="622" y="163" width="388" height="137" class="box cloud"/>
<text x="651" y="201" class="label">container / state key</text>
<text x="651" y="235" class="body">state blob contents + Blob lease</text>
<text x="651" y="270" class="small">租约互斥该 key 的并发写入</text>
<path d="M523 187 H612" class="line" marker-end="url(#arrow)"/>
<text x="533" y="175" class="small">HTTPS data calls</text>
<path d="M612 242 H523" class="line dash" marker-end="url(#tealArrow)"/>
<text x="534" y="266" class="small">read / write / lease</text>
<rect x="577" y="380" width="480" height="95" class="box warn"/>
<text x="603" y="416" class="label">管理面控制是另一套授权</text>
<text x="603" y="448" class="body">Contributor 不自动授予 Entra Blob 数据读写权限</text>
<path d="M820 342 V370" class="line dash" marker-end="url(#arrow)"/>
<text x="836" y="365" class="tiny">仅需查 endpoint 时再考虑 ARM Reader</text>
''', 520)

svg('lease-concurrency.svg', '''
<text x="40" y="42" class="title">两次 Terraform 操作争用同一状态 key</text>
<text x="195" y="91" class="label">时间向右</text><path d="M180 105 H1040" class="line" marker-end="url(#arrow)"/>
<text x="40" y="175" class="label">Runner A</text><path d="M175 167 H1040" stroke="#cad5da" stroke-width="2"/>
<text x="40" y="290" class="label">Runner B</text><path d="M175 282 H1040" stroke="#cad5da" stroke-width="2"/>
<text x="40" y="410" class="label">Blob key</text><path d="M175 400 H1040" stroke="#cad5da" stroke-width="2"/>
<rect x="200" y="132" width="150" height="70" class="box safe"/><text x="218" y="160" class="label">申请租约</text><text x="218" y="186" class="small">获得 lock ID</text>
<rect x="385" y="132" width="370" height="70" class="box cloud"/><text x="415" y="160" class="label">读状态 → Refresh / Plan → 写状态</text><text x="415" y="186" class="small">操作期间持有同一 Blob 的 lease</text>
<rect x="790" y="132" width="150" height="70" class="box neutral"/><text x="820" y="174" class="label">释放租约</text>
<path d="M350 167 H378" class="line" marker-end="url(#arrow)"/><path d="M755 167 H782" class="line" marker-end="url(#arrow)"/>
<rect x="420" y="248" width="230" height="70" class="box bad"/><text x="447" y="277" class="label">同 key 申请失败</text><text x="447" y="303" class="small">或按 lock-timeout 等待</text>
<path d="M330 235 C360 250 382 272 411 282" class="line dash" marker-end="url(#redArrow)"/>
<rect x="790" y="248" width="150" height="70" class="box safe"/><text x="814" y="277" class="label">重新申请</text><text x="814" y="303" class="small">前一操作已结束</text>
<path d="M940 282 C990 247 990 205 943 184" class="line" marker-end="url(#tealArrow)"/>
<rect x="385" y="365" width="370" height="72" class="box cloud"/><text x="412" y="394" class="label">同一个 key 上的 lease</text><text x="412" y="420" class="small">互斥边界；不锁住其他 key，也不防双重资源管理</text>
<path d="M575 202 V357" class="line dash" marker-end="url(#arrow)"/><path d="M535 318 V357" class="line dash" marker-end="url(#arrow)"/>
<text x="197" y="486" class="small">锁拒绝必须来自实际 Terraform 竞争进程；图示解释协议，不是运行日志。</text>
''', 520)

svg('drift-reconciliation.svg', '''
<text x="40" y="42" class="title">漂移是配置、State 与可观测对象三方不一致</text>
<rect x="65" y="100" width="270" height="115" class="box safe"/><text x="91" y="140" class="label">HCL configuration</text><text x="91" y="178" class="body">期望：setting = blue</text>
<rect x="415" y="100" width="270" height="115" class="box neutral"/><text x="441" y="140" class="label">当前 Terraform State</text><text x="441" y="178" class="body">上次记录：setting = blue</text>
<rect x="765" y="100" width="270" height="115" class="box bad"/><text x="791" y="140" class="label">实际对象 / Provider 读取</text><text x="791" y="178" class="body">带外改动：setting = green</text>
<path d="M335 157 H405" class="line" marker-end="url(#arrow)"/><path d="M685 157 H755" class="line" marker-end="url(#arrow)"/>
<rect x="117" y="276" width="395" height="105" class="box cloud"/><text x="147" y="317" class="label">正常 plan</text><text x="147" y="349" class="body">读取对象 → 报告漂移 → 提议改回 blue</text>
<rect x="588" y="276" width="395" height="105" class="box warn"/><text x="618" y="317" class="label">plan -refresh-only</text><text x="618" y="349" class="body">只提议把 State 更新为 green，不改对象</text>
<path d="M820 215 V263" class="line" marker-end="url(#arrow)"/><path d="M200 215 C200 248 280 245 310 263" class="line" marker-end="url(#arrow)"/>
<rect x="100" y="430" width="420" height="65" class="box safe"/><text x="128" y="458" class="label">非预期漂移 → 审阅 normal apply 修正对象</text>
<rect x="580" y="430" width="420" height="65" class="box neutral"/><text x="608" y="458" class="label">有意变更 → 改 HCL，再计划收敛</text>
<path d="M312 381 V410 H310 V422" class="line" marker-end="url(#arrow)"/><path d="M785 381 V410 H790 V422" class="line" marker-end="url(#arrow)"/>
''', 530)

svg('bootstrap-isolation.svg', '''
<text x="40" y="42" class="title">先造后端，再迁移状态；每个 key 是隔离单元</text>
<rect x="60" y="102" width="215" height="130" class="box warn"/><text x="87" y="141" class="label">1 · bootstrap</text><text x="87" y="176" class="body">本地 / 单独状态</text><text x="87" y="205" class="small">创建 Storage + container</text>
<rect x="340" y="102" width="215" height="130" class="box neutral"/><text x="365" y="141" class="label">2 · 配后端</text><text x="365" y="176" class="body">backend azurerm</text><text x="365" y="205" class="small">密钥与参数分开传入</text>
<rect x="620" y="102" width="215" height="130" class="box cloud"/><text x="648" y="141" class="label">3 · init 迁移</text><text x="648" y="176" class="body">审阅来源 / 目标</text><text x="648" y="205" class="small">备份，再 migrate-state</text>
<path d="M275 167 H330" class="line" marker-end="url(#arrow)"/><path d="M555 167 H610" class="line" marker-end="url(#arrow)"/>
<rect x="880" y="102" width="175" height="130" class="box safe"/><text x="905" y="141" class="label">4 · 验证</text><text x="905" y="176" class="body">Plan / key / scope</text><text x="905" y="205" class="small">旧本地状态受保护</text>
<path d="M835 167 H870" class="line" marker-end="url(#arrow)"/>
<text x="62" y="293" class="label">container: tfstate</text>
<rect x="62" y="316" width="455" height="97" class="box cloud"/><text x="89" y="352" class="label">dev / platform.tfstate</text><text x="89" y="383" class="body">lock A · 独立读取/恢复范围</text>
<rect x="580" y="316" width="475" height="97" class="box safe"/><text x="607" y="352" class="label">prod / platform.tfstate</text><text x="607" y="383" class="body">lock B · 不共享同一 State 生命周期</text>
<text x="62" y="467" class="small">两把锁互不冲突；但若两个 key 同时管理同一个 Azure 对象，仍会发生双重管理。</text>
''', 520)

svg('state-recovery.svg', '''
<text x="40" y="42" class="title">恢复状态先停止写入，再证明要恢复哪一版</text>
<rect x="55" y="104" width="205" height="105" class="box bad"/><text x="80" y="144" class="label">冻结 writer</text><text x="80" y="178" class="body">停止 pipeline / CLI</text>
<rect x="315" y="104" width="205" height="105" class="box neutral"/><text x="340" y="144" class="label">保护副本</text><text x="340" y="178" class="body">state pull / Blob 版本</text>
<rect x="575" y="104" width="205" height="105" class="box warn"/><text x="600" y="144" class="label">核验身份</text><text x="600" y="178" class="body">key / lineage / serial</text>
<rect x="835" y="104" width="205" height="105" class="box cloud"/><text x="860" y="144" class="label">隔离恢复</text><text x="860" y="178" class="body">审阅备份，再恢复</text>
<path d="M260 157 H305" class="line" marker-end="url(#arrow)"/><path d="M520 157 H565" class="line" marker-end="url(#arrow)"/><path d="M780 157 H825" class="line" marker-end="url(#arrow)"/>
<path d="M935 210 V271 H700" class="line" marker-end="url(#arrow)"/>
<rect x="418" y="273" width="442" height="92" class="box safe"/><text x="454" y="312" class="label">恢复后先 plan 对账</text><text x="454" y="342" class="body">查绑定、差异、作用范围；必要时再修复对象</text>
<rect x="85" y="416" width="425" height="75" class="box warn"/><text x="112" y="447" class="label">Blob versioning：保存对象历史</text><text x="112" y="474" class="small">不会阻止 Storage account / container 被删除</text>
<rect x="590" y="416" width="425" height="75" class="box bad"/><text x="617" y="447" class="label">force-unlock / state push -force</text><text x="617" y="474" class="small">可能绕过并发与 State 身份保护，不能当作常规修复</text>
<path d="M645 365 V405" class="line dash" marker-end="url(#arrow)"/><path d="M490 209 C460 310 325 338 300 407" class="line dash" marker-end="url(#arrow)"/>
''', 520)

print(f'Wrote {len(list(OUT.glob("*.svg")))} editable mechanism figures to {OUT}')
