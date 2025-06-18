"""
PowerAutomation 测试管理 - 预测性性能分析引擎

提供AI驱动的性能预测、瓶颈识别和优化建议功能。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """性能等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


class TrendDirection(Enum):
    """趋势方向"""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any]
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


@dataclass
class PerformanceAnalysis:
    """性能分析结果"""
    analysis_id: str
    timestamp: datetime
    overall_score: float
    performance_level: PerformanceLevel
    trend_direction: TrendDirection
    key_metrics: Dict[str, float]
    bottlenecks: List[Dict[str, Any]]
    predictions: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    confidence: float


@dataclass
class PerformancePrediction:
    """性能预测"""
    metric_name: str
    current_value: float
    predicted_values: List[Tuple[datetime, float]]
    confidence_interval: Tuple[float, float]
    trend_analysis: str
    risk_factors: List[str]


class PredictivePerformanceAnalyzer:
    """
    预测性性能分析引擎
    
    提供AI驱动的性能监控、趋势分析和预测功能。
    """
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        """
        初始化预测性性能分析引擎
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.metrics_path = self.project_root / "performance_metrics"
        self.models_path = self.project_root / "performance_models"
        self.reports_path = self.project_root / "performance_reports"
        
        # 确保目录存在
        for path in [self.metrics_path, self.models_path, self.reports_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # 性能数据存储
        self.metrics_history: List[PerformanceMetric] = []
        self.analysis_history: List[PerformanceAnalysis] = []
        
        # 性能阈值配置
        self.performance_thresholds = {
            "execution_time": {"warning": 30.0, "critical": 60.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "test_success_rate": {"warning": 90.0, "critical": 80.0},
            "response_time": {"warning": 2.0, "critical": 5.0},
            "throughput": {"warning": 100.0, "critical": 50.0}
        }
        
        # 预测模型参数
        self.prediction_window = 24  # 预测未来24小时
        self.history_window = 168   # 使用过去7天的数据
        
        logger.info("预测性性能分析引擎初始化完成")
    
    async def collect_performance_metrics(self, test_results: Dict[str, Any]) -> List[PerformanceMetric]:
        """
        收集性能指标
        
        Args:
            test_results: 测试结果数据
            
        Returns:
            性能指标列表
        """
        logger.info("收集性能指标")
        
        metrics = []
        timestamp = datetime.now()
        
        # 执行时间指标
        if "execution_time" in test_results:
            metrics.append(PerformanceMetric(
                name="execution_time",
                value=test_results["execution_time"],
                unit="seconds",
                timestamp=timestamp,
                context={"test_suite": test_results.get("test_suite", "unknown")},
                threshold_warning=self.performance_thresholds["execution_time"]["warning"],
                threshold_critical=self.performance_thresholds["execution_time"]["critical"]
            ))
        
        # 内存使用指标
        if "memory_usage" in test_results:
            metrics.append(PerformanceMetric(
                name="memory_usage",
                value=test_results["memory_usage"],
                unit="percentage",
                timestamp=timestamp,
                context={"peak_memory": test_results.get("peak_memory", 0)},
                threshold_warning=self.performance_thresholds["memory_usage"]["warning"],
                threshold_critical=self.performance_thresholds["memory_usage"]["critical"]
            ))
        
        # CPU使用指标
        if "cpu_usage" in test_results:
            metrics.append(PerformanceMetric(
                name="cpu_usage",
                value=test_results["cpu_usage"],
                unit="percentage",
                timestamp=timestamp,
                context={"cores_used": test_results.get("cores_used", 1)},
                threshold_warning=self.performance_thresholds["cpu_usage"]["warning"],
                threshold_critical=self.performance_thresholds["cpu_usage"]["critical"]
            ))
        
        # 测试成功率指标
        if "total_tests" in test_results and "passed_tests" in test_results:
            success_rate = (test_results["passed_tests"] / test_results["total_tests"]) * 100
            metrics.append(PerformanceMetric(
                name="test_success_rate",
                value=success_rate,
                unit="percentage",
                timestamp=timestamp,
                context={
                    "total_tests": test_results["total_tests"],
                    "passed_tests": test_results["passed_tests"],
                    "failed_tests": test_results.get("failed_tests", 0)
                },
                threshold_warning=self.performance_thresholds["test_success_rate"]["warning"],
                threshold_critical=self.performance_thresholds["test_success_rate"]["critical"]
            ))
        
        # 响应时间指标
        if "response_times" in test_results:
            avg_response_time = statistics.mean(test_results["response_times"])
            metrics.append(PerformanceMetric(
                name="response_time",
                value=avg_response_time,
                unit="seconds",
                timestamp=timestamp,
                context={
                    "min_response": min(test_results["response_times"]),
                    "max_response": max(test_results["response_times"]),
                    "requests_count": len(test_results["response_times"])
                },
                threshold_warning=self.performance_thresholds["response_time"]["warning"],
                threshold_critical=self.performance_thresholds["response_time"]["critical"]
            ))
        
        # 吞吐量指标
        if "throughput" in test_results:
            metrics.append(PerformanceMetric(
                name="throughput",
                value=test_results["throughput"],
                unit="requests_per_second",
                timestamp=timestamp,
                context={"test_duration": test_results.get("test_duration", 0)},
                threshold_warning=self.performance_thresholds["throughput"]["warning"],
                threshold_critical=self.performance_thresholds["throughput"]["critical"]
            ))
        
        # 存储指标到历史记录
        self.metrics_history.extend(metrics)
        
        # 保持历史记录在合理范围内
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-5000:]
        
        logger.info(f"收集了 {len(metrics)} 个性能指标")
        return metrics
    
    async def analyze_performance_trends(self, metric_name: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        分析性能趋势
        
        Args:
            metric_name: 指标名称
            time_window_hours: 时间窗口（小时）
            
        Returns:
            趋势分析结果
        """
        logger.info(f"分析性能趋势: {metric_name}")
        
        # 获取指定时间窗口内的指标数据
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        relevant_metrics = [
            m for m in self.metrics_history
            if m.name == metric_name and m.timestamp >= cutoff_time
        ]
        
        if len(relevant_metrics) < 2:
            return {
                "metric_name": metric_name,
                "trend": "insufficient_data",
                "message": "数据不足，无法分析趋势"
            }
        
        # 提取数值和时间戳
        values = [m.value for m in relevant_metrics]
        timestamps = [m.timestamp for m in relevant_metrics]
        
        # 计算基本统计信息
        mean_value = statistics.mean(values)
        median_value = statistics.median(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        min_value = min(values)
        max_value = max(values)
        
        # 计算趋势方向
        trend_direction = self._calculate_trend_direction(values)
        
        # 计算变化率
        if len(values) >= 2:
            change_rate = (values[-1] - values[0]) / values[0] * 100
        else:
            change_rate = 0
        
        # 检测异常值
        anomalies = self._detect_anomalies(values)
        
        # 计算稳定性指标
        stability_score = self._calculate_stability_score(values)
        
        return {
            "metric_name": metric_name,
            "time_window_hours": time_window_hours,
            "data_points": len(values),
            "trend_direction": trend_direction.value,
            "statistics": {
                "mean": mean_value,
                "median": median_value,
                "std_dev": std_dev,
                "min": min_value,
                "max": max_value,
                "range": max_value - min_value
            },
            "change_rate_percent": change_rate,
            "stability_score": stability_score,
            "anomalies_count": len(anomalies),
            "anomalies": anomalies,
            "latest_value": values[-1],
            "trend_analysis": self._generate_trend_analysis(trend_direction, change_rate, stability_score)
        }
    
    def _calculate_trend_direction(self, values: List[float]) -> TrendDirection:
        """计算趋势方向"""
        if len(values) < 3:
            return TrendDirection.STABLE
        
        # 使用线性回归计算趋势
        x = list(range(len(values)))
        y = values
        
        # 简化的线性回归
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # 计算变异系数
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_dev / mean_value if mean_value != 0 else 0
        
        # 判断趋势
        if cv > 0.3:  # 变异系数大于30%认为是波动的
            return TrendDirection.VOLATILE
        elif slope > 0.1:
            return TrendDirection.IMPROVING
        elif slope < -0.1:
            return TrendDirection.DEGRADING
        else:
            return TrendDirection.STABLE
    
    def _detect_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """检测异常值"""
        if len(values) < 3:
            return []
        
        anomalies = []
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # 使用3-sigma规则检测异常
        threshold = 3 * std_dev
        
        for i, value in enumerate(values):
            if abs(value - mean_value) > threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "deviation": abs(value - mean_value),
                    "type": "high" if value > mean_value else "low"
                })
        
        return anomalies
    
    def _calculate_stability_score(self, values: List[float]) -> float:
        """计算稳定性分数（0-100）"""
        if len(values) < 2:
            return 100.0
        
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # 变异系数
        cv = std_dev / mean_value if mean_value != 0 else 0
        
        # 稳定性分数（变异系数越小，稳定性越高）
        stability_score = max(0, 100 - (cv * 100))
        
        return min(100.0, stability_score)
    
    def _generate_trend_analysis(self, trend: TrendDirection, change_rate: float, stability: float) -> str:
        """生成趋势分析描述"""
        if trend == TrendDirection.IMPROVING:
            return f"性能呈改善趋势，变化率为 {change_rate:.1f}%，稳定性评分 {stability:.1f}"
        elif trend == TrendDirection.DEGRADING:
            return f"性能呈下降趋势，变化率为 {change_rate:.1f}%，稳定性评分 {stability:.1f}"
        elif trend == TrendDirection.VOLATILE:
            return f"性能波动较大，稳定性评分 {stability:.1f}，需要关注"
        else:
            return f"性能保持稳定，稳定性评分 {stability:.1f}"
    
    async def predict_future_performance(self, metric_name: str, prediction_hours: int = 24) -> PerformancePrediction:
        """
        预测未来性能
        
        Args:
            metric_name: 指标名称
            prediction_hours: 预测时间范围（小时）
            
        Returns:
            性能预测结果
        """
        logger.info(f"预测未来性能: {metric_name}")
        
        # 获取历史数据
        cutoff_time = datetime.now() - timedelta(hours=self.history_window)
        historical_metrics = [
            m for m in self.metrics_history
            if m.name == metric_name and m.timestamp >= cutoff_time
        ]
        
        if len(historical_metrics) < 10:
            return PerformancePrediction(
                metric_name=metric_name,
                current_value=0.0,
                predicted_values=[],
                confidence_interval=(0.0, 0.0),
                trend_analysis="数据不足，无法进行预测",
                risk_factors=["历史数据不足"]
            )
        
        # 提取数值
        values = [m.value for m in historical_metrics]
        current_value = values[-1]
        
        # 简化的预测模型（移动平均 + 趋势）
        predicted_values = []
        base_time = datetime.now()
        
        # 计算移动平均和趋势
        window_size = min(10, len(values))
        recent_values = values[-window_size:]
        moving_avg = statistics.mean(recent_values)
        
        # 计算趋势斜率
        if len(values) >= 5:
            x = list(range(len(values[-5:])))
            y = values[-5:]
            slope = self._calculate_slope(x, y)
        else:
            slope = 0
        
        # 生成预测值
        for hour in range(1, prediction_hours + 1):
            # 简单的线性预测 + 随机波动
            predicted_value = moving_avg + (slope * hour)
            
            # 添加一些随机性（基于历史标准差）
            if len(values) > 1:
                std_dev = statistics.stdev(values)
                # 简化：不添加随机性，保持确定性预测
            
            predicted_time = base_time + timedelta(hours=hour)
            predicted_values.append((predicted_time, predicted_value))
        
        # 计算置信区间
        if len(values) > 1:
            std_dev = statistics.stdev(values)
            confidence_interval = (
                moving_avg - 1.96 * std_dev,
                moving_avg + 1.96 * std_dev
            )
        else:
            confidence_interval = (current_value, current_value)
        
        # 识别风险因素
        risk_factors = self._identify_risk_factors(values, metric_name)
        
        # 生成趋势分析
        trend_analysis = self._generate_prediction_analysis(slope, std_dev if len(values) > 1 else 0)
        
        return PerformancePrediction(
            metric_name=metric_name,
            current_value=current_value,
            predicted_values=predicted_values,
            confidence_interval=confidence_interval,
            trend_analysis=trend_analysis,
            risk_factors=risk_factors
        )
    
    def _calculate_slope(self, x: List[int], y: List[float]) -> float:
        """计算线性回归斜率"""
        n = len(x)
        if n < 2:
            return 0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    def _identify_risk_factors(self, values: List[float], metric_name: str) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        if len(values) < 5:
            risk_factors.append("历史数据不足")
            return risk_factors
        
        # 检查趋势
        recent_trend = self._calculate_trend_direction(values[-5:])
        if recent_trend == TrendDirection.DEGRADING:
            risk_factors.append("近期性能下降趋势")
        elif recent_trend == TrendDirection.VOLATILE:
            risk_factors.append("性能波动较大")
        
        # 检查阈值接近程度
        current_value = values[-1]
        if metric_name in self.performance_thresholds:
            thresholds = self.performance_thresholds[metric_name]
            warning_threshold = thresholds["warning"]
            critical_threshold = thresholds["critical"]
            
            if metric_name in ["execution_time", "memory_usage", "cpu_usage", "response_time"]:
                # 这些指标值越高越差
                if current_value >= critical_threshold:
                    risk_factors.append("已达到关键阈值")
                elif current_value >= warning_threshold:
                    risk_factors.append("接近警告阈值")
            else:
                # 这些指标值越低越差（如成功率、吞吐量）
                if current_value <= critical_threshold:
                    risk_factors.append("已达到关键阈值")
                elif current_value <= warning_threshold:
                    risk_factors.append("接近警告阈值")
        
        # 检查变异性
        if len(values) > 1:
            std_dev = statistics.stdev(values)
            mean_value = statistics.mean(values)
            cv = std_dev / mean_value if mean_value != 0 else 0
            
            if cv > 0.3:
                risk_factors.append("性能变异性过高")
        
        return risk_factors
    
    def _generate_prediction_analysis(self, slope: float, std_dev: float) -> str:
        """生成预测分析描述"""
        if abs(slope) < 0.01:
            trend_desc = "保持稳定"
        elif slope > 0:
            trend_desc = f"预计将以 {slope:.3f} 的速率改善"
        else:
            trend_desc = f"预计将以 {abs(slope):.3f} 的速率下降"
        
        if std_dev < 1.0:
            stability_desc = "预测稳定性较高"
        elif std_dev < 5.0:
            stability_desc = "预测稳定性中等"
        else:
            stability_desc = "预测稳定性较低"
        
        return f"基于历史趋势，性能{trend_desc}，{stability_desc}"
    
    async def generate_performance_analysis(self, context: Dict[str, Any] = None) -> PerformanceAnalysis:
        """
        生成综合性能分析报告
        
        Args:
            context: 分析上下文
            
        Returns:
            性能分析结果
        """
        logger.info("生成综合性能分析报告")
        
        context = context or {}
        analysis_id = f"perf_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 收集关键指标
        key_metrics = {}
        recent_time = datetime.now() - timedelta(hours=1)
        
        for metric_name in ["execution_time", "memory_usage", "cpu_usage", "test_success_rate"]:
            recent_metrics = [
                m for m in self.metrics_history
                if m.name == metric_name and m.timestamp >= recent_time
            ]
            if recent_metrics:
                key_metrics[metric_name] = statistics.mean([m.value for m in recent_metrics])
        
        # 计算总体性能分数
        overall_score = self._calculate_overall_score(key_metrics)
        
        # 确定性能等级
        performance_level = self._determine_performance_level(overall_score)
        
        # 分析趋势方向
        trend_direction = await self._analyze_overall_trend()
        
        # 识别瓶颈
        bottlenecks = await self._identify_bottlenecks(key_metrics)
        
        # 生成预测
        predictions = await self._generate_predictions_summary()
        
        # 生成建议
        recommendations = await self._generate_performance_recommendations(key_metrics, bottlenecks)
        
        # 计算分析置信度
        confidence = self._calculate_analysis_confidence(key_metrics)
        
        analysis = PerformanceAnalysis(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            overall_score=overall_score,
            performance_level=performance_level,
            trend_direction=trend_direction,
            key_metrics=key_metrics,
            bottlenecks=bottlenecks,
            predictions=predictions,
            recommendations=recommendations,
            confidence=confidence
        )
        
        # 保存分析结果
        self.analysis_history.append(analysis)
        
        logger.info(f"性能分析完成: {analysis_id}")
        return analysis
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """计算总体性能分数"""
        if not metrics:
            return 50.0  # 默认中等分数
        
        scores = []
        
        # 执行时间分数（越低越好）
        if "execution_time" in metrics:
            exec_time = metrics["execution_time"]
            if exec_time <= 10:
                scores.append(100)
            elif exec_time <= 30:
                scores.append(80)
            elif exec_time <= 60:
                scores.append(60)
            else:
                scores.append(40)
        
        # 内存使用分数（越低越好）
        if "memory_usage" in metrics:
            memory = metrics["memory_usage"]
            if memory <= 50:
                scores.append(100)
            elif memory <= 70:
                scores.append(80)
            elif memory <= 85:
                scores.append(60)
            else:
                scores.append(40)
        
        # CPU使用分数（越低越好）
        if "cpu_usage" in metrics:
            cpu = metrics["cpu_usage"]
            if cpu <= 50:
                scores.append(100)
            elif cpu <= 70:
                scores.append(80)
            elif cpu <= 85:
                scores.append(60)
            else:
                scores.append(40)
        
        # 测试成功率分数（越高越好）
        if "test_success_rate" in metrics:
            success_rate = metrics["test_success_rate"]
            if success_rate >= 95:
                scores.append(100)
            elif success_rate >= 90:
                scores.append(80)
            elif success_rate >= 80:
                scores.append(60)
            else:
                scores.append(40)
        
        return statistics.mean(scores) if scores else 50.0
    
    def _determine_performance_level(self, score: float) -> PerformanceLevel:
        """确定性能等级"""
        if score >= 90:
            return PerformanceLevel.EXCELLENT
        elif score >= 75:
            return PerformanceLevel.GOOD
        elif score >= 60:
            return PerformanceLevel.AVERAGE
        elif score >= 40:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    async def _analyze_overall_trend(self) -> TrendDirection:
        """分析总体趋势"""
        # 简化实现：基于最近的执行时间趋势
        recent_time = datetime.now() - timedelta(hours=6)
        execution_metrics = [
            m for m in self.metrics_history
            if m.name == "execution_time" and m.timestamp >= recent_time
        ]
        
        if len(execution_metrics) >= 3:
            values = [m.value for m in execution_metrics]
            return self._calculate_trend_direction(values)
        
        return TrendDirection.STABLE
    
    async def _identify_bottlenecks(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """识别性能瓶颈"""
        bottlenecks = []
        
        # 检查各项指标是否超过阈值
        for metric_name, value in metrics.items():
            if metric_name in self.performance_thresholds:
                thresholds = self.performance_thresholds[metric_name]
                
                if metric_name in ["execution_time", "memory_usage", "cpu_usage", "response_time"]:
                    # 值越高越差的指标
                    if value >= thresholds["critical"]:
                        bottlenecks.append({
                            "type": "critical_threshold",
                            "metric": metric_name,
                            "current_value": value,
                            "threshold": thresholds["critical"],
                            "severity": "critical",
                            "description": f"{metric_name} 达到关键阈值"
                        })
                    elif value >= thresholds["warning"]:
                        bottlenecks.append({
                            "type": "warning_threshold",
                            "metric": metric_name,
                            "current_value": value,
                            "threshold": thresholds["warning"],
                            "severity": "warning",
                            "description": f"{metric_name} 接近警告阈值"
                        })
                else:
                    # 值越低越差的指标
                    if value <= thresholds["critical"]:
                        bottlenecks.append({
                            "type": "critical_threshold",
                            "metric": metric_name,
                            "current_value": value,
                            "threshold": thresholds["critical"],
                            "severity": "critical",
                            "description": f"{metric_name} 低于关键阈值"
                        })
                    elif value <= thresholds["warning"]:
                        bottlenecks.append({
                            "type": "warning_threshold",
                            "metric": metric_name,
                            "current_value": value,
                            "threshold": thresholds["warning"],
                            "severity": "warning",
                            "description": f"{metric_name} 低于警告阈值"
                        })
        
        return bottlenecks
    
    async def _generate_predictions_summary(self) -> Dict[str, Any]:
        """生成预测摘要"""
        predictions_summary = {}
        
        for metric_name in ["execution_time", "memory_usage", "test_success_rate"]:
            try:
                prediction = await self.predict_future_performance(metric_name, 12)
                predictions_summary[metric_name] = {
                    "current_value": prediction.current_value,
                    "trend": prediction.trend_analysis,
                    "risk_factors": prediction.risk_factors
                }
            except Exception as e:
                logger.warning(f"预测 {metric_name} 时出错: {e}")
        
        return predictions_summary
    
    async def _generate_performance_recommendations(self, metrics: Dict[str, float], bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成性能优化建议"""
        recommendations = []
        
        # 基于瓶颈生成建议
        for bottleneck in bottlenecks:
            metric_name = bottleneck["metric"]
            
            if metric_name == "execution_time":
                recommendations.append({
                    "type": "optimization",
                    "priority": "high",
                    "title": "优化测试执行时间",
                    "description": "考虑并行化测试执行或优化测试代码",
                    "actions": [
                        "启用并行测试执行",
                        "优化慢速测试用例",
                        "使用测试缓存机制"
                    ]
                })
            
            elif metric_name == "memory_usage":
                recommendations.append({
                    "type": "resource",
                    "priority": "high",
                    "title": "优化内存使用",
                    "description": "减少内存消耗或增加可用内存",
                    "actions": [
                        "优化数据结构使用",
                        "实现内存池管理",
                        "增加系统内存"
                    ]
                })
            
            elif metric_name == "cpu_usage":
                recommendations.append({
                    "type": "resource",
                    "priority": "medium",
                    "title": "优化CPU使用",
                    "description": "减少CPU密集型操作或增加处理能力",
                    "actions": [
                        "优化算法复杂度",
                        "使用异步处理",
                        "增加CPU核心数"
                    ]
                })
            
            elif metric_name == "test_success_rate":
                recommendations.append({
                    "type": "quality",
                    "priority": "critical",
                    "title": "提高测试成功率",
                    "description": "分析并修复失败的测试用例",
                    "actions": [
                        "分析测试失败原因",
                        "修复不稳定的测试",
                        "改进测试环境配置"
                    ]
                })
        
        # 基于总体性能生成通用建议
        if not recommendations:
            recommendations.append({
                "type": "general",
                "priority": "low",
                "title": "持续性能监控",
                "description": "保持当前性能水平并持续监控",
                "actions": [
                    "定期检查性能指标",
                    "建立性能基准",
                    "实施性能回归测试"
                ]
            })
        
        return recommendations
    
    def _calculate_analysis_confidence(self, metrics: Dict[str, float]) -> float:
        """计算分析置信度"""
        base_confidence = 0.5
        
        # 有更多指标数据，置信度更高
        if len(metrics) >= 4:
            base_confidence += 0.3
        elif len(metrics) >= 2:
            base_confidence += 0.2
        
        # 有足够的历史数据，置信度更高
        if len(self.metrics_history) >= 100:
            base_confidence += 0.2
        elif len(self.metrics_history) >= 50:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能分析引擎摘要"""
        recent_time = datetime.now() - timedelta(hours=24)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= recent_time]
        
        return {
            "status": "active",
            "total_metrics_collected": len(self.metrics_history),
            "recent_metrics_24h": len(recent_metrics),
            "analysis_history_size": len(self.analysis_history),
            "monitored_metrics": list(self.performance_thresholds.keys()),
            "prediction_window_hours": self.prediction_window,
            "history_window_hours": self.history_window
        }


# 创建全局预测性性能分析引擎实例
_global_performance_analyzer = None

def get_performance_analyzer(project_root: str = "/opt/powerautomation") -> PredictivePerformanceAnalyzer:
    """获取全局预测性性能分析引擎实例"""
    global _global_performance_analyzer
    if _global_performance_analyzer is None:
        _global_performance_analyzer = PredictivePerformanceAnalyzer(project_root)
    return _global_performance_analyzer


if __name__ == "__main__":
    # 测试预测性性能分析引擎
    async def test_performance_analyzer():
        analyzer = PredictivePerformanceAnalyzer()
        
        # 模拟测试结果数据
        test_results = {
            "execution_time": 25.5,
            "memory_usage": 65.2,
            "cpu_usage": 45.8,
            "total_tests": 100,
            "passed_tests": 95,
            "failed_tests": 5,
            "response_times": [1.2, 1.5, 1.8, 2.1, 1.9],
            "throughput": 150.0
        }
        
        # 收集性能指标
        metrics = await analyzer.collect_performance_metrics(test_results)
        print(f"收集了 {len(metrics)} 个性能指标")
        
        # 分析性能趋势
        if metrics:
            trend_analysis = await analyzer.analyze_performance_trends("execution_time")
            print(f"执行时间趋势: {trend_analysis['trend_direction']}")
        
        # 预测未来性能
        prediction = await analyzer.predict_future_performance("execution_time")
        print(f"执行时间预测: {prediction.trend_analysis}")
        
        # 生成综合分析
        analysis = await analyzer.generate_performance_analysis()
        print(f"总体性能分数: {analysis.overall_score:.1f}")
        print(f"性能等级: {analysis.performance_level.value}")
        print(f"发现 {len(analysis.bottlenecks)} 个瓶颈")
        print(f"生成 {len(analysis.recommendations)} 个建议")
    
    asyncio.run(test_performance_analyzer())

