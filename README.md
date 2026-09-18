# 激光测距链路预算仿真工具（Laser Ranging Link Budget）

基于**公开教科书公式**的激光测距接收链路预算与信噪比（SNR）仿真脚本。  
命令行 + 三张权衡曲线图即为完整交付；不含 GUI / 数据库 / Web。

**用途**：把课题中「链路预算方法论」做一次可独立展示的工程化复现（A 版简历项目条目）。

---

## 功能

输入发射功率、接收口径、距离、大气参数等，输出：

- 接收功率 \(P_r\)
- 背景噪声功率 \(P_{bg}\)
- 散粒噪声主导下的信噪比 SNR

并可扫描参数，生成三张权衡图：

1. **SNR–距离** 曲线（含 SNR=1 距离标注）
2. **口径–SNR** 权衡曲线（背景受限 \(\propto D_r\) vs 暗电流受限 \(\propto D_r^2\)）
3. **背景噪声功率 vs 滤光带宽**

---

## 快速开始

```bash
# 依赖：Python 3.10+，numpy，matplotlib
pip install numpy matplotlib

# 典型参数一键输出 P_r 与 SNR
python run_link_budget.py

# 自定义参数
python run_link_budget.py --R 5000 --d-r 0.10 --alpha 0.1 --dlam-nm 1

# 同时重新生成 3 张图
python run_link_budget.py --plots

# 仅出图
python make_plots.py

# 单元测试（公式手算对照 + 物理规律）
python -m unittest tests.test_formulas -v
```

图默认写到 `figures/`。

---

## 物理模型（公式来源）

全部为公开教材内容，不涉及任何具体工程方案参数。

### 1. 高斯光束传播

\[
z_R = \frac{\pi w_0^2}{\lambda}, \quad
\theta = \frac{\lambda}{\pi w_0}, \quad
w(z) = w_0 \sqrt{1 + (z/z_R)^2}
\]

### 2. 链路预算（漫反射目标）

\[
A_r = \pi (D_r/2)^2, \quad
\eta_{geo} = \frac{A_r}{\pi w(R)^2}, \quad
\tau_{atm} = e^{-\alpha R}
\]

\[
P_r = P_t \cdot \eta_{tx} \cdot \eta_{geo} \cdot \rho \cdot \tau_{atm}^2 \cdot \tau_{rx}
\]

大气单程透过率 \(\tau_{atm}\)；测距双程取平方。

### 3. 背景噪声（白天太阳光场景）

\[
\Omega_{FOV} = \pi (\theta_{FOV}/2)^2
\]

\[
P_{bg} = L_{sun} \cdot A_r \cdot \Omega_{FOV} \cdot \Delta\lambda \cdot \tau_{rx}
\]

实现说明：\(L_{sun}\) 以 \(\mathrm{W/(m^2\cdot sr\cdot nm)}\) 给出时，\(\Delta\lambda\) 在背景项中按 **nm** 使用（与光谱辐亮度单位一致）。

### 4. 信噪比（散粒噪声主导，APD 简化）

\[
i_s = R_\lambda P_r, \quad i_{bg} = R_\lambda P_{bg}
\]

\[
i_{noise} = \sqrt{2e (i_s + i_{bg} + i_d) B}, \quad
SNR = \frac{i_s}{i_{noise}\sqrt{F}}
\]

- \(e = 1.6\times10^{-19}\,\mathrm{C}\)
- PIN：\(F=1\)；APD：`--apd` 使用 \(F=4\) 作为演示量级

### 进阶（可选）

Koschmieder 能见度–衰减换算：

\[
\alpha \approx \frac{3.912}{V}\left(\frac{\lambda}{550\,\mathrm{nm}}\right)^{-1.3}
\]

---

## 典型参数（测试用量级，通用/公开）

| 参数 | 符号 | 典型值 |
|------|------|--------|
| 发射峰值功率 | \(P_t\) | 2 W |
| 束腰半径 | \(w_0\) | 3 mm |
| 波长 | \(\lambda\) | 1064 nm |
| 接收口径 | \(D_r\) | 0.05 ~ 0.30 m |
| 距离 | \(R\) | 1 ~ 10 km |
| 大气衰减 | \(\alpha\) | 0.1 ~ 1.0 /km |
| 目标反射率 | \(\rho\) | 0.1 |
| 滤光带宽 | \(\Delta\lambda\) | 1 nm |
| 太阳辐亮度 | \(L_{sun}\) | 0.05 W/(m²·sr·nm) |
| 接收视场 | \(\theta_{FOV}\) | 0.5 mrad |
| 响应度 | \(R_\lambda\) | 0.4 A/W |
| 暗电流 | \(i_d\) | 10 nA |
| 带宽 | \(B\) | 10 MHz |

> 注意：接口中 `alpha` 为 **1/m**（内部由 `/km` 参数自动换算）。

---

## 运行示例输出（示意）

```
=== Laser ranging link budget ===
Distance R          = 5000.0 m (5.00 km)
...
Received power P_r  = ... W
Background P_bg     = ... W
SNR                 = ...
```

三张图见 `figures/fig1_snr_vs_range.png` 等。

---

## 代码结构

```
link_budget/
  formulas.py   # 教科书公式（独立函数 + docstring）
  budget.py     # 组合为 link_budget(...) 与参数扫描
  plots.py      # 三张权衡图
run_link_budget.py  # CLI 入口
make_plots.py
tests/test_formulas.py
figures/
```

---

## 参考文献

1. Saleh, B. E. A., & Teich, M. C. *Fundamentals of Photonics*（高斯光束；光电探测噪声）.
2. 国内任一《激光雷达原理》教材中的链路预算 / 大气传输章节（多本均有）。

---

## 涉密自查（发布前）

- [x] 代码仅使用上表量级的**通用公开参数**，无课题/专利具体方案参数
- [x] 无所内项目编号、内部文档表述、合作单位信息
- [ ] 开源前与导师口头/书面确认（留沟通记录）

**红线**：国防专利保护具体技术方案，不保护教科书公式。公开公式 + 通用参数 = 安全；课题真实参数 = 不得写入。

---

## License

MIT — see [LICENSE](LICENSE).

---

## 简历写法（完成后）

- 激光测距链路预算仿真工具｜独立开发｜Python（GitHub 开源）
- 基于高斯光束传输与大气衰减模型，开发链路预算与信噪比仿真脚本，实现接收功率/SNR 随距离、口径、滤光带宽的定量分析，输出系统参数权衡曲线，验证「口径—视场—带宽」权衡规律
