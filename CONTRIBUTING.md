# 贡献指南

欢迎参与贡献！在提交贡献前，请仔细阅读以下指南。

## 如何贡献

### 1. 报告问题
- 在提交问题前，请先搜索是否已有类似问题
- 提供清晰的问题描述、复现步骤和环境信息
- 如果是Bug报告，请包括：
  - 使用的Python版本
  - 重现步骤
  - 预期行为与实际行为的对比
  - 相关日志或截图

### 2. 提交代码
1. Fork 项目并创建特性分支 (`git checkout -b feature/AmazingFeature`)
2. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
3. 推送到分支 (`git push origin feature/AmazingFeature`)
4. 打开 Pull Request

**Pull Request要求**:
- 标题清晰描述变更内容
- 详细说明变更原因和影响
- 关联相关Issue(如果有)
- 确保所有CI测试通过
- 保持提交历史整洁(使用`git rebase`而非`git merge`)

### 3. 代码风格
- 遵循PEP 8代码风格指南
- 使用类型注解(Type Hints)
- 确保代码通过所有测试
- 为新功能添加适当的测试用例
- 保持函数简洁(不超过50行)
- 添加必要的文档字符串(docstring)

### 4. 代码审查流程
- 至少需要1名核心维护者批准才能合并
- 审查重点包括：
  - 代码质量与可维护性
  - 测试覆盖率
  - 文档更新
  - 向后兼容性考虑
- 审查意见应在3个工作日内回复

### 5. 文档
- 更新相关文档以反映您的更改
- 确保README和其他文档保持最新
- 为新增API添加使用示例

## 开发环境设置

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/astrbot_plugin_checkin.git
   cd astrbot_plugin_checkin
   ```

2. 创建虚拟环境(推荐)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   pip install -e .  # 以开发模式安装
   ```

4. 运行测试
   ```bash
   pytest
   ```

5. 代码格式化(可选)
   ```bash
   black .
   isort .
   ```

## 版本控制规范
- 使用语义化版本控制(SemVer)
- 主分支(`main`)始终保持可发布状态
- 特性分支命名: `feature/<description>`
- Bug修复分支命名: `fix/<issue-number>`
- 提交信息格式:
  ```
  <type>(<scope>): <subject>
  
  <body>
  
  <footer>
  ```
  其中type可以是: feat, fix, docs, style, refactor, test, chore

## 项目结构
```
astrbot_plugin_checkin/
├── main.py           # 主程序入口
├── messages.py       # 消息处理模块
└── README.md         # 项目说明
```

## 行为准则

请遵守项目的[行为准则](CODE_OF_CONDUCT.md)。我们致力于提供一个友好、尊重和包容的贡献环境。

感谢您的贡献！