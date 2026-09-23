# SC2008-LAB03 — Sniffing and Analysing Network Packets

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2008 Computer Networks |
| 类型 | Wireshark packet capture（抓包）与 protocol encapsulation（协议封装）分析 |
| 实验日期 | 2026-09-23，Week 7 |
| 建议时长 | 1 小时 50 分钟 |
| 环境 | 实验室 Windows PC、Wireshark、Java UDP client 与课堂 QoD server |
| 状态 | Exercise 3A–3F 已完成并核对；提交状态不在公开仓库记录 |
| 相关讲义知识点 | `SC2008-L01-T02`、`SC2008-L01-T04`、`SC2008-L03-T01` |

## 实验目标

通过 RFC 865 Quote of the Day（每日引语）请求与回复，观察 ARP 如何为本地交付解析 MAC address，以及 application message（应用层消息）如何依次封装在 UDP datagram、IPv4 datagram 和 Ethernet frame 中。重点是从真实字节识别各层边界，而不是只看 Wireshark 的协议名称。

## 任务与完成情况

| 任务 | 本次完成内容 | 手册印刷页码 |
| --- | --- | --- |
| 3A：Packet sniffing（抓包） | 捕获并区分 ARP request/reply 与 UDP request/reply；核对 DNS 配置及网关 MAC | 3-1–3-3 |
| 3B：Data encapsulation（数据封装） | 选取客户端发往服务器的 UDP 请求，抄录完整捕获字节，每行 8 bytes | 3-3–3-4 |
| 3C：Ethernet frame（以太网帧） | 解析源/目的 MAC、EtherType 和 Frame Data | 3-4–3-5 |
| 3D：IPv4 datagram（IPv4 数据报） | 解析 Version、IHL、Total Length、Identification、Flags、Fragment Offset、Protocol、地址与 Packet Data | 3-5 |
| 3E：UDP datagram（UDP 数据报） | 解析源/目的端口、UDP Length 和 Data | 3-6 |
| 3F：Application PDU（应用层协议数据单元） | 将 UDP payload 按 ASCII 解码，确认与客户端实际发送的消息一致 | 3-6 |

原手册描述包含 DNS 的流程；本次现场补充说明要求 3A 按 **ARP request、ARP reply、UDP request、UDP reply 四行**填写，通常不会看到 DNS request/reply。本次客户端直接使用服务器 IP，因此没有为此次 QoD 请求解析域名；DNS server 地址来自主机配置，不冒充抓包结果。

## 文件与复现入口

- [packet-analysis-notes.md](packet-analysis-notes.md)：分层读取方法、长度自检、ARP 与 DNS 的区别及常见错误。
- [Lab 2 UDP client](../lab-02/code/Rfc865UdpClient.java)：已有的去标识化客户端参考实现。Lab 3 不再复制一份含课堂地址与身份信息的代码。
- [Lab 2 本地测试说明](../lab-02/README.md#本地测试)：用于复习 socket request/reply；localhost 测试不能复现以太网 ARP 交换。

本次课堂重新编译并运行了独立客户端，成功发送身份消息并收到 quote；公开参考实现通过命令行参数传入信息，与课堂副本并非逐字节相同。

## 验证与结果边界

- 实际过滤后的列表有五条相关记录：一条 ARP request、两条 ARP reply、一条 UDP request 和一条 UDP reply。四行表保留与实际 UDP 往返 MAC 一致的 ARP reply，并另注额外回复；不把五条抓包记录说成只有四条。
- 请求捕获长度为 74 bytes：Ethernet header 14 + IPv4 header 20 + UDP header 8 + application data 32。
- IPv4 Total Length 为 60 bytes，UDP Length 为 40 bytes，ASCII message 为 32 bytes；解码结果与客户端消息相符。
- 请求中的 IPv4 header checksum 和 UDP checksum 已根据完整十六进制字节重新计算并通过核对。UDP 校验包含 IPv4 pseudo-header（伪首部）。这项检查针对该请求，不扩展为所有抓包均已验证。
- 回复截图显示 99 captured bytes，其中 UDP payload 为 57 bytes；客户端也报告收到 quote。未取得完整回复字节，故没有宣称重算过回复 checksum 或独立解码过整段 quote。
- 本地核对依据是课堂截图、用户提供的命令输出和请求字节；没有在本机重新运行课堂服务器，也没有声称已审计完整 `.pcapng`。

## 提交与隐私

手册要求在实验结束时在线提交 **completed answer template（填写完成的答案模板）**；实际上传入口及额外文件要求以当期 lab site 和 TA 通知为准。不要把 Lab 2 的 Java 源码提交要求误套到 Lab 3。

公开仓库只保留去标识化总结，不保存官方手册、答案模板、已填答案、原始抓包、截图、实际姓名、组别、学号或实验室主机/服务器/网关地址。此目录用白名单式 `.gitignore` 限制可跟踪文件；不要用 `git add -f` 绕过它。`.gitignore` 不能删除已经进入 Git 历史的文件。

抓包和课堂源代码应另行备份到个人设备或私人存储。保存在实验室电脑的 D 盘不等于已经完成异地备份，也不能据此保证以后仍可访问。

## 来源

- SC2008/CZ3006/CE3005, *Laboratory Manual No. 3: Understanding Network Operations and Encapsulation by Sniffing and Analysing Network Packets*，封面标注 Semester 2, 2021–2022；本次提供的 PDF 共 7 页，正文印刷 pp. 3-1–3-6（PDF pp. 2–7）。
- *Lab 3 answer template*：Exercise 3A–3F 与每行 8 bytes 的填写格式。
- 2026-09-23 用户转述的现场四行表说明，以及课堂抓包截图与命令输出；原始证据仅留本地。
