"""
PowerAutomation 测试管理 - 共享接口包初始化

导出所有共享接口、数据模型和通信协议。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

# 导入核心接口
from .test_interfaces import (
    # 枚举类型
    TestType,
    TestStatus,
    ExecutionMode,
    
    # 数据模型
    TestCase,
    TestStrategy,
    TestPlan,
    TestResult,
    ExecutionResult,
    TestReport,
    
    # 接口定义
    ITestStrategyGenerator,
    ITestPlanGenerator,
    ITestExecutor,
    ITestReporter,
    IWorkflowOrchestrator,
    ITestManagerMCP,
    ITestExecutionEngine,
    ICommunicationProtocol
)

# 导入扩展数据模型
from .data_models import (
    # 枚举类型
    Priority,
    Severity,
    
    # 数据模型
    ModuleInfo,
    TestConfiguration,
    TestMetrics,
    TestIssue,
    TestEnvironment,
    AIRecommendation,
    WorkflowStep,
    TestWorkflow,
    TestSession,
    TestSuite,
    
    # 工具函数
    DataModelEncoder,
    serialize_model,
    deserialize_model,
    validate_model,
    create_test_case_from_dict,
    create_test_strategy_from_dict
)

# 导入通信协议
from .communication import (
    # 枚举类型
    MessageType,
    EventType,
    
    # 数据模型
    Message,
    Event,
    
    # 通信组件
    MessageBus,
    CommunicationProtocol,
    WorkflowCommunicationAdapter,
    AdapterCommunicationAdapter,
    
    # 工具函数
    get_message_bus,
    create_workflow_adapter,
    create_adapter_communication
)

# 版本信息
__version__ = "1.0.0"
__author__ = "PowerAutomation Team"
__email__ = "team@powerautomation.com"

# 导出的公共接口
__all__ = [
    # 核心接口
    "TestType", "TestStatus", "ExecutionMode",
    "TestCase", "TestStrategy", "TestPlan", "TestResult", "ExecutionResult", "TestReport",
    "ITestStrategyGenerator", "ITestPlanGenerator", "ITestExecutor", "ITestReporter",
    "IWorkflowOrchestrator", "ITestManagerMCP", "ITestExecutionEngine", "ICommunicationProtocol",
    
    # 扩展数据模型
    "Priority", "Severity",
    "ModuleInfo", "TestConfiguration", "TestMetrics", "TestIssue", "TestEnvironment",
    "AIRecommendation", "WorkflowStep", "TestWorkflow", "TestSession", "TestSuite",
    "DataModelEncoder", "serialize_model", "deserialize_model", "validate_model",
    "create_test_case_from_dict", "create_test_strategy_from_dict",
    
    # 通信协议
    "MessageType", "EventType", "Message", "Event",
    "MessageBus", "CommunicationProtocol", "WorkflowCommunicationAdapter", "AdapterCommunicationAdapter",
    "get_message_bus", "create_workflow_adapter", "create_adapter_communication"
]


def get_interface_version() -> str:
    """获取接口版本"""
    return __version__


def get_supported_test_types() -> list:
    """获取支持的测试类型"""
    return [test_type.value for test_type in TestType]


def get_supported_execution_modes() -> list:
    """获取支持的执行模式"""
    return [mode.value for mode in ExecutionMode]


def create_default_test_configuration() -> TestConfiguration:
    """创建默认测试配置"""
    return TestConfiguration()


def create_default_test_environment() -> TestEnvironment:
    """创建默认测试环境"""
    return TestEnvironment(
        name="default",
        python_version="3.11",
        os_type="linux",
        architecture="x64"
    )


def validate_interface_compatibility(component_version: str) -> bool:
    """验证组件版本兼容性"""
    # 简单的版本兼容性检查
    try:
        major, minor, patch = component_version.split('.')
        interface_major, interface_minor, interface_patch = __version__.split('.')
        
        # 主版本必须相同
        if major != interface_major:
            return False
        
        # 次版本向后兼容
        if int(minor) < int(interface_minor):
            return False
        
        return True
    except (ValueError, AttributeError):
        return False


# 接口使用示例
def example_usage():
    """接口使用示例"""
    
    # 创建测试用例
    test_case = TestCase(
        id="test_001",
        name="示例测试用例",
        description="这是一个示例测试用例",
        test_type=TestType.UNIT,
        module_name="example_module",
        file_path="/path/to/test_file.py",
        function_name="test_example_function"
    )
    
    # 创建测试策略
    strategy = TestStrategy(
        id="strategy_001",
        name="示例测试策略",
        description="这是一个示例测试策略",
        target_modules=["module1", "module2"],
        test_types=[TestType.UNIT, TestType.INTEGRATION],
        execution_mode=ExecutionMode.PARALLEL,
        max_workers=4
    )
    
    # 创建测试计划
    plan = TestPlan(
        id="plan_001",
        strategy_id=strategy.id,
        test_cases=[test_case],
        execution_order=[test_case.id],
        estimated_duration=300,
        created_at=datetime.now(),
        created_by="system"
    )
    
    return {
        "test_case": test_case,
        "strategy": strategy,
        "plan": plan
    }


if __name__ == "__main__":
    # 运行示例
    from datetime import datetime
    
    print(f"PowerAutomation 测试管理接口 v{__version__}")
    print(f"支持的测试类型: {get_supported_test_types()}")
    print(f"支持的执行模式: {get_supported_execution_modes()}")
    
    # 创建示例
    examples = example_usage()
    print(f"创建了 {len(examples)} 个示例对象")
    
    # 序列化示例
    for name, obj in examples.items():
        serialized = serialize_model(obj)
        print(f"{name} 序列化长度: {len(serialized)} 字符")

