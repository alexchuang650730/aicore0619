"""
PowerAutomation 测试管理 - 数据模型

统一的数据模型定义，确保工作流层和适配器层使用一致的数据结构。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
import uuid


class Priority(Enum):
    """优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Severity(Enum):
    """严重程度枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ModuleInfo:
    """模块信息数据模型"""
    name: str
    path: str
    type: str  # adapter, workflow, coordinator
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    test_coverage: float = 0.0
    last_modified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestConfiguration:
    """测试配置数据模型"""
    timeout: int = 300
    retry_count: int = 3
    parallel_workers: int = 4
    memory_limit: int = 1024  # MB
    cpu_limit: float = 1.0
    environment_variables: Dict[str, str] = field(default_factory=dict)
    setup_commands: List[str] = field(default_factory=list)
    teardown_commands: List[str] = field(default_factory=list)


@dataclass
class TestMetrics:
    """测试指标数据模型"""
    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    coverage_percentage: float = 0.0
    assertions_count: int = 0
    lines_covered: int = 0
    lines_total: int = 0
    complexity_score: float = 0.0
    performance_score: float = 0.0


@dataclass
class TestIssue:
    """测试问题数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_case_id: str = ""
    issue_type: str = ""  # syntax_error, import_error, assertion_error, etc.
    severity: Severity = Severity.ERROR
    message: str = ""
    file_path: str = ""
    line_number: int = 0
    suggested_fix: str = ""
    auto_fixable: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TestEnvironment:
    """测试环境数据模型"""
    name: str
    python_version: str
    os_type: str
    architecture: str
    installed_packages: Dict[str, str] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    resource_limits: TestConfiguration = field(default_factory=TestConfiguration)


@dataclass
class AIRecommendation:
    """AI推荐数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""  # optimization, test_case, strategy, etc.
    title: str = ""
    description: str = ""
    confidence_score: float = 0.0
    impact_score: float = 0.0
    implementation_effort: Priority = Priority.MEDIUM
    suggested_actions: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowStep:
    """工作流步骤数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    step_type: str = ""  # generate, execute, fix, report, etc.
    dependencies: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    estimated_duration: int = 0
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestWorkflow:
    """测试工作流数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    strategy_id: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    status: str = "created"
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSession:
    """测试会话数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    environment: TestEnvironment = field(default_factory=lambda: TestEnvironment("default", "3.11", "linux", "x64"))
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "active"
    test_results: List[str] = field(default_factory=list)  # Test result IDs
    issues: List[TestIssue] = field(default_factory=list)
    metrics: TestMetrics = field(default_factory=TestMetrics)


@dataclass
class TestSuite:
    """测试套件数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    module_info: ModuleInfo = None
    test_cases: List[str] = field(default_factory=list)  # Test case IDs
    configuration: TestConfiguration = field(default_factory=TestConfiguration)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class DataModelEncoder(json.JSONEncoder):
    """数据模型JSON编码器"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def serialize_model(model: Any) -> str:
    """序列化数据模型为JSON字符串"""
    return json.dumps(model, cls=DataModelEncoder, indent=2)


def deserialize_model(json_str: str, model_class: type) -> Any:
    """从JSON字符串反序列化数据模型"""
    data = json.loads(json_str)
    return model_class(**data)


def validate_model(model: Any) -> List[str]:
    """验证数据模型的完整性"""
    errors = []
    
    # 基本验证逻辑
    if hasattr(model, 'id') and not model.id:
        errors.append("ID不能为空")
    
    if hasattr(model, 'name') and not model.name:
        errors.append("名称不能为空")
    
    # 可以根据需要添加更多验证规则
    
    return errors


def create_test_case_from_dict(data: Dict[str, Any]) -> 'TestCase':
    """从字典创建TestCase对象"""
    from .test_interfaces import TestCase, TestType
    
    return TestCase(
        id=data.get('id', str(uuid.uuid4())),
        name=data.get('name', ''),
        description=data.get('description', ''),
        test_type=TestType(data.get('test_type', 'unit')),
        module_name=data.get('module_name', ''),
        file_path=data.get('file_path', ''),
        function_name=data.get('function_name', ''),
        dependencies=data.get('dependencies', []),
        timeout=data.get('timeout', 300),
        priority=data.get('priority', 1),
        tags=data.get('tags', [])
    )


def create_test_strategy_from_dict(data: Dict[str, Any]) -> 'TestStrategy':
    """从字典创建TestStrategy对象"""
    from .test_interfaces import TestStrategy, TestType, ExecutionMode
    
    return TestStrategy(
        id=data.get('id', str(uuid.uuid4())),
        name=data.get('name', ''),
        description=data.get('description', ''),
        target_modules=data.get('target_modules', []),
        test_types=[TestType(t) for t in data.get('test_types', ['unit'])],
        execution_mode=ExecutionMode(data.get('execution_mode', 'parallel')),
        max_workers=data.get('max_workers', 4),
        timeout=data.get('timeout', 3600),
        retry_count=data.get('retry_count', 3),
        optimization_enabled=data.get('optimization_enabled', True),
        ai_recommendations=data.get('ai_recommendations', {})
    )

