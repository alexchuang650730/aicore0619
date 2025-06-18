#!/usr/bin/env python3
"""
保险表单OCR准确度测试套件
独立测试不同OCR方法的文字识别准确度和表格正确性
"""

import asyncio
import logging
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

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

class InsuranceFormOCRTester:
    """保险表单OCR测试器"""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.test_results = []
        
        # 预期的关键信息（用于准确度验证）
        self.expected_data = {
            "print_number": "900829",
            "print_time": "2025/06/09 02:14:42",
            "form_title": "台银人壽利率變動型人壽保險要保書",
            "barcode1": "A910050",
            "barcode2": "HR60334699",
            "insured_name": "沈宗銘",
            "gender": "男",
            "birth_date": "87年5月29日",
            "age": "26",
            "address": "台中市東勢區40號5樓",
            "insurance_name": "安心傳家利率變動型終身壽險",
            "payment_period": "20年",
            "insurance_amount": "30万元",
            "premium": "8930元",
            "additional_premium": "524元",
            "additional_amount": "5万元"
        }
    
    async def test_mistral_ocr(self) -> OCRTestResult:
        """测试Mistral OCR"""
        print("🤖 测试Mistral Pixtral 12B OCR...")
        
        try:
            import aiohttp
            import base64
            
            # 配置
            api_key = "fLDmWp2L4HZ9MRxL1AfY8cqW5zxq3tumnew"
            base_url = "https://openrouter.ai/api/v1"
            model_name = "mistralai/pixtral-12b"
            
            # 编码图像
            with open(self.image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 专门的保险表单OCR提示词
            prompt = """你是专业的保险表单OCR专家。请仔细分析这张台湾保险表单，提取所有文字内容。

重点关注：
1. **表单头部**: 列印者、时间、条码
2. **被保险人信息**: 姓名、性别、出生日期、地址
3. **保险详情**: 保险名称、金额、期间、保费
4. **表格数据**: 所有表格中的数字和文字
5. **手写内容**: 准确识别手写文字

请以JSON格式返回：
```json
{
  "print_info": {
    "print_number": "",
    "print_time": "",
    "barcode1": "",
    "barcode2": ""
  },
  "form_title": "",
  "insured_person": {
    "name": "",
    "gender": "",
    "birth_date": "",
    "age": "",
    "address": ""
  },
  "insurance_details": {
    "insurance_name": "",
    "payment_period": "",
    "insurance_amount": "",
    "premium": ""
  },
  "additional_contracts": [
    {
      "name": "",
      "amount": "",
      "premium": ""
    }
  ],
  "extracted_text": "完整的文本内容",
  "confidence": 0.95
}
```"""
            
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
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://powerautomation.ai",
                "X-Title": "Insurance Form OCR Test"
            }
            
            data = {
                "model": model_name,
                "messages": messages,
                "max_tokens": 6000,
                "temperature": 0.1
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=180)
                ) as response:
                    
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # 尝试解析JSON
                        try:
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            
                            if json_start != -1 and json_end > json_start:
                                json_content = content[json_start:json_end]
                                structured_data = json.loads(json_content)
                                confidence = structured_data.get('confidence', 0.9)
                            else:
                                structured_data = {"raw_content": content}
                                confidence = 0.8
                        
                        except json.JSONDecodeError:
                            structured_data = {"raw_content": content}
                            confidence = 0.7
                        
                        return OCRTestResult(
                            method_name="Mistral Pixtral 12B",
                            processing_time=processing_time,
                            extracted_text=content,
                            confidence=confidence,
                            structured_data=structured_data,
                            success=True
                        )
                    
                    else:
                        error_text = await response.text()
                        return OCRTestResult(
                            method_name="Mistral Pixtral 12B",
                            processing_time=processing_time,
                            extracted_text="",
                            confidence=0.0,
                            structured_data={},
                            success=False,
                            error=f"API Error {response.status}: {error_text}"
                        )
        
        except Exception as e:
            return OCRTestResult(
                method_name="Mistral Pixtral 12B",
                processing_time=0.0,
                extracted_text="",
                confidence=0.0,
                structured_data={},
                success=False,
                error=str(e)
            )
    
    def test_traditional_ocr_simulation(self) -> OCRTestResult:
        """模拟传统OCR测试（Tesseract + EasyOCR）"""
        print("🔧 模拟传统OCR测试...")
        
        # 模拟传统OCR的典型结果
        simulated_text = """900829 2025/06/09 02:14:42
台银人壽利率變動型人壽保險要保書(傳統通路 A)
106.08.15壽險權字第1060540204號函備查
112.09.01壽險權字第1120540298號函備查

姓名: 沈宗銘
性别: 男
出生日期: 民國 87年 5月 29日
保險年齡: 26歲
住所: 台中市東勢區40號5樓

保險名稱: 安心傳家利率變動型終身壽險(定期給付型)
繳費年期: 20年
主契約保險費: 8930元
保險金額: 30万元

附加契約: 銀心自費醫療保險附約
保險金額: 5万元
保險費: 524元"""
        
        structured_data = {
            "print_info": {
                "print_number": "900829",
                "print_time": "2025/06/09 02:14:42"
            },
            "insured_person": {
                "name": "沈宗銘",
                "gender": "男",
                "birth_date": "87年5月29日",
                "age": "26",
                "address": "台中市東勢區40號5樓"
            },
            "insurance_details": {
                "insurance_name": "安心傳家利率變動型終身壽險",
                "payment_period": "20年",
                "premium": "8930元"
            }
        }
        
        return OCRTestResult(
            method_name="Traditional OCR (Simulated)",
            processing_time=2.5,
            extracted_text=simulated_text,
            confidence=0.85,
            structured_data=structured_data,
            success=True
        )
    
    def calculate_accuracy(self, result: OCRTestResult) -> Dict[str, float]:
        """计算准确度指标"""
        accuracy_scores = {}
        
        if not result.success:
            return {"overall_accuracy": 0.0}
        
        # 检查关键字段的准确性
        correct_fields = 0
        total_fields = len(self.expected_data)
        
        extracted_data = result.structured_data
        
        # 检查各个字段
        for key, expected_value in self.expected_data.items():
            found = False
            
            # 在结构化数据中查找
            if self._find_value_in_data(extracted_data, expected_value):
                correct_fields += 1
                found = True
            
            # 在原始文本中查找
            elif expected_value.lower() in result.extracted_text.lower():
                correct_fields += 1
                found = True
            
            accuracy_scores[f"{key}_found"] = found
        
        # 计算总体准确度
        overall_accuracy = correct_fields / total_fields
        accuracy_scores["overall_accuracy"] = overall_accuracy
        accuracy_scores["correct_fields"] = correct_fields
        accuracy_scores["total_fields"] = total_fields
        
        return accuracy_scores
    
    def _find_value_in_data(self, data: Dict, value: str) -> bool:
        """在嵌套字典中查找值"""
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, str) and value in v:
                    return True
                elif isinstance(v, dict) and self._find_value_in_data(v, value):
                    return True
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict) and self._find_value_in_data(item, value):
                            return True
        return False
    
    async def run_all_tests(self) -> List[OCRTestResult]:
        """运行所有OCR测试"""
        print("🧪 开始保险表单OCR准确度测试")
        print("=" * 80)
        
        # 测试Mistral OCR
        mistral_result = await self.test_mistral_ocr()
        self.test_results.append(mistral_result)
        
        # 测试传统OCR（模拟）
        traditional_result = self.test_traditional_ocr_simulation()
        self.test_results.append(traditional_result)
        
        return self.test_results
    
    def generate_accuracy_report(self) -> str:
        """生成准确度报告"""
        report = []
        report.append("# 保险表单OCR准确度测试报告")
        report.append("=" * 60)
        report.append("")
        
        for result in self.test_results:
            report.append(f"## {result.method_name}")
            report.append("-" * 40)
            
            if result.success:
                accuracy = self.calculate_accuracy(result)
                
                report.append(f"✅ **测试状态**: 成功")
                report.append(f"⏱️ **处理时间**: {result.processing_time:.2f}秒")
                report.append(f"🎯 **置信度**: {result.confidence:.2f}")
                report.append(f"📊 **总体准确度**: {accuracy['overall_accuracy']:.2%}")
                report.append(f"📝 **正确字段**: {accuracy['correct_fields']}/{accuracy['total_fields']}")
                report.append("")
                
                # 详细字段检查
                report.append("### 字段准确性检查:")
                for key, expected in self.expected_data.items():
                    found = accuracy.get(f"{key}_found", False)
                    status = "✅" if found else "❌"
                    report.append(f"- {status} **{key}**: {expected}")
                
                report.append("")
                
                # 文本预览
                preview = result.extracted_text[:300] + "..." if len(result.extracted_text) > 300 else result.extracted_text
                report.append(f"### 提取文本预览:")
                report.append(f"```")
                report.append(preview)
                report.append(f"```")
                
            else:
                report.append(f"❌ **测试状态**: 失败")
                report.append(f"🚫 **错误信息**: {result.error}")
            
            report.append("")
            report.append("")
        
        return "\\n".join(report)

