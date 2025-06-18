#!/usr/bin/env python3
"""
稳定版OCR测试套件 - 分步测试和错误处理
"""

import asyncio
import logging
import sys
import time
import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import subprocess
import signal

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OCRTestResult:
    """OCR测试结果"""
    method_name: str
    processing_time: float
    extracted_text: str
    confidence: float
    structured_data: Dict[str, Any]
    success: bool
    error: str = ""

class StableOCRTester:
    """稳定的OCR测试器"""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.test_results = []
        
        # 预期的关键信息
        self.expected_data = {
            "print_number": "900829",
            "print_time": "2025/06/09 02:14:42",
            "form_title": "台银人壽利率變動型人壽保險要保書",
            "insured_name": "沈宗銘",
            "gender": "男",
            "birth_date": "87年5月29日",
            "age": "26",
            "address": "台中市東勢區40號5樓",
            "insurance_name": "安心傳家利率變動型終身壽險",
            "payment_period": "20年",
            "premium": "8930元"
        }
    
    async def test_mistral_api(self) -> OCRTestResult:
        """测试Mistral API"""
        print("🤖 测试Mistral API...")
        
        try:
            import aiohttp
            
            # Mistral API配置
            api_key = "fLDmWp2L4HZ9MRxL1AfY8cqW5zxq3tumnew"
            base_url = "https://api.mistral.ai/v1"
            model_name = "pixtral-12b-2409"
            
            # 编码图像
            with open(self.image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = """请分析这张保险表单，提取所有可见的文字内容。重点关注：
1. 表单头部的数字和时间
2. 被保险人的个人信息
3. 保险产品的详细信息
4. 所有表格中的数据

请以清晰的格式返回所有识别的文字。"""
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    ]
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_name,
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    processing_time = time.time() - start_time
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text)
                        content = result['choices'][0]['message']['content']
                        
                        # 提取结构化数据
                        structured_data = self._extract_structured_data(content)
                        confidence = self._calculate_confidence(content)
                        
                        return OCRTestResult(
                            method_name="Mistral API",
                            processing_time=processing_time,
                            extracted_text=content,
                            confidence=confidence,
                            structured_data=structured_data,
                            success=True
                        )
                    
                    else:
                        return OCRTestResult(
                            method_name="Mistral API",
                            processing_time=processing_time,
                            extracted_text="",
                            confidence=0.0,
                            structured_data={},
                            success=False,
                            error=f"API Error {response.status}: {response_text}"
                        )
        
        except Exception as e:
            return OCRTestResult(
                method_name="Mistral API",
                processing_time=0.0,
                extracted_text="",
                confidence=0.0,
                structured_data={},
                success=False,
                error=str(e)
            )
    
    def test_tesseract_only(self) -> OCRTestResult:
        """只测试Tesseract OCR"""
        print("📝 测试Tesseract OCR...")
        
        try:
            start_time = time.time()
            
            # 使用命令行调用Tesseract，设置超时
            cmd = [
                'tesseract', 
                self.image_path, 
                'stdout',
                '--psm', '3',
                '--oem', '1',
                '-l', 'chi_sim+chi_tra+eng'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                encoding='utf-8'
            )
            
            processing_time = time.time() - start_time
            
            if result.returncode == 0:
                text = result.stdout
                structured_data = self._extract_structured_data(text)
                confidence = self._calculate_confidence(text)
                
                return OCRTestResult(
                    method_name="Tesseract OCR",
                    processing_time=processing_time,
                    extracted_text=text,
                    confidence=confidence,
                    structured_data=structured_data,
                    success=True
                )
            else:
                return OCRTestResult(
                    method_name="Tesseract OCR",
                    processing_time=processing_time,
                    extracted_text="",
                    confidence=0.0,
                    structured_data={},
                    success=False,
                    error=f"Tesseract error: {result.stderr}"
                )
        
        except subprocess.TimeoutExpired:
            return OCRTestResult(
                method_name="Tesseract OCR",
                processing_time=30.0,
                extracted_text="",
                confidence=0.0,
                structured_data={},
                success=False,
                error="Tesseract timeout after 30 seconds"
            )
        
        except Exception as e:
            return OCRTestResult(
                method_name="Tesseract OCR",
                processing_time=0.0,
                extracted_text="",
                confidence=0.0,
                structured_data={},
                success=False,
                error=str(e)
            )
    
    def test_easyocr_only(self) -> OCRTestResult:
        """只测试EasyOCR"""
        print("🔍 测试EasyOCR...")
        
        try:
            import easyocr
            
            start_time = time.time()
            
            # 创建EasyOCR reader
            reader = easyocr.Reader(['ch_sim', 'ch_tra', 'en'], gpu=False)
            
            # 读取文本
            results = reader.readtext(self.image_path)
            
            processing_time = time.time() - start_time
            
            # 组合文本
            text_lines = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # 过滤低置信度结果
                    text_lines.append(text)
            
            combined_text = '\\n'.join(text_lines)
            
            # 计算平均置信度
            confidences = [conf for (_, _, conf) in results if conf > 0.3]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            structured_data = self._extract_structured_data(combined_text)
            
            return OCRTestResult(
                method_name="EasyOCR",
                processing_time=processing_time,
                extracted_text=combined_text,
                confidence=avg_confidence,
                structured_data=structured_data,
                success=True
            )
        
        except Exception as e:
            return OCRTestResult(
                method_name="EasyOCR",
                processing_time=0.0,
                extracted_text="",
                confidence=0.0,
                structured_data={},
                success=False,
                error=str(e)
            )
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """从文本中提取结构化数据"""
        structured_data = {
            "extracted_fields": {},
            "found_keywords": []
        }
        
        text_lower = text.lower()
        
        # 查找关键信息
        for key, expected_value in self.expected_data.items():
            if expected_value.lower() in text_lower:
                structured_data["extracted_fields"][key] = expected_value
                structured_data["found_keywords"].append(expected_value)
        
        return structured_data
    
    def _calculate_confidence(self, text: str) -> float:
        """计算置信度"""
        if not text:
            return 0.0
        
        # 基于关键字匹配
        found_keywords = 0
        for expected_value in self.expected_data.values():
            if expected_value.lower() in text.lower():
                found_keywords += 1
        
        keyword_score = found_keywords / len(self.expected_data)
        
        # 基于文本长度
        length_score = min(len(text) / 1000, 1.0)
        
        # 综合置信度
        confidence = keyword_score * 0.7 + length_score * 0.3
        
        return min(confidence, 0.95)
    
    def calculate_accuracy(self, result: OCRTestResult) -> Dict[str, float]:
        """计算准确度指标"""
        if not result.success:
            return {"overall_accuracy": 0.0, "correct_fields": 0, "total_fields": len(self.expected_data)}
        
        correct_fields = 0
        text_lower = result.extracted_text.lower()
        
        field_results = {}
        
        for key, expected_value in self.expected_data.items():
            found = expected_value.lower() in text_lower
            if found:
                correct_fields += 1
            field_results[f"{key}_found"] = found
        
        overall_accuracy = correct_fields / len(self.expected_data)
        
        return {
            "overall_accuracy": overall_accuracy,
            "correct_fields": correct_fields,
            "total_fields": len(self.expected_data),
            **field_results
        }
    
    async def run_all_tests(self) -> List[OCRTestResult]:
        """运行所有测试"""
        print("🧪 开始稳定OCR测试套件")
        print("=" * 80)
        
        # 1. 测试Mistral API
        mistral_result = await self.test_mistral_api()
        self.test_results.append(mistral_result)
        
        # 2. 测试Tesseract
        tesseract_result = self.test_tesseract_only()
        self.test_results.append(tesseract_result)
        
        # 3. 测试EasyOCR
        easyocr_result = self.test_easyocr_only()
        self.test_results.append(easyocr_result)
        
        return self.test_results
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("# 保险表单OCR测试报告")
        report.append("=" * 60)
        report.append("")
        report.append(f"**测试图像**: {self.image_path}")
        report.append(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 结果汇总表
        report.append("## 测试结果汇总")
        report.append("")
        report.append("| 方法 | 状态 | 处理时间 | 置信度 | 准确度 |")
        report.append("|------|------|----------|--------|--------|")
        
        for result in self.test_results:
            if result.success:
                accuracy = self.calculate_accuracy(result)
                status = "✅"
                time_str = f"{result.processing_time:.2f}s"
                conf_str = f"{result.confidence:.2f}"
                acc_str = f"{accuracy['overall_accuracy']:.2%}"
            else:
                status = "❌"
                time_str = "-"
                conf_str = "-"
                acc_str = "-"
            
            report.append(f"| {result.method_name} | {status} | {time_str} | {conf_str} | {acc_str} |")
        
        report.append("")
        
        # 详细结果
        for result in self.test_results:
            report.append(f"## {result.method_name}")
            report.append("-" * 40)
            
            if result.success:
                accuracy = self.calculate_accuracy(result)
                
                report.append(f"✅ **状态**: 成功")
                report.append(f"⏱️ **处理时间**: {result.processing_time:.2f}秒")
                report.append(f"🎯 **置信度**: {result.confidence:.2f}")
                report.append(f"📊 **准确度**: {accuracy['overall_accuracy']:.2%} ({accuracy['correct_fields']}/{accuracy['total_fields']})")
                report.append("")
                
                # 字段检查
                report.append("### 关键字段识别:")
                for key, expected in self.expected_data.items():
                    found = accuracy.get(f"{key}_found", False)
                    status = "✅" if found else "❌"
                    report.append(f"- {status} **{key}**: {expected}")
                
                report.append("")
                
                # 文本预览
                preview = result.extracted_text[:300] + "..." if len(result.extracted_text) > 300 else result.extracted_text
                report.append("### 提取文本预览:")
                report.append("```")
                report.append(preview)
                report.append("```")
                
            else:
                report.append(f"❌ **状态**: 失败")
                report.append(f"🚫 **错误**: {result.error}")
            
            report.append("")
        
        return "\\n".join(report)

async def main():
    """主函数"""
    image_path = "/home/ubuntu/upload/張家銓_1.jpg"
    
    if not Path(image_path).exists():
        print(f"❌ 图像文件不存在: {image_path}")
        return
    
    # 创建测试器
    tester = StableOCRTester(image_path)
    
    # 运行测试
    results = await tester.run_all_tests()
    
    # 显示结果
    print("\\n📊 测试完成！结果汇总:")
    print("=" * 80)
    
    for result in results:
        if result.success:
            accuracy = tester.calculate_accuracy(result)
            print(f"✅ {result.method_name}: {result.processing_time:.2f}s | {result.confidence:.2f} | {accuracy['overall_accuracy']:.2%}")
        else:
            print(f"❌ {result.method_name}: {result.error}")
    
    # 保存报告
    report = tester.generate_report()
    report_path = "/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/stable_ocr_test_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\\n📄 详细报告已保存: {report_path}")
    
    # 保存JSON结果
    results_data = []
    for result in results:
        accuracy = tester.calculate_accuracy(result)
        results_data.append({
            "method_name": result.method_name,
            "success": result.success,
            "processing_time": result.processing_time,
            "confidence": result.confidence,
            "accuracy": accuracy,
            "error": result.error
        })
    
    json_path = "/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/stable_ocr_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 JSON数据已保存: {json_path}")
    print("\\n🏁 OCR测试完成！")

if __name__ == "__main__":
    asyncio.run(main())

