# SC2008-LAB01 — Understanding Networking with Internet Technologies

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2008 Computer Networks |
| 类型 | 网络配置与诊断实验（无编程任务） |
| 实验日期 | 2026-08-26 |
| 建议时长 | 2 小时 |
| 状态 | 已完成并核对；提交状态不在公开仓库记录 |
| 相关讲义知识点 | `SC2008-L01-T02`、`SC2008-L01-T03`、`SC2008-L03-T01` |

## 实验目标

使用 Windows 提供的 networking tools（网络工具）观察 TCP/IP protocol suite（TCP/IP 协议族）在真实主机中的配置和运行结果，并把抽象的 layer、address 与 protocol 概念对应到具体网络接口和诊断命令。

## 任务概述

1. **Communication architecture（通信体系结构）与 addressing（寻址）**
   - 将 IP、network interface card、port number、IP address 和 MAC address 对应到 TCP/IP layers。
2. **主机与接口配置**
   - 查询 MAC address 与制造商；识别 IPv4/CIDR、loopback/private address；检查 DHCP、subnet mask 与 NAT 前后的地址。
3. **Internet services（互联网服务）与 name resolution（名称解析）**
   - 核对 common well-known ports；了解 `.sg` domain registration；查询 local/authoritative DNS servers、DNS records 与 DNS cache；检查 Windows WINS 配置。
4. **Local delivery（本地交付）与 path diagnosis（路径诊断）**
   - 查询 default gateway；使用 ARP 观察 IP-to-MAC mapping；使用 `ping` 检查 reachability；使用 `tracert` 观察到目标的 router path。

## 使用的工具

```text
ipconfig /all
ipconfig /displaydns
ipconfig /flushdns
nslookup
arp -a
ping
tracert
```

实验还使用 WHOIS、MAC vendor lookup 和公网 IP 查询服务核对注册信息及地址归属。这些查询结果会随时间、实验地点和所连接网络变化，不能把某次输出当作固定课程结论。

## 完成与验证

- 已按 answer template 完成 Exercise 1A--1H 与 1J--1N，并对概念分类、命令输出与解释进行本地核对。
- 本实验没有 source code、build command 或 automated test；验证依据是命令的实际输出和概念解释是否一致。
- ARP 只能直接解析 local link（本地链路）上的 MAC address；访问其他网络时，主机会解析 default gateway 的 MAC address，而不是远端服务器的 MAC address。
- `ping` 或 `tracert` 失败不必然表示目标不可达，firewall（防火墙）可能过滤相关探测报文。

## 提交与隐私

提交应通过 NTULearn 的 **lab site** 完成，而不是课程 main site。公开仓库不保存官方实验手册、答案模板或已填写答案，也不记录姓名、MAC/IP address、DNS/WINS server、default gateway、neighbour device 等主机或个人相关信息；实际提交以本地完成的答案文档为准。

## 来源

- SC2008/CZ3006/CE3005, *Laboratory Manual No. 1: Understanding Networking with Internet Technologies*, Laboratory 1, pp. 1-1--1-12（2026-08-26 本地核对）。
