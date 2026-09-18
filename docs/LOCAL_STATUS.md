# 任务A 交付说明（本地）

## 已完成

| 项 | 路径 |
|----|------|
| 可运行仿真包 | `link_budget/` + `run_link_budget.py` |
| 单元测试 15 项全部通过 | `tests/test_formulas.py` |
| 三张权衡图 | `figures/fig1_snr_vs_range.png` 等 |
| README（公式/参数/文献） | `README.md` |
| MIT LICENSE | `LICENSE` |
| 面试题答案 | `docs/interview_A.md` |
| 涉密自查 | `docs/security_checklist.md` |
| 验收清单 | `docs/acceptance.md` |

## 本地已验证命令

```bash
# 单元测试
python -m unittest tests.test_formulas -v

# 输出典型参数 P_r / SNR
python run_link_budget.py

# 出图
python run_link_budget.py --plots
# 或
python make_plots.py
```

**依赖**：本机需 `numpy` + `matplotlib`（系统 Python 3.12 已具备）。  
MIMO 内置 Python 有 numpy 但无 matplotlib，出图请用系统 Python。

## 典型运行结果（α=0.1/km, D_r=10cm, R=5km）

- P_r ≈ 3.23e-4 W
- SNR ≈ 6.4e3（约 76 dB）
- Koschmieder 能见度 ≈ 16.6 km（λ=1064 nm）

## 还需你完成的

1. **与导师确认**开源公式小工具（`docs/security_checklist.md` 第 3 项）
2. 创建 **GitHub 公开仓库**，上传本目录（可去掉 `docs/acceptance.md` 等过程文件，或保留）
3. 确认 README 链接、截图 3 张图
4. 把 A-7 简历条目写入 A 版简历
