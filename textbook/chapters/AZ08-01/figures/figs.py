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


svg("topology-choice.svg", '''
<text x="38" y="42" class="title">两种 Hub-Spoke 拓扑的 transit 语义不同</text>
<rect x="42" y="78" width="480" height="382" class="box neutral"/><text x="66" y="115" class="label">经典 VNet peering</text>
<rect x="190" y="148" width="190" height="86" class="box cloud"/><text x="214" y="182" class="label">Hub VNet</text><text x="214" y="211" class="small">ER / VPN gateway</text>
<rect x="67" y="315" width="176" height="74" class="box safe"/><text x="91" y="359" class="label">Spoke A</text><rect x="317" y="315" width="176" height="74" class="box safe"/><text x="341" y="359" class="label">Spoke B</text>
<path d="M220 239V279H155V306" class="line" marker-end="url(#arrow)"/><path d="M340 239V279H405V306" class="line" marker-end="url(#arrow)"/>
<path d="M243 350H317" class="line dash" marker-end="url(#red)"/><text x="119" y="428" class="small">Peering 本身非传递；spoke 间需另配路由/连接</text>
<rect x="578" y="78" width="480" height="382" class="box cloud"/><text x="602" y="115" class="label">Standard Virtual WAN</text>
<rect x="720" y="148" width="196" height="86" class="box warn"/><text x="746" y="182" class="label">Virtual hub</text><text x="746" y="211" class="small">hub router + route tables</text>
<rect x="603" y="315" width="176" height="74" class="box safe"/><text x="625" y="359" class="label">VNet / branch</text><rect x="856" y="315" width="176" height="74" class="box safe"/><text x="878" y="359" class="label">VNet / branch</text>
<path d="M752 239V279H690V306" class="line" marker-end="url(#teal)"/><path d="M884 239V279H944V306" class="line" marker-end="url(#teal)"/>
<path d="M779 350H856" class="line" marker-end="url(#teal)"/><text x="645" y="428" class="small">Standard 提供 hub 管理的传递路由，需设计 route tables</text>
<text x="74" y="505" class="tiny">选择依据：peer 数量、跨区/transit 需求、路由控制方式、运维与成本，而非“hub”这个名称。</text>
''')

svg("route-exchange-and-data-path.svg", '''
<text x="38" y="42" class="title">BGP 交换可达性，数据包仍按实际路由逐跳转发</text>
<rect x="54" y="112" width="220" height="143" class="box neutral"/><text x="78" y="151" class="label">企业边界路由器</text><text x="78" y="186" class="body">分支前缀</text><text x="78" y="220" class="small">本地策略 / BGP</text>
<rect x="410" y="92" width="253" height="80" class="box cloud"/><text x="438" y="127" class="label">ExpressRoute private peering</text><text x="438" y="153" class="small">Azure VNet 私有连通</text>
<rect x="410" y="205" width="253" height="80" class="box warn"/><text x="438" y="240" class="label">Route-based S2S VPN</text><text x="438" y="266" class="small">IPsec 隧道 · 可选 BGP</text>
<rect x="802" y="133" width="239" height="135" class="box safe"/><text x="830" y="172" class="label">Hub VNet gateway</text><text x="830" y="207" class="body">路由传播 → Spoke</text><text x="830" y="239" class="small">gateway transit 成对配置</text>
<path d="M281 153H400" class="line" marker-end="url(#arrow)"/><path d="M281 215H400" class="line" marker-end="url(#arrow)"/>
<path d="M673 132H792" class="line" marker-end="url(#teal)"/><path d="M673 245H792" class="line" marker-end="url(#arrow)"/>
<rect x="802" y="353" width="239" height="91" class="box neutral"/><text x="830" y="390" class="label">Workload Spoke</text><text x="830" y="421" class="small">只收到可传播路由</text>
<path d="M922 270V343" class="line" marker-end="url(#teal)"/><path d="M802 398H676V314H280V265" class="line dash" marker-end="url(#arrow)"/>
<text x="353" y="335" class="small">回程是另一条独立路由决策；核对实际前缀与路径</text>
<rect x="118" y="405" width="548" height="76" class="box bad"/><text x="147" y="438" class="label">ExpressRoute 不是 transit router</text><text x="147" y="465" class="small">跨站点转发要由网络服务商或明确的 Azure 路由架构承接</text>
<text x="55" y="525" class="tiny">ER 与 VPN 同前缀选择有方向与组件边界；不要把 Azure Route Server preference 和 on-premises local preference 混为一谈。</text>
''')

