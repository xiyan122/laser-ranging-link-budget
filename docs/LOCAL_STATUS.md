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

1. **与导师确认**开源公式小工具（`docs/security_checklist.md` 第 3 项）——仓库已公开，尽快补沟通记录
2. ✅ GitHub 公开仓库：**https://github.com/xiyan122/laser-ranging-link-budget**
3. 在浏览器打开仓库链接，确认 README / 三张图 / LICENSE 可见
4. 把 A-7 简历条目写入 A 版简历，链接可写在项目旁

### 推送说明（2026-09-18）

- 远端：`git@github.com:xiyan122/laser-ranging-link-budget.git`
- 本机 `https://github.com` 直连不稳，最终经 GitHub Contents API 上传全部 18 个文件
- 本地 git 历史与远端 API 提交不同源；若要以本地 git 为准，在网络正常时：
  `git pull --rebase origin main` 再 `git push`（勿在未确认时 force push）
