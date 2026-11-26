from pathlib import Path

OUT = Path(__file__).parent
STYLE = """
text{font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;fill:#18334a}
.title{font-size:25px;font-weight:700}.label{font-size:19px;font-weight:700}.body{font-size:16px}.small{font-size:14px;fill:#52697a}.tiny{font-size:12px;fill:#52697a}
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


svg('pipeline-execution.svg', '''
<text x="38" y="42" class="title">流水线是执行图：工作目录不会自动跨 job 保留</text>
<rect x="36" y="82" width="245" height="132" class="box safe"/><text x="61" y="119" class="label">Repository event</text><text x="61" y="151" class="body">commit / manual queue</text><text x="61" y="183" class="small">PR policy 是另一入口</text>
<rect x="321" y="82" width="300" height="132" class="box cloud"/><text x="346" y="119" class="label">Compile / expand</text><text x="346" y="151" class="body">YAML + templates + parameters</text><text x="346" y="183" class="small">先构造计划执行结构</text>
<rect x="665" y="82" width="399" height="132" class="box neutral"/><text x="690" y="119" class="label">Evaluate conditions</text><text x="690" y="151" class="body">branch / reason / dependencies</text><text x="690" y="183" class="small">条件控制流程，不代替资源授权</text>
<path d="M283 148H313" class="line" marker-end="url(#arrow)"/><path d="M623 148H657" class="line" marker-end="url(#arrow)"/>
<rect x="88" y="292" width="258" height="137" class="box safe"/><text x="112" y="332" class="label">Stage · Validate</text><text x="112" y="365" class="body">Job → Agent → Steps</text><text x="112" y="398" class="small">本 job 的 checkout / tests</text>
<rect x="420" y="292" width="258" height="137" class="box warn"/><text x="444" y="332" class="label">Stage · Plan</text><text x="444" y="365" class="body">另一个 job / runner</text><text x="444" y="398" class="small">显式下载已发布的 artifact</text>
<rect x="752" y="292" width="258" height="137" class="box cloud"/><text x="776" y="332" class="label">Stage · Apply</text><text x="776" y="365" class="body">deployment job / Environment</text><text x="776" y="398" class="small">资源 checks 成功后才进入</text>
<path d="M347 360H411" class="line" marker-end="url(#arrow)"/><path d="M679 360H743" class="line" marker-end="url(#arrow)"/>
<rect x="421" y="464" width="257" height="54" class="box neutral"/><text x="457" y="497" class="body">Pipeline Artifact：显式跨 job 边界</text><path d="M549 430V456" class="line dash" marker-end="url(#teal)"/>
<text x="40" y="545" class="small">Microsoft-hosted job VM 会回收；self-hosted 工作区须由管理员定义和清理。</text>
''')

svg('repository-and-resource-gates.svg', '''
<text x="38" y="42" class="title">代码事件和资源所有者分别把住两道门</text>
<rect x="42" y="104" width="290" height="133" class="box safe"/><text x="68" y="142" class="label">Azure Repos</text><text x="68" y="176" class="body">push → YAML trigger</text><text x="68" y="207" class="small">PR → target branch policy</text>
<rect x="402" y="104" width="290" height="133" class="box neutral"/><text x="428" y="142" class="label">Pipeline YAML</text><text x="428" y="176" class="body">stages / jobs / conditions</text><text x="428" y="207" class="small">checkout 只请求代码资源</text>
<rect x="762" y="104" width="290" height="133" class="box warn"/><text x="788" y="142" class="label">Protected resource</text><text x="788" y="176" class="body">Environment / connection / pool</text><text x="788" y="207" class="small">owner 配权限和 checks</text>
<path d="M335 170H393" class="line" marker-end="url(#arrow)"/><path d="M695 170H753" class="line" marker-end="url(#arrow)"/>
<rect x="156" y="324" width="314" height="127" class="box cloud"/><text x="184" y="364" class="label">Stage 暂停在门前</text><text x="184" y="397" class="body">等待所有资源 checks</text><text x="184" y="428" class="small">拒绝或 timeout → 不执行</text>
<rect x="630" y="324" width="314" height="127" class="box safe"/><text x="658" y="364" class="label">获准后消费资源</text><text x="658" y="397" class="body">agent 运行 deployment job</text><text x="658" y="428" class="small">只拿该环境所需权限</text>
<path d="M907 239V278H314V315" class="line dash" marker-end="url(#arrow)"/><path d="M471 388H621" class="line" marker-end="url(#teal)"/>
<rect x="324" y="488" width="452" height="48" class="box bad"/><text x="354" y="519" class="body">YAML condition 是流程逻辑，不替代服务端检查</text>
''')

svg('wif-trust-chain.svg', '''
<text x="38" y="42" class="title">WIF：信任 token 来源，再单独检查资源权限</text>
<rect x="36" y="111" width="218" height="160" class="box neutral"/><text x="57" y="151" class="label">Azure Pipeline</text><text x="57" y="185" class="body">agent job + task</text><text x="57" y="217" class="small">短时请求 OIDC token</text><text x="57" y="243" class="tiny">AccessToken / OidcRequestUri</text>
<rect x="303" y="111" width="218" height="160" class="box warn"/><text x="324" y="151" class="label">Service Connection</text><text x="324" y="185" class="body">固定 endpoint identity</text><text x="324" y="217" class="small">pipeline permission</text><text x="324" y="243" class="tiny">issuer / subject / audience</text>
<rect x="570" y="111" width="218" height="160" class="box cloud"/><text x="591" y="151" class="label">Microsoft Entra</text><text x="591" y="185" class="body">匹配 federated credential</text><text x="591" y="217" class="small">交换 Azure access token</text><text x="591" y="243" class="tiny">不发长期 client secret</text>
<rect x="837" y="111" width="218" height="160" class="box safe"/><text x="858" y="151" class="label">Azure target</text><text x="858" y="185" class="body">RBAC / data-plane role</text><text x="858" y="217" class="small">检查 action 与 scope</text><text x="858" y="243" class="tiny">认证 ≠ 授权</text>
<path d="M257 190H294" class="line" marker-end="url(#arrow)"/><path d="M524 190H561" class="line" marker-end="url(#arrow)"/><path d="M791 190H828" class="line" marker-end="url(#teal)"/>
<rect x="104" y="355" width="391" height="115" class="box safe"/><text x="132" y="393" class="label">Terraform backend identity</text><text x="132" y="428" class="body">State Blob 读 / 写 / lease 数据面角色</text>
<rect x="605" y="355" width="391" height="115" class="box warn"/><text x="633" y="393" class="label">Terraform provider identity</text><text x="633" y="428" class="body">目标资源 Plan / Apply 所需角色</text>
<path d="M678 274V318H300V346" class="line dash" marker-end="url(#arrow)"/><path d="M678 318H800V346" class="line dash" marker-end="url(#arrow)"/>
<text x="176" y="519" class="small">可用分离身份缩小影响范围；共享身份时需审查 backend 与 provider 权限并集。</text>
''')

svg('approved-plan-flow.svg', '''
<text x="38" y="42" class="title">审批对象必须是不可变的那份 Plan</text>
<rect x="40" y="114" width="227" height="144" class="box safe"/><text x="61" y="151" class="label">Plan run</text><text x="61" y="184" class="body">Git SHA + target</text><text x="61" y="213" class="small">lock digest + state read</text><text x="61" y="239" class="small">生成 saved plan bytes</text>
<rect x="321" y="114" width="227" height="144" class="box cloud"/><text x="342" y="151" class="label">Protected artifact</text><text x="342" y="184" class="body">plan digest + run ID</text><text x="342" y="213" class="small">creation / expiry time</text><text x="342" y="239" class="small">限权访问与保留期</text>
<rect x="602" y="114" width="227" height="144" class="box warn"/><text x="623" y="151" class="label">Resource owner</text><text x="623" y="184" class="body">看摘要与目标范围</text><text x="623" y="213" class="small">指定人审批 / 拒绝</text><text x="623" y="239" class="small">审批附于当前 run</text>
<rect x="883" y="114" width="177" height="144" class="box safe"/><text x="904" y="151" class="label">Apply</text><text x="904" y="184" class="body">重验 digest</text><text x="904" y="213" class="small">消费保存计划</text><text x="904" y="239" class="small">失败则 stop</text>
<path d="M270 185H312" class="line" marker-end="url(#arrow)"/><path d="M551 185H593" class="line" marker-end="url(#arrow)"/><path d="M832 185H874" class="line" marker-end="url(#teal)"/>
<rect x="141" y="341" width="809" height="88" class="box neutral"/><text x="173" y="376" class="label">manifest 与 approval 必须一致</text><text x="173" y="408" class="body">source SHA · target · provider lock hash · plan hash · run · approver · approved time · expiry</text>
<path d="M435 259V332" class="line dash" marker-end="url(#arrow)"/><path d="M715 259V332" class="line dash" marker-end="url(#arrow)"/><path d="M895 258V294H943V332" class="line dash" marker-end="url(#arrow)"/>
<rect x="224" y="477" width="652" height="56" class="box bad"/><text x="257" y="512" class="body">Plan stale、篡改、错目标或过期 → 拒绝并重新 Plan + 审批</text>
''')

svg('failure-boundaries.svg', '''
<text x="38" y="42" class="title">失败先定位到拥有该边界的那一层</text>
<rect x="58" y="100" width="275" height="104" class="box neutral"/><text x="84" y="138" class="label">Repository boundary</text><text x="84" y="174" class="body">PR policy / protected branch</text>
<rect x="412" y="100" width="275" height="104" class="box warn"/><text x="438" y="138" class="label">Identity boundary</text><text x="438" y="174" class="body">issuer / subject / audience</text>
<rect x="766" y="100" width="275" height="104" class="box cloud"/><text x="792" y="138" class="label">Resource boundary</text><text x="792" y="174" class="body">Service Connection / Environment</text>
<path d="M334 152H402" class="line" marker-end="url(#arrow)"/><path d="M688 152H756" class="line" marker-end="url(#arrow)"/>
<rect x="184" y="286" width="730" height="100" class="box bad"/><text x="220" y="326" class="label">失败、拒绝或 timeout → 保留证据，不自动绕过</text><text x="220" y="359" class="body">run ID / stage / scope / status code / artifact digest / 当前 State</text>
<path d="M195 205V245H548V278" class="line dash" marker-end="url(#arrow)"/><path d="M549 205V278" class="line dash" marker-end="url(#arrow)"/><path d="M903 205V245H549V278" class="line dash" marker-end="url(#arrow)"/>
<rect x="237" y="444" width="624" height="71" class="box safe"/><text x="270" y="474" class="body">分类修复 → 重新验证同一提交 / 目标 / Plan 合同</text><text x="270" y="501" class="small">stale plan: stop and re-plan；不得以新建空计划绕过审批</text>
<path d="M549 387V436" class="line" marker-end="url(#teal)"/>
''')