async def main():
    """主测试函数"""
    
    # 测试图像路径
    image_path = "/home/ubuntu/upload/張家銓_1.jpg"
    
    if not Path(image_path).exists():
        print(f"❌ 测试图像不存在: {image_path}")
        return
    
    # 创建测试器
    tester = InsuranceFormOCRTester(image_path)
    
    # 运行测试
    results = await tester.run_all_tests()
    
    # 显示结果
    print("\\n📊 测试结果汇总:")
    print("=" * 80)
    
    for result in results:
        print(f"\\n🔍 {result.method_name}:")
        if result.success:
            accuracy = tester.calculate_accuracy(result)
            print(f"  ✅ 成功 | ⏱️ {result.processing_time:.2f}s | 🎯 {result.confidence:.2f} | 📊 {accuracy['overall_accuracy']:.2%}")
        else:
            print(f"  ❌ 失败: {result.error}")
    
    # 生成详细报告
    report = tester.generate_accuracy_report()
    
    # 保存报告
    report_path = "/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/insurance_ocr_accuracy_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\\n📄 详细报告已保存到: {report_path}")
    
    # 保存测试结果JSON
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
    
    json_path = "/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/insurance_ocr_test_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 测试数据已保存到: {json_path}")
    print("\\n🏁 保险表单OCR准确度测试完成！")

if __name__ == "__main__":
    asyncio.run(main())

