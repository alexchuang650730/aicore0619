#!/usr/bin/env python3
"""
智慧路由系统分析报告

基于PowerAutomation智慧路由系统的分析，为Cloud Edge Data MCP重构提供参考。

分析来源: https://github.com/alexchuang650730/powerauto.ai_0.53/blob/66077d84ee59a3273e7f5bdebd51dad48e9bcc60/shared_core/engines/smart_routing_system.py
"""

# ============================================================================
# 1. 智慧路由系统核心架构分析
# ============================================================================

"""
从PowerAutomation智慧路由系统代码分析得出的核心架构：

1. SmartRouter类 - 核心路由决策引擎
   - route_request(): 主要路由决策方法
   - _make_routing_decision(): 核心决策算法
   - 支持隐私级别、复杂度、本地能力评估

2. 路由决策流程：
   Step 1: 分析请求特征
   - privacy_level = privacy_classifier.classify_sensitivity(user_request)
   - task_type = interaction_manager.classify_interaction(user_request)
   - complexity = complexity_analyzer.analyze_complexity(user_request, task_type)
   
   Step 2: 评估本地处理能力
   - local_capability = capability_assessor.assess_local_capability(task_type, complexity)
   
   Step 3: 计算成本
   - input_tokens, output_tokens = cost_calculator.estimate_tokens(user_request)
   - cloud_cost = cost_calculator.calculate_cloud_cost(input_tokens, output_tokens)
   - local_cost = cost_calculator.calculate_local_cost(30)  # 假设30秒处理时间
   
   Step 4: 路由决策逻辑
   - decision = _make_routing_decision(privacy_level, complexity, local_capability, 
                                      cloud_cost, local_cost, input_tokens + output_tokens)
   
   Step 5: 记录决策
   - _log_routing_decision(decision, user_request, context)

3. 决策算法核心逻辑：
   - 隐私敏感度优先：高敏感度优先本地处理
   - 本地能力评估：能力不足时转云端
   - 成本效益分析：平衡处理成本和质量
   - Token数量限制：大任务优先云端处理
"""

# ============================================================================
# 2. 路由决策枚举和数据结构
# ============================================================================

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

