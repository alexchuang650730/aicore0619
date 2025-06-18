"""
PowerAutomation 测试管理 - 共享接口定义

这个模块定义了工作流层和适配器层之间的标准接口，
确保组件间的松耦合和高内聚。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class TestType(Enum):
    """测试类型枚举"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class ExecutionMode(Enum):
    """执行模式枚举"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


@dataclass
class TestCase:
    """测试用例数据模型"""
    id: str
    name: str
    description: str
    test_type: TestType
    module_name: str
    file_path: str
    function_name: str
    dependencies: List[str] = None
    timeout: int = 300
    priority: int = 1
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


@dataclass
class TestStrategy:
    """测试策略数据模型"""
    id: str
    name: str
    description: str
    target_modules: List[str]
    test_types: List[TestType]
    execution_mode: ExecutionMode
    max_workers: int = 4
    timeout: int = 3600
    retry_count: int = 3
    optimization_enabled: bool = True
    ai_recommendations: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.ai_recommendations is None:
            self.ai_recommendations = {}


@dataclass
class TestPlan:
    """测试计划数据模型"""
    id: str
    strategy_id: str
    test_cases: List[TestCase]
    execution_order: List[str]
    estimated_duration: int
    created_at: datetime
    created_by: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestResult:
    """单个测试结果数据模型"""
    test_case_id: str
    status: TestStatus
    duration: float
    start_time: datetime
    end_time: datetime
    output: str = ""
    error_message: str = ""
    stack_trace: str = ""
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


@dataclass
class ExecutionResult:
    """执行结果数据模型"""
    plan_id: str
    strategy_id: str
    status: TestStatus
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration: float
    start_time: datetime
    end_time: datetime
    test_results: List[TestResult]
    summary: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.summary is None:
            self.summary = {}
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100


@dataclass
class TestReport:
    """测试报告数据模型"""
    id: str
    execution_result: ExecutionResult
    generated_at: datetime
    report_type: str = "standard"
    format: str = "json"
    file_path: str = ""
    insights: Dict[str, Any] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.insights is None:
            self.insights = {}
        if self.recommendations is None:
            self.recommendations = []


class ITestStrategyGenerator(ABC):
    """测试策略生成器接口"""
    
    @abstractmethod
    async def generate_strategy(self, requirements: Dict[str, Any]) -> TestStrategy:
        """生成测试策略"""
        pass
    
    @abstractmethod
    async def optimize_strategy(self, strategy: TestStrategy, context: Dict[str, Any]) -> TestStrategy:
        """优化测试策略"""
        pass


class ITestPlanGenerator(ABC):
    """测试计划生成器接口"""
    
    @abstractmethod
    async def generate_plan(self, strategy: TestStrategy) -> TestPlan:
        """根据策略生成测试计划"""
        pass
    
    @abstractmethod
    async def validate_plan(self, plan: TestPlan) -> Dict[str, Any]:
        """验证测试计划"""
        pass


class ITestExecutor(ABC):
    """测试执行器接口"""
    
    @abstractmethod
    async def execute_plan(self, plan: TestPlan) -> ExecutionResult:
        """执行测试计划"""
        pass
    
    @abstractmethod
    async def execute_test_case(self, test_case: TestCase) -> TestResult:
        """执行单个测试用例"""
        pass
    
    @abstractmethod
    async def stop_execution(self, plan_id: str) -> bool:
        """停止测试执行"""
        pass


class ITestReporter(ABC):
    """测试报告生成器接口"""
    
    @abstractmethod
    async def generate_report(self, execution_result: ExecutionResult) -> TestReport:
        """生成测试报告"""
        pass
    
    @abstractmethod
    async def export_report(self, report: TestReport, format: str) -> str:
        """导出测试报告"""
        pass


class IWorkflowOrchestrator(ABC):
    """工作流编排器接口"""
    
    @abstractmethod
    async def orchestrate_test_workflow(self, strategy: TestStrategy) -> ExecutionResult:
        """编排测试工作流"""
        pass
    
    @abstractmethod
    async def monitor_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """监控工作流状态"""
        pass


class ITestManagerMCP(ABC):
    """测试管理器MCP主接口 - 工作流层"""
    
    @abstractmethod
    async def create_test_strategy(self, requirements: Dict[str, Any]) -> TestStrategy:
        """创建测试策略"""
        pass
    
    @abstractmethod
    async def execute_test_workflow(self, strategy: TestStrategy) -> ExecutionResult:
        """执行测试工作流"""
        pass
    
    @abstractmethod
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        pass
    
    @abstractmethod
    async def optimize_test_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """优化测试执行"""
        pass


class ITestExecutionEngine(ABC):
    """测试执行引擎主接口 - 适配器层"""
    
    @abstractmethod
    async def generate_test_frameworks(self, modules: List[str]) -> Dict[str, Any]:
        """生成测试框架"""
        pass
    
    @abstractmethod
    async def execute_tests(self, plan: TestPlan) -> ExecutionResult:
        """执行测试"""
        pass
    
    @abstractmethod
    async def fix_test_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """修复测试问题"""
        pass
    
    @abstractmethod
    async def generate_reports(self, execution_result: ExecutionResult) -> TestReport:
        """生成报告"""
        pass


class ICommunicationProtocol(ABC):
    """组件间通信协议接口"""
    
    @abstractmethod
    async def send_message(self, target: str, message: Dict[str, Any]) -> bool:
        """发送消息"""
        pass
    
    @abstractmethod
    async def receive_message(self, source: str) -> Optional[Dict[str, Any]]:
        """接收消息"""
        pass
    
    @abstractmethod
    async def broadcast_event(self, event: Dict[str, Any]) -> bool:
        """广播事件"""
        pass
    
    @abstractmethod
    async def subscribe_to_events(self, event_types: List[str]) -> bool:
        """订阅事件"""
        pass

