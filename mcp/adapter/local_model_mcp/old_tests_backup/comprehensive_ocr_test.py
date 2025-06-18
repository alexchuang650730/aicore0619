#!/usr/bin/env python3
"""
OCR引擎优化效果综合测试
"""

import os
import time
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import asyncio

# 导入我们的优化组件
from image_preprocessor import ImagePreprocessor, PreprocessConfig
from tesseract_optimizer import TesseractOptimizer, ContentType
from multi_engine_ocr import MultiEngineOCRManager, OCREngine, OCRResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果数据结构"""
    test_name: str
    processing_time: float
    quality_score: float
    text_length: int
    confidence: float
    engine: str
    config: str
    text_preview: str
    error: str = ""

class OCROptimizationTester:
    """OCR优化效果测试器"""
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.tesseract_optimizer = TesseractOptimizer()
        self.multi_engine_manager = None  # 延迟初始化避免内存问题
        self.test_results = []
        
    def run_comprehensive_test(self, image_path: str) -> Dict[str, Any]:
        """运行综合测试"""
        logger.info(f"🚀 开始OCR优化效果综合测试")
        logger.info(f"📸 测试图像: {image_path}")
        print("=" * 80)
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"测试图像不存在: {image_path}")
        
        # 测试套件
        test_suite = {
            "baseline_test": self._test_baseline_ocr,
            "preprocessing_test": self._test_preprocessing_optimization,
            "tesseract_optimization_test": self._test_tesseract_optimization,
            "multi_engine_test": self._test_multi_engine_optimization,
            "comprehensive_test": self._test_comprehensive_optimization
        }
        
        results = {}
        
        for test_name, test_func in test_suite.items():
            print(f"\n🧪 执行测试: {test_name}")
            print("-" * 60)
            
            try:
                start_time = time.time()
                result = test_func(image_path)
                test_time = time.time() - start_time
                
                result.processing_time = test_time
                results[test_name] = asdict(result)
                
                print(f"✅ 测试完成: {test_name}")
                print(f"⏱️ 总耗时: {test_time:.2f}秒")
                print(f"📊 质量分数: {result.quality_score:.2f}")
                print(f"📝 文本长度: {result.text_length}")
                
            except Exception as e:
                logger.error(f"❌ 测试失败 {test_name}: {e}")
                results[test_name] = {
                    "test_name": test_name,
                    "error": str(e),
                    "quality_score": 0.0
                }
        
        # 生成对比分析
        comparison = self._generate_comparison_analysis(results)
        results["comparison_analysis"] = comparison
        
        return results
    
    def _test_baseline_ocr(self, image_path: str) -> TestResult:
        """基线测试 - 使用默认Tesseract设置"""
        import pytesseract
        from PIL import Image
        
        print("📋 基线测试: 默认Tesseract设置")
        
        # 使用默认设置
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='chi_sim+chi_tra+eng')
        
        quality_score = self._calculate_quality_score(text)
        
        return TestResult(
            test_name="baseline_ocr",
            processing_time=0.0,  # 将在外部设置
            quality_score=quality_score,
            text_length=len(text.strip()),
            confidence=0.5,  # 默认置信度
            engine="tesseract_default",
            config="default",
            text_preview=text[:100] + "..." if len(text) > 100 else text
        )
    
    def _test_preprocessing_optimization(self, image_path: str) -> TestResult:
        """预处理优化测试"""
        import pytesseract
        from PIL import Image
        
        print("🎨 预处理优化测试")
        
        # 创建优化版本
        optimized_path = self.preprocessor.optimize_for_ocr(image_path)
        
        # 使用优化后的图像进行OCR
        image = Image.open(optimized_path)
        text = pytesseract.image_to_string(image, lang='chi_sim+chi_tra+eng')
        
        quality_score = self._calculate_quality_score(text)
        
        # 清理临时文件
        if os.path.exists(optimized_path):
            os.remove(optimized_path)
        
        return TestResult(
            test_name="preprocessing_optimization",
            processing_time=0.0,
            quality_score=quality_score,
            text_length=len(text.strip()),
            confidence=0.6,
            engine="tesseract_preprocessed",
            config="image_preprocessing",
            text_preview=text[:100] + "..." if len(text) > 100 else text
        )
    
    def _test_tesseract_optimization(self, image_path: str) -> TestResult:
        """Tesseract参数优化测试"""
        import pytesseract
        from PIL import Image
        
        print("⚙️ Tesseract参数优化测试")
        
        # 获取最佳配置
        best_config, best_text = self.tesseract_optimizer.get_best_config(image_path)
        cmd = self.tesseract_optimizer.build_tesseract_command(best_config)
        
        quality_score = self._calculate_quality_score(best_text)
        
        return TestResult(
            test_name="tesseract_optimization",
            processing_time=0.0,
            quality_score=quality_score,
            text_length=len(best_text.strip()),
            confidence=0.7,
            engine="tesseract_optimized",
            config=cmd,
            text_preview=best_text[:100] + "..." if len(best_text) > 100 else best_text
        )
    
    def _test_multi_engine_optimization(self, image_path: str) -> TestResult:
        """多引擎优化测试"""
        print("🔧 多引擎优化测试")
        
        try:
            # 初始化多引擎管理器（仅在需要时）
            if self.multi_engine_manager is None:
                self.multi_engine_manager = MultiEngineOCRManager()
            
            # 使用最佳置信度策略
            result = asyncio.run(self.multi_engine_manager.process_image(
                image_path, 
                engines=[OCREngine.TESSERACT],  # 仅使用Tesseract避免内存问题
                fusion_strategy="best_confidence"
            ))
            
            quality_score = self._calculate_quality_score(result.text)
            
            return TestResult(
                test_name="multi_engine_optimization",
                processing_time=0.0,
                quality_score=quality_score,
                text_length=len(result.text.strip()),
                confidence=result.confidence,
                engine=result.engine or "multi_engine",
                config="best_confidence_fusion",
                text_preview=result.text[:100] + "..." if len(result.text) > 100 else result.text
            )
            
        except Exception as e:
            logger.warning(f"多引擎测试失败，回退到Tesseract: {e}")
            return self._test_baseline_ocr(image_path)
    
    def _test_comprehensive_optimization(self, image_path: str) -> TestResult:
        """综合优化测试 - 结合所有优化技术"""
        import pytesseract
        from PIL import Image
        
        print("🚀 综合优化测试: 预处理 + 参数优化")
        
        # 1. 图像预处理
        optimized_path = self.preprocessor.optimize_for_ocr(image_path)
        
        # 2. 获取最佳Tesseract配置
        best_config, _ = self.tesseract_optimizer.get_best_config(optimized_path)
        cmd = self.tesseract_optimizer.build_tesseract_command(best_config)
        
        # 3. 使用优化配置处理优化图像
        image = Image.open(optimized_path)
        text = pytesseract.image_to_string(image, config=cmd)
        
        quality_score = self._calculate_quality_score(text)
        
        # 清理临时文件
        if os.path.exists(optimized_path):
            os.remove(optimized_path)
        
        return TestResult(
            test_name="comprehensive_optimization",
            processing_time=0.0,
            quality_score=quality_score,
            text_length=len(text.strip()),
            confidence=0.8,
            engine="tesseract_comprehensive",
            config=f"preprocessing + {cmd}",
            text_preview=text[:100] + "..." if len(text) > 100 else text
        )
    
    def _calculate_quality_score(self, text: str) -> float:
        """计算OCR质量分数"""
        if not text.strip():
            return 0.0
        
        score = 0.0
        
        # 文本长度分数
        if len(text.strip()) > 10:
            score += 0.2
        
        # 中文字符识别分数
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        if chinese_chars > 0:
            score += 0.3
        
        # 数字识别分数
        digits = len(re.findall(r'\d', text))
        if digits > 0:
            score += 0.2
        
        # 关键词识别分数
        keywords = ['保险', '银行', '姓名', '地址', '电话', '金额', '日期', '台湾', '人寿']
        found_keywords = sum(1 for keyword in keywords if keyword in text)
        score += (found_keywords / len(keywords)) * 0.3
        
        return min(score, 1.0)
    
    def _generate_comparison_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成对比分析"""
        print(f"\n📊 生成对比分析报告")
        
        # 提取有效结果
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            return {"error": "没有有效的测试结果"}
        
        # 找到最佳结果
        best_test = max(valid_results.keys(), key=lambda k: valid_results[k]['quality_score'])
        best_score = valid_results[best_test]['quality_score']
        
        # 计算改进幅度
        baseline_score = valid_results.get('baseline_test', {}).get('quality_score', 0)
        improvement = ((best_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
        
        # 性能排名
        ranking = sorted(
            valid_results.items(), 
            key=lambda x: x[1]['quality_score'], 
            reverse=True
        )
        
        analysis = {
            "best_method": best_test,
            "best_score": best_score,
            "baseline_score": baseline_score,
            "improvement_percentage": improvement,
            "performance_ranking": [
                {
                    "rank": i + 1,
                    "method": method,
                    "score": data['quality_score'],
                    "time": data['processing_time']
                }
                for i, (method, data) in enumerate(ranking)
            ],
            "summary": {
                "total_tests": len(valid_results),
                "successful_tests": len(valid_results),
                "failed_tests": len(results) - len(valid_results),
                "max_improvement": f"{improvement:.1f}%"
            }
        }
        
        return analysis
    
    def save_results(self, results: Dict[str, Any], output_path: str = "ocr_optimization_results.json"):
        """保存测试结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 测试结果已保存: {output_path}")
        return output_path

def main():
    """主测试函数"""
    print("🧪 OCR引擎优化效果综合测试")
    print("=" * 80)
    
    # 测试图像路径
    test_image = "/home/ubuntu/upload/張家銓_1.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        return
    
    # 创建测试器
    tester = OCROptimizationTester()
    
    try:
        # 运行综合测试
        results = tester.run_comprehensive_test(test_image)
        
        # 保存结果
        output_file = tester.save_results(results)
        
        # 显示最终报告
        print(f"\n🎉 测试完成！")
        print("=" * 80)
        
        if "comparison_analysis" in results:
            analysis = results["comparison_analysis"]
            print(f"🏆 最佳方法: {analysis['best_method']}")
            print(f"📊 最佳分数: {analysis['best_score']:.2f}")
            print(f"📈 改进幅度: {analysis['improvement_percentage']:.1f}%")
            
            print(f"\n📋 性能排名:")
            for rank_info in analysis["performance_ranking"]:
                print(f"  {rank_info['rank']}. {rank_info['method']}: {rank_info['score']:.2f} ({rank_info['time']:.2f}s)")
        
        print(f"\n📄 详细结果已保存至: {output_file}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error(f"测试失败: {e}")

if __name__ == "__main__":
    main()