class RoutingDecision(Enum):
    """路由决策结果"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    HYBRID_LOCAL_FIRST = "hybrid_local_first"
    HYBRID_CLOUD_FIRST = "hybrid_cloud_first"
    LOAD_BALANCED = "load_balanced"

class PrivacySensitivity(Enum):
    """隐私敏感度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class ProcessingLocation(Enum):
    """处理位置"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    HYBRID = "hybrid"

@dataclass
class RoutingContext:
    """路由上下文"""
    user_request: str
    task_type: str
    privacy_level: PrivacySensitivity
    complexity: TaskComplexity
    local_capability: float  # 0.0-1.0
    cloud_cost: float
    local_cost: float
    estimated_tokens: int
    user_preferences: Dict[str, Any] = None
    system_load: Dict[str, float] = None

@dataclass
class RoutingResult:
    """路由结果"""
    decision: RoutingDecision
    processing_location: ProcessingLocation
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_time: float
    fallback_options: List[RoutingDecision] = None
    metadata: Dict[str, Any] = None

# ============================================================================
# 3. 智慧路由决策算法重构
# ============================================================================

class EnhancedSmartRouter:
    """
    增强版智慧路由器
    
    基于PowerAutomation智慧路由系统，针对OCR和MCP场景优化
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.routing_stats = {
            "total_requests": 0,
            "local_decisions": 0,
            "cloud_decisions": 0,
            "hybrid_decisions": 0,
            "average_confidence": 0.0
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "privacy_weight": 0.4,
            "cost_weight": 0.3,
            "performance_weight": 0.2,
            "capability_weight": 0.1,
            "local_capability_threshold": 0.7,
            "cost_sensitivity": 1.0,
            "privacy_enforcement": True,
            "load_balancing_enabled": True,
            "fallback_enabled": True
        }
    
    def route_request(self, context: RoutingContext) -> RoutingResult:
        """
        路由请求决策
        
        Args:
            context: 路由上下文
            
        Returns:
            路由决策结果
        """
        
        # 更新统计
        self.routing_stats["total_requests"] += 1
        
        # 执行决策算法
        decision = self._make_routing_decision(context)
        
        # 计算置信度
        confidence = self._calculate_confidence(context, decision)
        
        # 生成推理说明
        reasoning = self._generate_reasoning(context, decision)
        
        # 估算成本和时间
        estimated_cost, estimated_time = self._estimate_cost_and_time(context, decision)
        
        # 生成备选方案
        fallback_options = self._generate_fallback_options(context, decision)
        
        # 更新统计
        self._update_stats(decision, confidence)
        
        result = RoutingResult(
            decision=decision,
            processing_location=self._decision_to_location(decision),
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            fallback_options=fallback_options,
            metadata={
                "context": context,
                "config": self.config,
                "timestamp": time.time()
            }
        )
        
        return result
    
    def _make_routing_decision(self, context: RoutingContext) -> RoutingDecision:
        """
        核心路由决策算法
        
        基于PowerAutomation的决策逻辑，结合OCR场景特点
        """
        
        # 1. 隐私优先规则
        if context.privacy_level == PrivacySensitivity.CRITICAL:
            if context.local_capability >= 0.5:  # 降低门槛，优先本地
                return RoutingDecision.LOCAL_ONLY
            else:
                # 即使本地能力不足，也要尝试本地处理
                return RoutingDecision.HYBRID_LOCAL_FIRST
        
        if context.privacy_level == PrivacySensitivity.HIGH:
            if context.local_capability >= self.config["local_capability_threshold"]:
                return RoutingDecision.LOCAL_ONLY
            else:
                return RoutingDecision.HYBRID_LOCAL_FIRST
        
        # 2. 本地能力评估
        if context.local_capability < 0.3:
            # 本地能力严重不足，直接云端
            return RoutingDecision.CLOUD_ONLY
        
        # 3. 成本效益分析
        cost_ratio = context.cloud_cost / max(context.local_cost, 0.001)
        
        if cost_ratio > 10:  # 云端成本过高
            if context.local_capability >= 0.5:
                return RoutingDecision.LOCAL_ONLY
            else:
                return RoutingDecision.HYBRID_LOCAL_FIRST
        
        # 4. 复杂度和Token数量考虑
        if context.complexity == TaskComplexity.VERY_COMPLEX or context.estimated_tokens > 10000:
            if context.local_capability >= 0.8:
                return RoutingDecision.HYBRID_LOCAL_FIRST
            else:
                return RoutingDecision.CLOUD_ONLY
        
        # 5. 负载均衡决策
        if self.config["load_balancing_enabled"]:
            local_load = context.system_load.get("local", 0.5) if context.system_load else 0.5
            cloud_load = context.system_load.get("cloud", 0.5) if context.system_load else 0.5
            
            if local_load < 0.3 and context.local_capability >= 0.6:
                return RoutingDecision.LOCAL_ONLY
            elif cloud_load < 0.3:
                return RoutingDecision.CLOUD_ONLY
            else:
                return RoutingDecision.LOAD_BALANCED
        
        # 6. 默认混合策略
        if context.local_capability >= 0.7:
            return RoutingDecision.HYBRID_LOCAL_FIRST
        else:
            return RoutingDecision.HYBRID_CLOUD_FIRST
    
    def _calculate_confidence(self, context: RoutingContext, decision: RoutingDecision) -> float:
        """计算决策置信度"""
        
        confidence_factors = []
        
        # 隐私匹配度
        if context.privacy_level == PrivacySensitivity.CRITICAL:
            if decision in [RoutingDecision.LOCAL_ONLY, RoutingDecision.HYBRID_LOCAL_FIRST]:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.3)
        
        # 能力匹配度
        if decision == RoutingDecision.LOCAL_ONLY:
            confidence_factors.append(context.local_capability)
        elif decision == RoutingDecision.CLOUD_ONLY:
            confidence_factors.append(0.9)  # 假设云端能力很强
        else:
            confidence_factors.append((context.local_capability + 0.9) / 2)
        
        # 成本合理性
        cost_ratio = context.cloud_cost / max(context.local_cost, 0.001)
        if cost_ratio < 2:
            confidence_factors.append(0.8)
        elif cost_ratio < 5:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # 复杂度匹配
        if context.complexity == TaskComplexity.SIMPLE:
            if decision in [RoutingDecision.LOCAL_ONLY, RoutingDecision.HYBRID_LOCAL_FIRST]:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.6)
        elif context.complexity == TaskComplexity.VERY_COMPLEX:
            if decision in [RoutingDecision.CLOUD_ONLY, RoutingDecision.HYBRID_CLOUD_FIRST]:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.7)
        
        # 计算加权平均
        return sum(confidence_factors) / len(confidence_factors)
    
    def _generate_reasoning(self, context: RoutingContext, decision: RoutingDecision) -> str:
        """生成决策推理说明"""
        
        reasons = []
        
        # 隐私考虑
        if context.privacy_level in [PrivacySensitivity.HIGH, PrivacySensitivity.CRITICAL]:
            reasons.append(f"隐私级别为{context.privacy_level.value}，优先考虑本地处理")
        
        # 能力评估
        if context.local_capability < 0.5:
            reasons.append(f"本地处理能力较低({context.local_capability:.2f})，需要云端支持")
        elif context.local_capability > 0.8:
            reasons.append(f"本地处理能力较强({context.local_capability:.2f})，可以本地处理")
        
        # 成本分析
        cost_ratio = context.cloud_cost / max(context.local_cost, 0.001)
        if cost_ratio > 5:
            reasons.append(f"云端成本过高(云端/本地={cost_ratio:.1f}倍)，优先本地处理")
        elif cost_ratio < 2:
            reasons.append(f"云端成本合理(云端/本地={cost_ratio:.1f}倍)，可以考虑云端处理")
        
        # 复杂度考虑
        if context.complexity == TaskComplexity.VERY_COMPLEX:
            reasons.append("任务复杂度很高，建议使用云端高性能模型")
        elif context.complexity == TaskComplexity.SIMPLE:
            reasons.append("任务复杂度较低，本地处理即可满足需求")
        
        # Token数量
        if context.estimated_tokens > 10000:
            reasons.append(f"Token数量较大({context.estimated_tokens})，云端处理更高效")
        
        return "; ".join(reasons) if reasons else "基于综合评估的平衡决策"
    
    def _estimate_cost_and_time(self, context: RoutingContext, decision: RoutingDecision) -> tuple:
        """估算成本和时间"""
        
        if decision == RoutingDecision.LOCAL_ONLY:
            return context.local_cost, 30.0  # 假设本地处理30秒
        elif decision == RoutingDecision.CLOUD_ONLY:
            return context.cloud_cost, 10.0  # 假设云端处理10秒
        else:
            # 混合处理
            hybrid_cost = context.local_cost * 0.3 + context.cloud_cost * 0.7
            hybrid_time = 20.0  # 假设混合处理20秒
            return hybrid_cost, hybrid_time
    
    def _generate_fallback_options(self, context: RoutingContext, 
                                 primary_decision: RoutingDecision) -> List[RoutingDecision]:
        """生成备选方案"""
        
        fallbacks = []
        
        if primary_decision == RoutingDecision.LOCAL_ONLY:
            if context.privacy_level != PrivacySensitivity.CRITICAL:
                fallbacks.append(RoutingDecision.HYBRID_LOCAL_FIRST)
                fallbacks.append(RoutingDecision.CLOUD_ONLY)
        
        elif primary_decision == RoutingDecision.CLOUD_ONLY:
            if context.local_capability >= 0.5:
                fallbacks.append(RoutingDecision.HYBRID_CLOUD_FIRST)
                fallbacks.append(RoutingDecision.LOCAL_ONLY)
        
        elif primary_decision in [RoutingDecision.HYBRID_LOCAL_FIRST, RoutingDecision.HYBRID_CLOUD_FIRST]:
            fallbacks.append(RoutingDecision.LOCAL_ONLY)
            fallbacks.append(RoutingDecision.CLOUD_ONLY)
        
        return fallbacks
    
    def _decision_to_location(self, decision: RoutingDecision) -> ProcessingLocation:
        """将决策转换为处理位置"""
        
        if decision == RoutingDecision.LOCAL_ONLY:
            return ProcessingLocation.LOCAL_ONLY
        elif decision == RoutingDecision.CLOUD_ONLY:
            return ProcessingLocation.CLOUD_ONLY
        else:
            return ProcessingLocation.HYBRID
    
    def _update_stats(self, decision: RoutingDecision, confidence: float):
        """更新统计信息"""
        
        if decision == RoutingDecision.LOCAL_ONLY:
            self.routing_stats["local_decisions"] += 1
        elif decision == RoutingDecision.CLOUD_ONLY:
            self.routing_stats["cloud_decisions"] += 1
        else:
            self.routing_stats["hybrid_decisions"] += 1
        
        # 更新平均置信度
        total = self.routing_stats["total_requests"]
        current_avg = self.routing_stats["average_confidence"]
        self.routing_stats["average_confidence"] = (current_avg * (total - 1) + confidence) / total
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        
        total = self.routing_stats["total_requests"]
        if total == 0:
            return self.routing_stats
        
        stats = self.routing_stats.copy()
        stats["local_percentage"] = (stats["local_decisions"] / total) * 100
        stats["cloud_percentage"] = (stats["cloud_decisions"] / total) * 100
        stats["hybrid_percentage"] = (stats["hybrid_decisions"] / total) * 100
        
        return stats

