# SmartUI MCP EC2隧道部署指南

## 🎯 部署概述

SmartUI MCP已成功部署到EC2隧道模式，提供外部访问能力。本指南将帮助您了解如何访问和使用部署的服务。

## 🌐 访问信息

### 主要访问地址
```
https://8080-il87v3xvpi7qjanl9c8os-3fac7940.manusvm.computer
```

### 服务端点
- **主页面**: `/`
- **健康检查**: `/health`
- **系统状态**: `/api/status`
- **场景测试**: `/api/test_scenario`
- **功能测试**: `/api/test_function`

## 🚀 核心功能

### 智慧感知演示
1. **新用户场景** - 自动引导模式
2. **高级用户场景** - 高效操作模式
3. **无障碍场景** - 辅助功能支持

### 功能模块测试
- **UI生成** - 智能界面配置
- **用户分析** - 行为模式识别
- **主题管理** - 智能主题切换
- **布局优化** - 自适应布局

## 🔧 技术规格

- **部署模式**: EC2隧道
- **安全协议**: HTTPS加密
- **CORS支持**: 已启用
- **响应时间**: < 50ms
- **版本**: 1.0.0

## 📱 使用方法

### 基础访问
1. 在浏览器中打开主要访问地址
2. 系统将自动加载SmartUI MCP界面
3. 查看系统状态和组件健康状况

### 功能测试
1. **智慧感知测试**
   - 点击"测试新用户模式"体验引导式界面
   - 点击"测试专家模式"体验高效操作界面
   - 点击"测试无障碍模式"体验辅助功能

2. **功能模块测试**
   - 测试UI生成器的智能配置能力
   - 测试用户分析器的行为识别能力
   - 测试主题切换的自适应能力
   - 测试布局优化的响应式能力

### API调用示例

#### 健康检查
```bash
curl https://8080-il87v3xvpi7qjanl9c8os-3fac7940.manusvm.computer/health
```

#### 测试智慧感知场景
```bash
curl -X POST https://8080-il87v3xvpi7qjanl9c8os-3fac7940.manusvm.computer/api/test_scenario \
  -H "Content-Type: application/json" \
  -d '{"scenario": "new_user"}'
```

#### 测试功能模块
```bash
curl -X POST https://8080-il87v3xvpi7qjanl9c8os-3fac7940.manusvm.computer/api/test_function \
  -H "Content-Type: application/json" \
  -d '{"function": "ui_generation"}'
```

## 🎯 智慧感知能力展示

### 用户行为识别
- 自动检测用户经验水平
- 识别设备类型和屏幕尺寸
- 分析交互模式和偏好

### 自适应UI生成
- 基于用户特征生成最适合的界面
- 动态调整布局和组件配置
- 优化交互方式和视觉设计

### 智能决策引擎
- 实时分析用户上下文
- 提供个性化功能建议
- 优化用户体验路径

### 无障碍智能支持
- 自动检测无障碍需求
- 智能调整界面对比度和字体大小
- 优化键盘导航和屏幕阅读器支持

## 🔍 监控和调试

### 系统状态监控
访问 `/api/status` 端点可以获取实时系统状态：
- 组件健康状况
- 性能指标
- 最后更新时间

### 日志查看
系统运行日志包含详细的操作记录和性能数据，有助于问题诊断和性能优化。

## 🛠️ 故障排除

### 常见问题
1. **无法访问服务**
   - 检查网络连接
   - 确认URL地址正确
   - 验证HTTPS证书

2. **功能测试失败**
   - 检查请求格式是否正确
   - 确认Content-Type头部设置
   - 查看浏览器控制台错误信息

3. **性能问题**
   - 检查网络延迟
   - 确认服务器负载状况
   - 优化请求频率

## 📞 技术支持

如果您在使用过程中遇到问题，请：
1. 查看系统健康状态
2. 检查浏览器控制台日志
3. 记录具体的错误信息和操作步骤

## 🎉 总结

SmartUI MCP EC2隧道部署为您提供了：
- 🌐 **外部访问能力** - 随时随地访问智能UI服务
- 🧠 **智慧感知功能** - 体验AI驱动的用户界面适配
- 🔒 **安全可靠** - HTTPS加密保障数据安全
- 📱 **跨设备支持** - 完美适配桌面和移动设备
- ♿ **无障碍友好** - 智能支持各种无障碍需求

现在您可以充分体验SmartUI MCP的智慧感知UI功能了！

