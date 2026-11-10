# SC4001 Group Project：量子测量数据的潜在表征可靠性

2026-11-10 确认已通过 NTULearn 提交报告和代码。

实验使用八自旋 Ising 链的 Z 基测量数据。预测下一个自旋时，三种 VAE 解码器分别可以看到零个、少量或全部先前的测量值。我们比较模型拟合测量分布的效果、从潜在表征估计物理量的误差，以及打乱潜变量后解码结果的变化。另用无潜变量的自回归模型作对照。

代码、实验记录和复现说明见独立私有仓库 [quantum-latent-reliability](https://github.com/tigerdyger/quantum-latent-reliability)。仓库中的 `work/FINAL_HANDOFF.md` 列出了本地归档的报告、v5 提交包及其校验值。