# ============================================================================
# 4. OCR场景特化的路由策略
# ============================================================================

class OCRSmartRouter(EnhancedSmartRouter):
    """
    OCR场景特化的智慧路由器
    
    针对OCR任务的特点进行优化
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.ocr_config = self._get_ocr_config()
    
    def _get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR特化配置"""
        return {
            "handwriting_cloud_preference": 0.8,  # 手写识别偏好云端
            "table_extraction_cloud_preference": 0.7,  # 表格提取偏好云端
            "document_ocr_local_preference": 0.6,  # 文档OCR可以本地
            "multilingual_cloud_preference": 0.9,  # 多语言偏好云端
            "image_size_threshold": 5 * 1024 * 1024,  # 5MB图像大小阈值
            "quality_requirement_threshold": 0.9  # 高质量要求阈值
        }
    
    def route_ocr_request(self, 
                         task_type: str,
                         image_size: int,
                         quality_requirement: float,
                         privacy_level: PrivacySensitivity,
                         local_capability: float) -> RoutingResult:
        """
        OCR请求路由决策
        
        Args:
            task_type: OCR任务类型
            image_size: 图像大小(bytes)
            quality_requirement: 质量要求(0.0-1.0)
            privacy_level: 隐私级别
            local_capability: 本地处理能力
            
        Returns:
            路由决策结果
        """
        
        # 构建OCR特化的路由上下文
        context = self._build_ocr_context(
            task_type, image_size, quality_requirement, 
            privacy_level, local_capability
        )
        
        # 执行路由决策
        return self.route_request(context)
    
    def _build_ocr_context(self, 
                          task_type: str,
                          image_size: int,
                          quality_requirement: float,
                          privacy_level: PrivacySensitivity,
                          local_capability: float) -> RoutingContext:
        """构建OCR路由上下文"""
        
        # 根据任务类型调整复杂度
        complexity_mapping = {
            "document_ocr": TaskComplexity.SIMPLE,
            "handwriting_ocr": TaskComplexity.COMPLEX,
            "table_extraction": TaskComplexity.COMPLEX,
            "form_processing": TaskComplexity.MEDIUM,
            "multilingual_ocr": TaskComplexity.COMPLEX,
            "structured_data": TaskComplexity.VERY_COMPLEX
        }
        
        complexity = complexity_mapping.get(task_type, TaskComplexity.MEDIUM)
        
        # 估算Token数量（基于图像大小和任务复杂度）
        base_tokens = image_size // 1024  # 每KB约1个token
        complexity_multiplier = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MEDIUM: 1.5,
            TaskComplexity.COMPLEX: 2.0,
            TaskComplexity.VERY_COMPLEX: 3.0
        }
        estimated_tokens = int(base_tokens * complexity_multiplier[complexity])
        
        # 估算成本
        cloud_cost = estimated_tokens * 0.000001  # 假设每token 0.000001美元
        local_cost = 0.01  # 假设本地处理固定成本
        
        # 根据OCR任务类型调整本地能力
        task_preference = self.ocr_config.get(f"{task_type}_cloud_preference", 0.5)
        adjusted_local_capability = local_capability * (1 - task_preference)
        
        return RoutingContext(
            user_request=f"OCR任务: {task_type}",
            task_type=task_type,
            privacy_level=privacy_level,
            complexity=complexity,
            local_capability=adjusted_local_capability,
            cloud_cost=cloud_cost,
            local_cost=local_cost,
            estimated_tokens=estimated_tokens,
            user_preferences={
                "quality_requirement": quality_requirement,
                "image_size": image_size
            }
        )
    
    def _make_routing_decision(self, context: RoutingContext) -> RoutingDecision:
        """
        OCR特化的路由决策算法
        """
        
        # 获取OCR特定参数
        quality_requirement = context.user_preferences.get("quality_requirement", 0.8)
        image_size = context.user_preferences.get("image_size", 0)
        task_type = context.task_type
        
        # 1. 高质量要求优先云端
        if quality_requirement >= self.ocr_config["quality_requirement_threshold"]:
            if context.privacy_level != PrivacySensitivity.CRITICAL:
                return RoutingDecision.CLOUD_ONLY
        
        # 2. 大图像优先云端
        if image_size > self.ocr_config["image_size_threshold"]:
            if context.privacy_level in [PrivacySensitivity.LOW, PrivacySensitivity.MEDIUM]:
                return RoutingDecision.CLOUD_ONLY
        
        # 3. 任务类型特化决策
        if task_type == "handwriting_ocr":
            # 手写识别优先云端
            if context.privacy_level != PrivacySensitivity.CRITICAL:
                return RoutingDecision.CLOUD_ONLY
            else:
                return RoutingDecision.HYBRID_LOCAL_FIRST
        
        elif task_type == "multilingual_ocr":
            # 多语言OCR优先云端
            if context.privacy_level in [PrivacySensitivity.LOW, PrivacySensitivity.MEDIUM]:
                return RoutingDecision.CLOUD_ONLY
            else:
                return RoutingDecision.HYBRID_CLOUD_FIRST
        
        elif task_type == "document_ocr":
            # 文档OCR可以本地处理
            if context.local_capability >= 0.6:
                return RoutingDecision.LOCAL_ONLY
            else:
                return RoutingDecision.HYBRID_LOCAL_FIRST
        
        # 4. 回退到基础决策算法
        return super()._make_routing_decision(context)

