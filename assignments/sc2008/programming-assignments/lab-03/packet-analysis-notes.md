# SC2008-LAB03 协议解析笔记

## 1. 从请求流程理解 ARP 与 DNS

在本次同一 IPv4 subnet（子网）的实验中，四类报文的作用是：

| 顺序 | 报文 | 作用 |
| --- | --- | --- |
| 1 | ARP request | 以 Ethernet broadcast（以太网广播）询问服务器 IP 对应的 MAC |
| 2 | ARP reply | 返回该 IP-to-MAC mapping（IP 到 MAC 的映射） |
| 3 | UDP request | 客户端临时端口向服务器 port 17 发送应用层消息 |
| 4 | UDP reply | 服务器 port 17 将 quote 发回客户端请求使用的端口 |

ARP cache 已有有效映射时，不一定出现新的 ARP request/reply。因此，“四类报文”是本次清缓存后的观察路线，不是每一次 UDP 通信的固定包数。

DNS 解决 domain name → IP address，ARP 解决本地链路上的 IPv4 next hop → MAC address。直接使用 IPv4 地址通常不需要为该目标做 DNS 查询；反向查询没有 PTR record，也不意味着服务器不可达。

判断 MAC 地址时必须区分三个角色：

- **Ethernet destination**：这一跳帧实际送往的 MAC。
- **ARP target protocol address**：想询问的 IPv4 地址。ARP 本身没有 IPv4 header；不能把 ARP 表里的 sender/target IP 误称为该报文的 IP 首部字段。
- **Default gateway MAC**：可用 `arp -a <gateway-ip>` 核对。同子网服务器可直接交付，UDP 帧中的服务器 MAC 不能拿来填写网关 MAC；跨子网交付时，目的 IP 仍是服务器，但本地 Ethernet 目的 MAC 通常属于所选路由的 next hop。

本次两个不同 MAC 都回应了同一个目标 IP。只能据截图记录这一事实，并根据 UDP 请求目的 MAC、回复源 MAC 选择实际往返使用的映射；无法仅凭这些截图断定是地址冲突、代理机制或其他原因。

## 2. 封装边界与长度

下表使用本次请求的实际长度，但不保留原始地址或身份 payload。所有偏移均从捕获字节的首字节起、以 0 开始计数。

| 内容 | 起始偏移 | 长度 | 如何确定 |
| --- | --- | --- | --- |
| Ethernet II header | 0 | 14 bytes | 目的 MAC 6 + 源 MAC 6 + EtherType 2 |
| IPv4 header | 14 | 20 bytes | IHL = 5，首部长度为 5 × 4 |
| UDP header | 34 | 8 bytes | 四个 16-bit 字段 |
| Application data | 42 | 32 bytes | UDP Length 40 − header 8 |

```text
Captured Ethernet frame: 74 bytes
└── Ethernet header: 14 + Frame Data: 60
    └── IPv4 header: 20 + Packet Data: 40
        └── UDP header: 8 + Application data: 32
```

因此下面四个名字表示不同范围：

- **Complete Captured Data**：截图提供的完整 74 bytes。
- **Frame Data**：剥去 Ethernet header 后的 60 bytes，即完整 IPv4 datagram。
- **Packet Data**：剥去 IPv4 header 后的 40 bytes，即完整 UDP datagram。
- **UDP Data**：剥去 UDP header 后的 32 bytes，即应用层消息。

本次捕获不含 preamble/SFD 和 FCS，不能为了匹配教材的完整物理帧示意图而自行补字节。捕获长度也不包括 inter-frame gap（帧间间隔）。

## 3. 按字段判断上层协议

### Ethernet → IPv4

EtherType 的两个字节是 `08 00`，即 `0x0800`，表示上层为 IPv4。不要把 EtherType 与 IP Protocol 字段混为一谈。

### IPv4 → UDP

IPv4 首字节 `45` 分成两个 nibble（半字节）：高四位是 Version = 4，低四位是 IHL = 5。IHL 的单位是 32-bit word，因此首部为 20 bytes，没有 Options + Padding。

本次 Protocol = `0x11`，十进制 17，表示 UDP。这里的 **IP protocol number 17** 和 **QoD port 17** 恰好数值相同，但来自不同首部、意义不同。

Flags 为 `000`：reserved = 0，DF = 0 表示允许分片，MF = 0 表示没有后续分片。结合 Fragment Offset = 0，本次是未分片的数据报。仅看到 MF = 0 不足以单独判断未分片，因为最后一片的 MF 也为 0。

### UDP → 应用消息

UDP Length 包括 8-byte header 和 payload；IPv4 Total Length 则包括 IPv4 header 和整个 UDP datagram。因此本次分别为 40 和 60，而不是都填成消息长度 32。

UDP reply 应发回请求的 source port；客户端临时端口由运行时选择，不应硬记某次实验的具体数值。

## 4. 字节抄录与验证方法

1. 选择 **client-to-server request**，不要把 quote reply 误当作 3B 的分析对象。
2. 从 packet bytes pane（报文字节窗格）读取十六进制；地址、长度、首部和 payload 都来自同一条报文。
3. 每行填 8 bytes。末行不足 8 bytes 时保留实际数量，不补 `00`。
4. 按 network byte order（网络字节序，大端）解释多字节字段。例如 `00 3c` = 60，不能读成 `3c00`。
5. 用 `IP Total Length = IP header + UDP Length` 和 `UDP Length = 8 + payload length` 交叉检查边界。
6. 解码消息时只读实际 payload；Java 接收端应使用 `reply.getLength()`，而不是把整个接收缓冲区都解码。

校验和的范围也不同：IPv4 header checksum 只覆盖 IP 首部；UDP checksum 覆盖 IPv4 pseudo-header、UDP header 和 UDP data。伪首部用于计算，不是 UDP payload 中额外传输的一段数据。本次请求的两项重算均通过；这是抄录与字段一致性的检查，不是身份认证或对服务器行为的保证。

## 5. 抓包和保存的易错点

- Capture filter（捕获过滤器）在采集时筛选报文；display filter（显示过滤器）仅改变显示范围，不会自动删去文件里的其他报文。
- 接收到 reply 才能确认本次请求完成了往返；没有 DNS PTR record、某次 ping 失败和 UDP timeout 不是同一种结论。
- 同名 `.java` 文件不保证内容相同；修改源代码后必须重新 `javac`，否则可能继续运行旧 `.class`。
- 备份只需相关报文时，应导出 displayed packets（当前显示的报文），重新打开并核对包数，避免把无关网络流量一并分享。不要把完整抓包传入公开 Git 仓库。
- 保存到实验室 PC 的 D 盘仅是本机留存。离开前确认文件存在，并将需要保留的抓包与课堂源代码另存到个人设备或私人存储。

来源与证据边界见 [实验 README](README.md)。本页是去标识化的复习总结，不是原始答案模板或完整抓包副本。
