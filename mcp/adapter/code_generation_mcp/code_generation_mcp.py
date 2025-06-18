"""
代码生成工作流MCP - Code Generation Workflow MCP
专门处理代码生成相关的工作流任务
"""

import asyncio
import json
import uuid
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class CodeType(Enum):
    """代码类型枚举"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    API = "api"
    MOBILE = "mobile"
    SCRIPT = "script"
    TEST = "test"
    CONFIG = "config"

class Language(Enum):
    """编程语言枚举"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    SQL = "sql"
    HTML = "html"
    CSS = "css"

class Framework(Enum):
    """框架枚举"""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    FLASK = "flask"
    DJANGO = "django"
    FASTAPI = "fastapi"
    EXPRESS = "express"
    SPRING = "spring"
    DOTNET = "dotnet"

class CodeGenerationMcp:
    """代码生成工作流MCP"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "CodeGenerationMcp"
        self.module_name = "code_generation_mcp"
        self.module_type = "workflow_adapter"
        self.config = config or {}
        self.initialized = False
        self.version = "1.0.0"
        self.status = "inactive"
        
        # 代码生成管理
        self.generation_sessions: Dict[str, Dict[str, Any]] = {}
        self.generated_code: Dict[str, Dict[str, Any]] = {}
        self.operation_count = 0
        
        # 代码模板和规则
        self.code_templates = self._initialize_code_templates()
        self.generation_rules = self._initialize_generation_rules()
        
        # 性能统计
        self.performance_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "active_sessions": 0,
            "average_generation_time": 0.0,
            "code_quality_score": 0.0
        }

    def _initialize_code_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化代码模板"""
        return {
            "python_api": {
                "template": """
from flask import Flask, request, jsonify
from typing import Dict, Any

app = Flask(__name__)

@app.route('/{endpoint}', methods=['{method}'])
def {function_name}():
    \"\"\"
    {description}
    \"\"\"
    try:
        # 处理请求
        data = request.get_json() if request.method == 'POST' else request.args
        
        # 业务逻辑
        result = process_{function_name}(data)
        
        return jsonify({{"status": "success", "data": result}})
    except Exception as e:
        return jsonify({{"status": "error", "message": str(e)}}), 500

def process_{function_name}(data: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"处理业务逻辑\"\"\"
    # TODO: 实现具体业务逻辑
    return {{"message": "处理完成"}}

if __name__ == '__main__':
    app.run(debug=True)
""",
                "variables": ["endpoint", "method", "function_name", "description"]
            },
            "react_component": {
                "template": """
import React, {{ useState, useEffect }} from 'react';
import './{component_name}.css';

interface {component_name}Props {{
  {props_interface}
}}

const {component_name}: React.FC<{component_name}Props> = ({{ {props_destructure} }}) => {{
  const [state, setState] = useState({initial_state});

  useEffect(() => {{
    // 组件挂载时的逻辑
    {mount_logic}
  }}, []);

  const handle{action_name} = () => {{
    // 处理用户交互
    {action_logic}
  }};

  return (
    <div className="{component_name.lower()}">
      <h2>{title}</h2>
      {content_jsx}
    </div>
  );
}};

export default {component_name};
""",
                "variables": ["component_name", "props_interface", "props_destructure", 
                            "initial_state", "mount_logic", "action_name", "action_logic", 
                            "title", "content_jsx"]
            },
            "database_model": {
                "template": """
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {model_name}(Base):
    \"\"\"
    {description}
    \"\"\"
    __tablename__ = '{table_name}'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    {fields}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<{model_name}(id={{self.id}})>"
    
    def to_dict(self):
        \"\"\"转换为字典\"\"\"
        return {{
            'id': self.id,
            {to_dict_fields}
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}
""",
                "variables": ["model_name", "description", "table_name", "fields", "to_dict_fields"]
            }
        }

    def _initialize_generation_rules(self) -> Dict[str, List[str]]:
        """初始化生成规则"""
        return {
            "naming_conventions": [
                "使用有意义的变量和函数名",
                "遵循语言特定的命名规范",
                "避免使用缩写和模糊的名称"
            ],
            "code_structure": [
                "保持函数简洁，单一职责",
                "适当添加注释和文档字符串",
                "使用类型提示（如果语言支持）"
            ],
            "error_handling": [
                "添加适当的异常处理",
                "提供有意义的错误消息",
                "记录错误日志"
            ],
            "security": [
                "验证输入参数",
                "避免SQL注入和XSS攻击",
                "使用安全的加密方法"
            ]
        }

    async def initialize(self) -> bool:
        """初始化代码生成MCP"""
        try:
            self.initialized = True
            self.status = "active"
            return True
        except Exception as e:
            self.status = "error"
            return False

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理代码生成请求"""
        try:
            self.operation_count += 1
            
            request_type = data.get("type", "generate_code")
            
            if request_type == "generate_code":
                return await self._generate_code(data)
            elif request_type == "generate_from_requirements":
                return await self._generate_from_requirements(data)
            elif request_type == "refactor_code":
                return await self._refactor_code(data)
            elif request_type == "optimize_code":
                return await self._optimize_code(data)
            elif request_type == "generate_tests":
                return await self._generate_tests(data)
            elif request_type == "create_project_structure":
                return await self._create_project_structure(data)
            elif request_type == "start_generation_session":
                return await self._start_generation_session(data)
            elif request_type == "get_generation_status":
                return await self._get_generation_status(data)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown request type: {request_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _generate_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成代码"""
        code_type = data.get("code_type", "api")
        language = data.get("language", "python")
        framework = data.get("framework")
        specifications = data.get("specifications", {})
        
        generation_id = str(uuid.uuid4())
        
        # 选择合适的模板
        template_key = f"{language}_{code_type}"
        if template_key not in self.code_templates:
            template_key = f"{language}_api"  # 默认模板
        
        if template_key in self.code_templates:
            generated_code = await self._apply_template(
                self.code_templates[template_key], 
                specifications
            )
        else:
            generated_code = await self._generate_custom_code(
                code_type, language, framework, specifications
            )
        
        # 应用代码质量规则
        improved_code = await self._apply_quality_rules(generated_code, language)
        
        # 保存生成的代码
        code_info = {
            "generation_id": generation_id,
            "code_type": code_type,
            "language": language,
            "framework": framework,
            "specifications": specifications,
            "generated_code": improved_code,
            "created_time": datetime.now().isoformat(),
            "quality_score": await self._calculate_code_quality(improved_code, language)
        }
        
        self.generated_code[generation_id] = code_info
        self.performance_stats["total_generations"] += 1
        self.performance_stats["successful_generations"] += 1
        
        return {
            "status": "success",
            "generation_id": generation_id,
            "generated_code": improved_code,
            "code_info": {
                "type": code_type,
                "language": language,
                "framework": framework,
                "quality_score": code_info["quality_score"]
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _apply_template(self, template_info: Dict[str, Any], specifications: Dict[str, Any]) -> str:
        """应用代码模板"""
        template = template_info["template"]
        variables = template_info["variables"]
        
        # 填充模板变量
        for var in variables:
            value = specifications.get(var, f"TODO_{var.upper()}")
            template = template.replace(f"{{{var}}}", str(value))
        
        return template

    async def _generate_custom_code(self, code_type: str, language: str, 
                                  framework: str, specifications: Dict[str, Any]) -> str:
        """生成自定义代码"""
        # 这里实现自定义代码生成逻辑
        # 在实际实现中，可以使用AI模型或更复杂的代码生成器
        
        code_skeleton = f"""
# Generated {code_type} code in {language}
# Framework: {framework if framework else 'None'}
# Generated at: {datetime.now().isoformat()}

"""
        
        if language == "python":
            if code_type == "api":
                code_skeleton += """
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/endpoint', methods=['GET', 'POST'])
def api_endpoint():
    \"\"\"API端点\"\"\"
    return jsonify({"message": "Hello from generated API"})

if __name__ == '__main__':
    app.run(debug=True)
"""
            elif code_type == "script":
                code_skeleton += """
#!/usr/bin/env python3
\"\"\"
Generated script
\"\"\"

def main():
    \"\"\"主函数\"\"\"
    print("Generated script is running")

if __name__ == '__main__':
    main()
"""
        
        elif language == "javascript":
            if code_type == "frontend":
                code_skeleton += """
// Generated frontend JavaScript code

document.addEventListener('DOMContentLoaded', function() {
    console.log('Generated frontend code loaded');
    
    // TODO: Add your frontend logic here
});
"""
        
        return code_skeleton

    async def _apply_quality_rules(self, code: str, language: str) -> str:
        """应用代码质量规则"""
        improved_code = code
        
        # 添加基本的代码质量改进
        if language == "python":
            # 确保有适当的导入
            if "import" not in improved_code and "from" not in improved_code:
                improved_code = "# -*- coding: utf-8 -*-\n" + improved_code
            
            # 添加类型提示（简单示例）
            improved_code = improved_code.replace("def ", "def ")
        
        elif language == "javascript":
            # 添加严格模式
            if "'use strict'" not in improved_code:
                improved_code = "'use strict';\n\n" + improved_code
        
        return improved_code

    async def _calculate_code_quality(self, code: str, language: str) -> float:
        """计算代码质量分数"""
        score = 100.0
        
        # 基本质量检查
        lines = code.split('\n')
        
        # 检查注释比例
        comment_lines = 0
        code_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if language == "python" and line.startswith('#'):
                comment_lines += 1
            elif language == "javascript" and (line.startswith('//') or line.startswith('/*')):
                comment_lines += 1
            else:
                code_lines += 1
        
        if code_lines > 0:
            comment_ratio = comment_lines / code_lines
            if comment_ratio < 0.1:
                score -= 10  # 注释太少
            elif comment_ratio > 0.3:
                score += 5   # 注释充足
        
        # 检查函数长度
        if language == "python":
            function_lines = []
            current_function_lines = 0
            in_function = False
            
            for line in lines:
                if line.strip().startswith('def '):
                    if in_function:
                        function_lines.append(current_function_lines)
                    in_function = True
                    current_function_lines = 1
                elif in_function:
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                        function_lines.append(current_function_lines)
                        in_function = False
                        current_function_lines = 0
                    else:
                        current_function_lines += 1
            
            # 检查是否有过长的函数
            for func_len in function_lines:
                if func_len > 50:
                    score -= 5
        
        return max(0.0, min(100.0, score))

    async def _generate_from_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从需求生成代码"""
        requirements = data.get("requirements", [])
        target_language = data.get("language", "python")
        target_framework = data.get("framework")
        
        generated_components = []
        
        for req in requirements:
            req_type = req.get("type", "functional")
            req_description = req.get("description", "")
            
            # 根据需求类型生成相应的代码组件
            if "API" in req_description or "接口" in req_description:
                component = await self._generate_api_from_requirement(req, target_language)
            elif "数据库" in req_description or "database" in req_description.lower():
                component = await self._generate_model_from_requirement(req, target_language)
            elif "界面" in req_description or "UI" in req_description:
                component = await self._generate_ui_from_requirement(req, target_language)
            else:
                component = await self._generate_generic_from_requirement(req, target_language)
            
            generated_components.append(component)
        
        return {
            "status": "success",
            "generated_components": generated_components,
            "total_components": len(generated_components),
            "target_language": target_language,
            "target_framework": target_framework,
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_api_from_requirement(self, requirement: Dict[str, Any], language: str) -> Dict[str, Any]:
        """从需求生成API代码"""
        req_id = requirement.get("req_id", str(uuid.uuid4()))
        description = requirement.get("description", "")
        
        # 简单的API生成逻辑
        endpoint_name = requirement.get("title", "api_endpoint").lower().replace(" ", "_")
        
        if language == "python":
            api_code = f"""
@app.route('/api/{endpoint_name}', methods=['GET', 'POST'])
def {endpoint_name}():
    \"\"\"
    {description}
    \"\"\"
    try:
        if request.method == 'POST':
            data = request.get_json()
            # TODO: 处理POST请求数据
            result = process_{endpoint_name}_post(data)
        else:
            # TODO: 处理GET请求
            result = process_{endpoint_name}_get()
        
        return jsonify({{"status": "success", "data": result}})
    except Exception as e:
        return jsonify({{"status": "error", "message": str(e)}}), 500

def process_{endpoint_name}_post(data):
    \"\"\"处理POST请求\"\"\"
    # TODO: 实现具体逻辑
    return {{"message": "POST处理完成"}}

def process_{endpoint_name}_get():
    \"\"\"处理GET请求\"\"\"
    # TODO: 实现具体逻辑
    return {{"message": "GET处理完成"}}
"""
        else:
            api_code = f"// TODO: 生成{language}的API代码"
        
        return {
            "component_type": "api",
            "requirement_id": req_id,
            "endpoint_name": endpoint_name,
            "generated_code": api_code,
            "language": language
        }

    async def _generate_model_from_requirement(self, requirement: Dict[str, Any], language: str) -> Dict[str, Any]:
        """从需求生成数据模型代码"""
        req_id = requirement.get("req_id", str(uuid.uuid4()))
        description = requirement.get("description", "")
        
        model_name = requirement.get("title", "DataModel").replace(" ", "")
        
        if language == "python":
            model_code = f"""
class {model_name}(Base):
    \"\"\"
    {description}
    \"\"\"
    __tablename__ = '{model_name.lower()}'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<{model_name}(id={{self.id}}, name={{self.name}})>"
    
    def to_dict(self):
        return {{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}
"""
        else:
            model_code = f"// TODO: 生成{language}的数据模型代码"
        
        return {
            "component_type": "model",
            "requirement_id": req_id,
            "model_name": model_name,
            "generated_code": model_code,
            "language": language
        }

    async def _generate_ui_from_requirement(self, requirement: Dict[str, Any], language: str) -> Dict[str, Any]:
        """从需求生成UI代码"""
        req_id = requirement.get("req_id", str(uuid.uuid4()))
        description = requirement.get("description", "")
        
        component_name = requirement.get("title", "UIComponent").replace(" ", "")
        
        if language == "javascript" or language == "typescript":
            ui_code = f"""
import React, {{ useState }} from 'react';

const {component_name} = () => {{
    const [data, setData] = useState(null);
    
    // {description}
    
    return (
        <div className="{component_name.lower()}">
            <h2>{component_name}</h2>
            <p>{description}</p>
            {{/* TODO: 添加具体的UI元素 */}}
        </div>
    );
}};

export default {component_name};
"""
        else:
            ui_code = f"<!-- TODO: 生成{language}的UI代码 -->"
        
        return {
            "component_type": "ui",
            "requirement_id": req_id,
            "component_name": component_name,
            "generated_code": ui_code,
            "language": language
        }

    async def _generate_generic_from_requirement(self, requirement: Dict[str, Any], language: str) -> Dict[str, Any]:
        """从需求生成通用代码"""
        req_id = requirement.get("req_id", str(uuid.uuid4()))
        description = requirement.get("description", "")
        
        function_name = requirement.get("title", "generic_function").lower().replace(" ", "_")
        
        if language == "python":
            generic_code = f"""
def {function_name}():
    \"\"\"
    {description}
    \"\"\"
    # TODO: 实现具体功能
    pass
"""
        elif language == "javascript":
            generic_code = f"""
function {function_name}() {{
    // {description}
    // TODO: 实现具体功能
}}
"""
        else:
            generic_code = f"// TODO: 生成{language}的通用代码"
        
        return {
            "component_type": "generic",
            "requirement_id": req_id,
            "function_name": function_name,
            "generated_code": generic_code,
            "language": language
        }

    async def _refactor_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """重构代码"""
        original_code = data.get("code", "")
        language = data.get("language", "python")
        refactor_type = data.get("refactor_type", "improve_readability")
        
        refactored_code = await self._apply_refactoring_rules(original_code, language, refactor_type)
        
        return {
            "status": "success",
            "original_code": original_code,
            "refactored_code": refactored_code,
            "refactor_type": refactor_type,
            "language": language,
            "improvements": await self._identify_improvements(original_code, refactored_code),
            "timestamp": datetime.now().isoformat()
        }

    async def _apply_refactoring_rules(self, code: str, language: str, refactor_type: str) -> str:
        """应用重构规则"""
        refactored = code
        
        if refactor_type == "improve_readability":
            # 改善可读性
            if language == "python":
                # 添加空行分隔逻辑块
                lines = refactored.split('\n')
                improved_lines = []
                for i, line in enumerate(lines):
                    improved_lines.append(line)
                    if line.strip().startswith('def ') and i < len(lines) - 1:
                        if lines[i + 1].strip() and not lines[i + 1].startswith(' '):
                            improved_lines.append('')
                refactored = '\n'.join(improved_lines)
        
        elif refactor_type == "extract_functions":
            # 提取函数（简单示例）
            if language == "python" and len(code.split('\n')) > 20:
                refactored = "# TODO: 提取长函数为多个小函数\n" + refactored
        
        return refactored

    async def _identify_improvements(self, original: str, refactored: str) -> List[str]:
        """识别改进点"""
        improvements = []
        
        if len(refactored.split('\n')) > len(original.split('\n')):
            improvements.append("添加了空行以改善可读性")
        
        if "TODO" in refactored and "TODO" not in original:
            improvements.append("添加了TODO注释以标识需要进一步改进的地方")
        
        return improvements

    async def _optimize_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """优化代码性能"""
        original_code = data.get("code", "")
        language = data.get("language", "python")
        optimization_type = data.get("optimization_type", "performance")
        
        optimized_code = await self._apply_optimization_rules(original_code, language, optimization_type)
        
        return {
            "status": "success",
            "original_code": original_code,
            "optimized_code": optimized_code,
            "optimization_type": optimization_type,
            "language": language,
            "optimizations_applied": await self._identify_optimizations(original_code, optimized_code),
            "timestamp": datetime.now().isoformat()
        }

    async def _apply_optimization_rules(self, code: str, language: str, optimization_type: str) -> str:
        """应用优化规则"""
        optimized = code
        
        if optimization_type == "performance":
            if language == "python":
                # 简单的性能优化示例
                if "for i in range(len(" in optimized:
                    optimized = "# 建议使用enumerate()而不是range(len())\n" + optimized
        
        return optimized

    async def _identify_optimizations(self, original: str, optimized: str) -> List[str]:
        """识别优化点"""
        optimizations = []
        
        if "enumerate()" in optimized and "enumerate()" not in original:
            optimizations.append("建议使用enumerate()优化循环")
        
        return optimizations

    async def _generate_tests(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试代码"""
        target_code = data.get("code", "")
        language = data.get("language", "python")
        test_type = data.get("test_type", "unit")
        
        test_code = await self._generate_test_code(target_code, language, test_type)
        
        return {
            "status": "success",
            "target_code": target_code,
            "test_code": test_code,
            "test_type": test_type,
            "language": language,
            "test_framework": await self._get_test_framework(language),
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_test_code(self, target_code: str, language: str, test_type: str) -> str:
        """生成测试代码"""
        if language == "python":
            test_code = f"""
import unittest
from unittest.mock import patch, MagicMock

class TestGeneratedCode(unittest.TestCase):
    \"\"\"
    生成的测试代码
    \"\"\"
    
    def setUp(self):
        \"\"\"测试设置\"\"\"
        pass
    
    def tearDown(self):
        \"\"\"测试清理\"\"\"
        pass
    
    def test_basic_functionality(self):
        \"\"\"测试基本功能\"\"\"
        # TODO: 添加具体的测试逻辑
        self.assertTrue(True)
    
    def test_error_handling(self):
        \"\"\"测试错误处理\"\"\"
        # TODO: 测试异常情况
        pass

if __name__ == '__main__':
    unittest.main()
"""
        elif language == "javascript":
            test_code = f"""
const {{ expect }} = require('chai');
const {{ describe, it, beforeEach, afterEach }} = require('mocha');

describe('Generated Code Tests', () => {{
    beforeEach(() => {{
        // 测试设置
    }});
    
    afterEach(() => {{
        // 测试清理
    }});
    
    it('should test basic functionality', () => {{
        // TODO: 添加具体的测试逻辑
        expect(true).to.be.true;
    }});
    
    it('should handle errors properly', () => {{
        // TODO: 测试错误处理
    }});
}});
"""
        else:
            test_code = f"// TODO: 生成{language}的测试代码"
        
        return test_code

    async def _get_test_framework(self, language: str) -> str:
        """获取推荐的测试框架"""
        frameworks = {
            "python": "unittest/pytest",
            "javascript": "mocha/chai",
            "typescript": "jest",
            "java": "junit",
            "csharp": "nunit"
        }
        return frameworks.get(language, "unknown")

    async def _create_project_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目结构"""
        project_name = data.get("project_name", "new_project")
        project_type = data.get("project_type", "web_app")
        language = data.get("language", "python")
        framework = data.get("framework")
        
        structure = await self._generate_project_structure(project_name, project_type, language, framework)
        
        return {
            "status": "success",
            "project_name": project_name,
            "project_type": project_type,
            "language": language,
            "framework": framework,
            "structure": structure,
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_project_structure(self, name: str, project_type: str, language: str, framework: str) -> Dict[str, Any]:
        """生成项目结构"""
        structure = {
            "directories": [],
            "files": {},
            "commands": []
        }
        
        if language == "python" and framework == "flask":
            structure["directories"] = [
                f"{name}/",
                f"{name}/app/",
                f"{name}/app/models/",
                f"{name}/app/views/",
                f"{name}/app/static/",
                f"{name}/app/templates/",
                f"{name}/tests/",
                f"{name}/config/"
            ]
            
            structure["files"] = {
                f"{name}/app/__init__.py": "# Flask应用初始化",
                f"{name}/app/models/__init__.py": "# 数据模型",
                f"{name}/app/views/__init__.py": "# 视图函数",
                f"{name}/requirements.txt": "flask\nflask-sqlalchemy\nflask-migrate",
                f"{name}/run.py": "# 应用启动文件",
                f"{name}/config.py": "# 配置文件",
                f"{name}/README.md": f"# {name}\n\nFlask应用项目"
            }
            
            structure["commands"] = [
                f"cd {name}",
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "python run.py"
            ]
        
        elif language == "javascript" and framework == "react":
            structure["directories"] = [
                f"{name}/",
                f"{name}/src/",
                f"{name}/src/components/",
                f"{name}/src/pages/",
                f"{name}/src/utils/",
                f"{name}/public/",
                f"{name}/tests/"
            ]
            
            structure["files"] = {
                f"{name}/package.json": "# React项目配置",
                f"{name}/src/App.js": "# 主应用组件",
                f"{name}/src/index.js": "# 应用入口",
                f"{name}/public/index.html": "# HTML模板",
                f"{name}/README.md": f"# {name}\n\nReact应用项目"
            }
            
            structure["commands"] = [
                f"cd {name}",
                "npm install",
                "npm start"
            ]
        
        return structure

    async def _start_generation_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """开始代码生成会话"""
        session_id = data.get("session_id", str(uuid.uuid4()))
        session_type = data.get("session_type", "code_generation")
        
        session_data = {
            "session_id": session_id,
            "session_type": session_type,
            "status": "active",
            "created_time": datetime.now().isoformat(),
            "generated_code": {},
            "current_language": data.get("language", "python"),
            "current_framework": data.get("framework")
        }
        
        self.generation_sessions[session_id] = session_data
        self.performance_stats["active_sessions"] = len(self.generation_sessions)
        
        return {
            "status": "success",
            "session_id": session_id,
            "session_data": session_data,
            "timestamp": datetime.now().isoformat()
        }

    async def _get_generation_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """获取生成状态"""
        session_id = data.get("session_id")
        
        if session_id and session_id in self.generation_sessions:
            session_data = self.generation_sessions[session_id]
            return {
                "status": "success",
                "session_data": session_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": "Generation session not found",
                "timestamp": datetime.now().isoformat()
            }

    async def get_status(self) -> Dict[str, Any]:
        """获取MCP状态"""
        return {
            "name": self.name,
            "module_name": self.module_name,
            "type": self.module_type,
            "initialized": self.initialized,
            "status": self.status,
            "version": self.version,
            "operation_count": self.operation_count,
            "total_generated": len(self.generated_code),
            "active_sessions": len(self.generation_sessions),
            "performance_stats": self.performance_stats,
            "timestamp": datetime.now().isoformat()
        }

    def get_info(self) -> Dict[str, Any]:
        """获取模块信息"""
        return {
            "name": self.name,
            "module_name": self.module_name,
            "type": self.module_type,
            "version": self.version,
            "description": "Code Generation Workflow MCP for automated code generation",
            "capabilities": [
                "generate_code", "generate_from_requirements", "refactor_code",
                "optimize_code", "generate_tests", "create_project_structure",
                "start_generation_session", "get_generation_status"
            ],
            "supported_code_types": [ct.value for ct in CodeType],
            "supported_languages": [lang.value for lang in Language],
            "supported_frameworks": [fw.value for fw in Framework]
        }

    async def cleanup(self) -> bool:
        """清理资源"""
        try:
            self.generation_sessions.clear()
            self.status = "inactive"
            return True
        except Exception:
            return False

# 为了兼容性，也导出原始名称
Codegenerationmcp = CodeGenerationMcp