# ============================================================================
# 5. 使用示例和测试
# ============================================================================

import time

def demo_smart_routing():
    """智慧路由演示"""
    
    print("🧠 智慧路由系统演示")
    print("=" * 50)
    
    # 初始化路由器
    router = OCRSmartRouter()
    
    # 测试场景
    test_cases = [
        {
            "name": "高隐私文档OCR",
            "task_type": "document_ocr",
            "image_size": 1024 * 1024,  # 1MB
            "quality_requirement": 0.8,
            "privacy_level": PrivacySensitivity.HIGH,
            "local_capability": 0.7
        },
        {
            "name": "手写识别",
            "task_type": "handwriting_ocr", 
            "image_size": 2 * 1024 * 1024,  # 2MB
            "quality_requirement": 0.9,
            "privacy_level": PrivacySensitivity.MEDIUM,
            "local_capability": 0.6
        },
        {
            "name": "大型表格提取",
            "task_type": "table_extraction",
            "image_size": 8 * 1024 * 1024,  # 8MB
            "quality_requirement": 0.95,
            "privacy_level": PrivacySensitivity.LOW,
            "local_capability": 0.5
        },
        {
            "name": "多语言文档",
            "task_type": "multilingual_ocr",
            "image_size": 3 * 1024 * 1024,  # 3MB
            "quality_requirement": 0.85,
            "privacy_level": PrivacySensitivity.CRITICAL,
            "local_capability": 0.4
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}: {case['name']}")
        print("-" * 30)
        
        result = router.route_ocr_request(
            task_type=case["task_type"],
            image_size=case["image_size"],
            quality_requirement=case["quality_requirement"],
            privacy_level=case["privacy_level"],
            local_capability=case["local_capability"]
        )
        
        print(f"🎯 路由决策: {result.decision.value}")
        print(f"📍 处理位置: {result.processing_location.value}")
        print(f"🎲 置信度: {result.confidence:.2%}")
        print(f"💰 预估成本: ${result.estimated_cost:.6f}")
        print(f"⏱️  预估时间: {result.estimated_time:.1f}秒")
        print(f"💭 决策理由: {result.reasoning}")
        
        if result.fallback_options:
            print(f"🔄 备选方案: {[opt.value for opt in result.fallback_options]}")
    
    # 显示统计信息
    print(f"\n📊 路由统计:")
    stats = router.get_routing_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

if __name__ == "__main__":
    demo_smart_routing()

