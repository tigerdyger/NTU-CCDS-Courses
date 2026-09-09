# SC2008-LAB02 — Programming Network Applications using Sockets

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 课程 | SC2008 Computer Networks |
| 类型 | Java socket 编程实验 |
| 实验日期 | 2026-09-09 |
| 建议时长 | 2 小时 |
| 状态 | 必做与选做部分均已完成并核对；提交状态不在公开仓库记录 |
| 相关讲义知识点 | `SC2008-L01-T02`、`SC2008-L01-T04` |

## 实验目标

使用 socket API（套接字接口）在 Application layer（应用层）实现 RFC 865 Quote of the Day protocol（每日引语协议），观察 application（应用）如何通过 Transport layer（传输层）的 UDP 与 TCP service（服务）交换消息。

## 目录与任务

```text
code/
├── Rfc865UdpServer.java   # Exercise 2C：UDP server
├── Rfc865UdpClient.java   # Exercise 2D：UDP client，课程要求的唯一提交物
├── Rfc865TcpClient.java   # Exercise 2F：TCP client（选做）
└── Rfc865TcpServer.java   # Exercise 2G：TCP server（选做）
```

RFC 865 使用 well-known port 17（知名端口 17）。UDP server 收到 datagram（数据报）后，把少于 512 个 ASCII characters（字符）的 quote 返回到该 datagram 的 source address 与 source port；TCP server 建立 connection（连接）后发送 quote 并关闭连接。

## 构建

需要 JDK 21 或兼容版本：

```bash
cd code
javac Rfc865UdpServer.java Rfc865UdpClient.java \
      Rfc865TcpServer.java Rfc865TcpClient.java
```

## 本地测试

示例使用非特权测试端口 `18650`；省略端口参数时，程序使用 RFC 865 规定的 port 17。

### UDP

Terminal 1：

```bash
java Rfc865UdpServer 18650
```

Terminal 2：

```bash
java Rfc865UdpClient 127.0.0.1 \
  "Test User, Lab Group, 127.0.0.1" 18650
```

### TCP（选做）

Terminal 1：

```bash
java Rfc865TcpServer 18650
```

Terminal 2：

```bash
java Rfc865TcpClient 127.0.0.1 \
  "TCP client test" 18650
```

## 设计与验证

- UDP client 通过 `DatagramSocket` 发送 request datagram，再使用 512-byte buffer（缓冲区）接收 reply；解码时只读取 `reply.getLength()` 指定的有效数据。
- UDP server 从 request 中取得 client address 与 ephemeral port（临时端口），据此构造 reply datagram。
- TCP client 使用 `Socket` 建立 connection；TCP server 使用 `ServerSocket` 接受连接，并为每个 client 创建独立 thread（线程）。
- 两组程序均通过 localhost（本地主机）端到端测试。课堂 server 已记录 UDP request；其 reply service 在现场不稳定，因此公开记录不把远端 quote 写成已验证结果。
- `code/` 下的公开版本使用命令行参数代替真实姓名、实验组、内网 IP 与课堂 server address，不包含个人或实验室网络信息。

## 提交边界

课程只要求通过 NTULearn lab site 提交 UDP client source code（源代码），不提交 server 或选做 TCP 程序。实际提交副本需要按课程要求填写姓名、实验组和 client IP；公开仓库中的代码是去标识化的学习参考实现，不是课堂原始提交副本。生成式 AI 或外部辅助工具的使用必须服从课程当期政策，提交者应能够解释并独立修改程序。

## 来源

- SC2008/CZ3006/CE3005, *Laboratory Manual No. 2: Programming Network Applications using Sockets*, Laboratory 2, pp. 2-1--2-5（2026-09-09 本地核对）。
- J. Postel, *RFC 865: Quote of the Day Protocol*, May 1983.
