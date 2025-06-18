    async def execute(self, action: str, query: str = "", context: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        self.logger.info(f"Smart Search action: {action}, query: {query}")
        if action == "find_tool":
            # 智能工具选择逻辑
            tool_id = self._select_tool_by_context(query, context)
            return {"tool_id": tool_id, "tool_params": {}}
        else:
            return {"status": "failure", "message": f"Unknown action: {action}"}
    
    def _select_tool_by_context(self, query: str, context: Optional[Any] = None) -> str:
        """根据查询和上下文智能选择工具"""
        # 获取上下文中的任务类型和内容
        task_type = ""
        content = ""
        
        if context and isinstance(context, dict):
            processed_data = context.get("processed_data", {})
            task_type = processed_data.get("type", "")
            content = processed_data.get("content", "")
        
        # 组合查询文本
        full_text = f"{task_type} {content} {query}".lower()
        
        # 代码生成相关任务 → kilocode_mcp
        code_keywords = ["code", "代码", "生成", "ppt", "文档", "document", "generate", "create", "编程", "python", "javascript", "html", "css"]
        if any(keyword in full_text for keyword in code_keywords):
            self.logger.info(f"选择kilocode_mcp: 检测到代码/生成任务")
            return "kilocode_mcp"
        
        # UI测试相关任务 → playwright_mcp  
        ui_keywords = ["ui", "test", "测试", "界面", "点击", "click", "browser", "浏览器", "automation", "自动化"]
        if any(keyword in full_text for keyword in ui_keywords):
            self.logger.info(f"选择playwright_mcp: 检测到UI/测试任务")
            return "playwright_mcp"
        
        # 默认选择kilocode_mcp作为兜底
        self.logger.info(f"默认选择kilocode_mcp: 未匹配特定任务类型")
        return "kilocode_mcp"