svg("hybrid-dns-directions.svg", '''
<text x="38" y="42" class="title">混合 DNS 是两条不同的查询路径</text>
<rect x="45" y="102" width="274" height="146" class="box neutral"/><text x="69" y="142" class="label">On-premises client</text><text x="69" y="176" class="body">orders.privatelink…</text><text x="69" y="212" class="small">企业 DNS 条件转发器</text>
<rect x="414" y="94" width="282" height="160" class="box cloud"/><text x="442" y="134" class="label">Private Resolver · Hub</text><text x="442" y="172" class="body">Inbound endpoint VIP</text><text x="442" y="207" class="small">Azure DNS + linked private zone</text>
<rect x="785" y="102" width="270" height="146" class="box safe"/><text x="809" y="142" class="label">Azure Private DNS</text><text x="809" y="177" class="body">Private Link record</text><text x="809" y="212" class="small">zone linked to resolver VNet</text>
<path d="M321 162H405" class="line" marker-end="url(#arrow)"/><path d="M698 174H777" class="line" marker-end="url(#teal)"/><text x="334" y="287" class="small">查询方向 A：On-premises → Azure inbound</text>
<rect x="45" y="343" width="274" height="144" class="box warn"/><text x="69" y="382" class="label">Azure workload VNet</text><text x="69" y="418" class="body">ledger.corp.example</text><text x="69" y="455" class="small">Azure-provided DNS</text>
<rect x="414" y="335" width="282" height="160" class="box cloud"/><text x="442" y="375" class="label">Ruleset + outbound</text><text x="442" y="413" class="body">longest suffix match</text><text x="442" y="449" class="small">linked to workload VNet</text>
<rect x="785" y="343" width="270" height="144" class="box neutral"/><text x="809" y="382" class="label">Enterprise DNS</text><text x="809" y="418" class="body">corp.example zone</text><text x="809" y="455" class="small">UDP/TCP 53 path required</text>
<path d="M321 408H405" class="line" marker-end="url(#arrow)"/><path d="M698 416H777" class="line" marker-end="url(#teal)"/><text x="334" y="527" class="small">查询方向 B：Azure workload → outbound → On-premises DNS</text>
''')

svg("dns-suffix-and-loop.svg", '''
<text x="38" y="42" class="title">DNS 先选最长后缀，再检查 forwarding 的落点</text>
<rect x="54" y="101" width="407" height="333" class="box neutral"/><text x="80" y="142" class="label">查询：ledger.corp.example</text>
<rect x="90" y="183" width="332" height="65" class="box neutral"/><text x="116" y="222" class="body">example → 10.1.0.53</text>
<rect x="90" y="270" width="332" height="76" class="box safe"/><text x="116" y="301" class="label">corp.example → 10.1.0.53</text><text x="116" y="328" class="small">命中更长后缀</text>
<text x="85" y="391" class="small">规则集须链接到发起查询的 VNet；</text><text x="85" y="416" class="small">目标 DNS 还需有双向网络与 UDP/TCP 53。</text>
<rect x="599" y="101" width="446" height="333" class="box warn"/><text x="625" y="142" class="label">Loop 风险：ruleset 链回自己的 inbound</text>
<rect x="637" y="185" width="159" height="82" class="box cloud"/><text x="654" y="219" class="body">Hub VNet</text><text x="654" y="246" class="small">inbound VIP</text>
<rect x="852" y="185" width="155" height="82" class="box neutral"/><text x="870" y="219" class="body">Outbound</text><text x="870" y="246" class="small">ruleset</text>
<path d="M797 208H843" class="line" marker-end="url(#arrow)"/><path d="M920 276V330H715V276" class="line" marker-end="url(#red)"/>
<text x="649" y="372" class="small">若把“转给 inbound VIP”的规则集</text><text x="649" y="400" class="small">链接到该 inbound 所在 VNet，可能形成循环。</text>
''')

svg("diagnose-hybrid-planes.svg", '''
<text x="38" y="42" class="title">分别验证路由控制、数据路径与名称解析</text>
<rect x="58" y="99" width="296" height="120" class="box cloud"/><text x="86" y="140" class="label">1 · Control / route exchange</text><text x="86" y="177" class="body">BGP peer · prefixes · propagation</text>
<rect x="402" y="99" width="296" height="120" class="box safe"/><text x="430" y="140" class="label">2 · Packet forwarding</text><text x="430" y="177" class="body">双向 route · gateway · NSG/NVA</text>
<rect x="746" y="99" width="296" height="120" class="box warn"/><text x="774" y="140" class="label">3 · DNS resolution</text><text x="774" y="177" class="body">zone/ruleset · suffix · UDP/TCP 53</text>
<path d="M355 159H393" class="line" marker-end="url(#arrow)"/><path d="M699 159H737" class="line" marker-end="url(#arrow)"/>
<rect x="120" y="294" width="384" height="132" class="box bad"/><text x="148" y="336" class="label">Route Server 交换路由</text><text x="148" y="374" class="body">BGP route reflector</text><text x="148" y="404" class="small">它不承载 NVA ↔ VM 数据包</text>
<rect x="598" y="294" width="384" height="132" class="box neutral"/><text x="626" y="336" class="label">排障的判别顺序</text><text x="626" y="374" class="body">有路由 ≠ 双向可达 ≠ DNS 可解析</text><text x="626" y="404" class="small">用目标 IP 探测与查询名分别定位</text>
<path d="M506 359H589" class="line dash" marker-end="url(#teal)"/>
<text x="177" y="491" class="small">保留来源 VNet / prefix / 方向 / 查询名 / 目标 resolver / 失败层；不要从单次 ping 推断全部链路。</text>
''')
