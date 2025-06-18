"""
Mistral OCR LLM引擎 - 基于Mistral的智能OCR处理
"""

import base64
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import io
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class MistralOCRResult:
    """Mistral OCR结果"""
    text: str
    confidence: float
    processing_time: float
    structured_data: Dict[str, Any]
    table_data: List[List[str]]
    metadata: Dict[str, Any]

class MistralOCREngine:
    """Mistral OCR LLM引擎"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = "mistralai/mistral-nemo"  # Mistral 12B OCR模型
        self.session = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    def _encode_image(self, image_path: str) -> str:
        """将图像编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_ocr_prompt(self, task_type: str = "comprehensive") -> str:
        """创建OCR提示词"""
        
        base_prompt = """你是一个专业的OCR专家，请仔细分析这张图像并提取所有文本内容。

请按照以下要求处理：

1. **文本识别**：
   - 识别所有可见的文字，包括印刷体和手写体
   - 保持原始的文本布局和格式
   - 对于不确定的字符，请标注[?]

2. **结构化输出**：
   - 如果是表格，请保持表格结构
   - 如果是表单，请识别字段名和对应值
   - 保持段落和行的分隔

3. **特殊处理**：
   - 日期格式：保持原始格式
   - 数字：确保准确性
   - 签名和手写：尽力识别

请以JSON格式返回结果：
```json
{
  "extracted_text": "完整的文本内容",
  "confidence": 0.95,
  "document_type": "表单/表格/文档",
  "structured_data": {
    "fields": {},
    "tables": [],
    "metadata": {}
  }
}
```"""

        if task_type == "table_focus":
            base_prompt += """

**特别注意**：这是一个包含表格的文档，请特别关注：
- 表格的行列结构
- 单元格的对齐关系
- 表头和数据的区分
- 合并单元格的处理"""

        elif task_type == "handwriting_focus":
            base_prompt += """

**特别注意**：这个文档包含手写内容，请特别关注：
- 手写字迹的识别
- 与印刷体的区分
- 手写数字和文字的准确性
- 签名和特殊标记"""

        elif task_type == "form_focus":
            base_prompt += """

**特别注意**：这是一个表单文档，请特别关注：
- 字段名称和对应的填写内容
- 复选框和选择项的状态
- 表单的逻辑结构
- 必填项和可选项的区分"""

        return base_prompt
    
    async def process_image(self, 
                          image_path: str, 
                          task_type: str = "comprehensive",
                          max_retries: int = 3) -> MistralOCRResult:
        """
        使用Mistral处理图像OCR
        
        Args:
            image_path: 图像路径
            task_type: 任务类型 (comprehensive/table_focus/handwriting_focus/form_focus)
            max_retries: 最大重试次数
            
        Returns:
            MistralOCRResult: OCR结果
        """
        logger.info(f"🤖 Mistral OCR处理: {image_path} (任务类型: {task_type})")
        
        start_time = time.time()
        
        # 编码图像
        try:
            image_base64 = self._encode_image(image_path)
        except Exception as e:
            logger.error(f"❌ 图像编码失败: {e}")
            raise
        
        # 创建提示词
        prompt = self._create_ocr_prompt(task_type)
        
        # 构建请求
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
        
        # 发送请求
        for attempt in range(max_retries):
            try:
                result = await self._send_request(messages)
                processing_time = time.time() - start_time
                
                # 解析结果
                ocr_result = self._parse_response(result, processing_time)
                
                logger.info(f"✅ Mistral OCR完成: {processing_time:.2f}s, 置信度: {ocr_result.confidence:.2f}")
                return ocr_result
                
            except Exception as e:
                logger.warning(f"⚠️ Mistral OCR尝试 {attempt + 1} 失败: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数退避
        
        raise Exception("Mistral OCR处理失败")
    
    async def _send_request(self, messages: List[Dict]) -> str:
        """发送API请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://powerautomation.ai",  # OpenRouter要求
            "X-Title": "PowerAutomation OCR"  # OpenRouter要求
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.1  # 低温度确保一致性
        }
        
        if not self.session:
            raise Exception("Session未初始化，请使用async with语句")
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API请求失败: {response.status} - {error_text}")
            
            result = await response.json()
            return result["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str, processing_time: float) -> MistralOCRResult:
        """解析Mistral响应"""
        try:
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                # 如果没有JSON格式，创建基本结构
                data = {
                    "extracted_text": response,
                    "confidence": 0.8,
                    "document_type": "unknown",
                    "structured_data": {}
                }
            
            # 提取表格数据
            table_data = []
            if "structured_data" in data and "tables" in data["structured_data"]:
                table_data = data["structured_data"]["tables"]
            
            return MistralOCRResult(
                text=data.get("extracted_text", response),
                confidence=data.get("confidence", 0.8),
                processing_time=processing_time,
                structured_data=data.get("structured_data", {}),
                table_data=table_data,
                metadata={
                    "document_type": data.get("document_type", "unknown"),
                    "model": self.model_name,
                    "task_type": "mistral_ocr"
                }
            )
            
        except json.JSONDecodeError:
            logger.warning("⚠️ JSON解析失败，使用原始文本")
            return MistralOCRResult(
                text=response,
                confidence=0.7,
                processing_time=processing_time,
                structured_data={},
                table_data=[],
                metadata={
                    "document_type": "unknown",
                    "model": self.model_name,
                    "task_type": "mistral_ocr",
                    "parse_error": True
                }
            )
    
    async def batch_process(self, 
                          image_paths: List[str], 
                          task_type: str = "comprehensive") -> List[MistralOCRResult]:
        """批量处理图像"""
        logger.info(f"📦 Mistral批量OCR处理: {len(image_paths)}张图像")
        
        results = []
        for i, image_path in enumerate(image_paths):
            logger.info(f"🔄 处理进度: {i+1}/{len(image_paths)}")
            try:
                result = await self.process_image(image_path, task_type)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ 图像处理失败 {image_path}: {e}")
                # 创建错误结果
                error_result = MistralOCRResult(
                    text="",
                    confidence=0.0,
                    processing_time=0.0,
                    structured_data={},
                    table_data=[],
                    metadata={"error": str(e)}
                )
                results.append(error_result)
        
        return results
    
    def compare_with_traditional_ocr(self, 
                                   mistral_result: MistralOCRResult,
                                   traditional_result: str) -> Dict[str, Any]:
        """对比Mistral OCR和传统OCR结果"""
        
        # 计算文本长度对比
        mistral_length = len(mistral_result.text.strip())
        traditional_length = len(traditional_result.strip())
        
        # 计算相似度（简单的字符重叠）
        mistral_chars = set(mistral_result.text.lower())
        traditional_chars = set(traditional_result.lower())
        
        if mistral_chars or traditional_chars:
            similarity = len(mistral_chars & traditional_chars) / len(mistral_chars | traditional_chars)
        else:
            similarity = 0.0
        
        # 分析结构化数据优势
        has_structured_data = bool(mistral_result.structured_data)
        has_table_data = bool(mistral_result.table_data)
        
        comparison = {
            "text_length_comparison": {
                "mistral": mistral_length,
                "traditional": traditional_length,
                "difference": mistral_length - traditional_length,
                "improvement_ratio": mistral_length / traditional_length if traditional_length > 0 else float('inf')
            },
            "similarity_score": similarity,
            "mistral_advantages": {
                "has_structured_data": has_structured_data,
                "has_table_data": has_table_data,
                "confidence_score": mistral_result.confidence,
                "processing_time": mistral_result.processing_time
            },
            "quality_assessment": {
                "mistral_quality": self._assess_text_quality(mistral_result.text),
                "traditional_quality": self._assess_text_quality(traditional_result)
            }
        }
        
        return comparison
    
    def _assess_text_quality(self, text: str) -> Dict[str, float]:
        """评估文本质量"""
        import re
        
        if not text.strip():
            return {"overall": 0.0, "completeness": 0.0, "structure": 0.0}
        
        # 完整性评分（基于长度和内容丰富度）
        completeness = min(len(text) / 1000, 1.0)  # 假设1000字符为完整
        
        # 结构性评分（基于格式和组织）
        has_structure = bool(re.search(r'\n\s*\n', text))  # 有段落分隔
        has_numbers = bool(re.search(r'\d', text))  # 有数字
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))  # 有中文
        
        structure = (has_structure + has_numbers + has_chinese) / 3
        
        # 整体质量
        overall = (completeness + structure) / 2
        
        return {
            "overall": overall,
            "completeness": completeness,
            "structure": structure
        }

# 测试函数
async def test_mistral_ocr():
    """测试Mistral OCR功能"""
    print("🤖 测试Mistral OCR LLM引擎")
    print("=" * 60)
    
    # 测试图像路径
    test_image = "/home/ubuntu/upload/張家銓_1.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        return
    
    # API密钥（从配置文件读取）
    api_key = "Po6zoCs8d8CpmtvGZhih7uxpCwebA6K6"
    
    try:
        async with MistralOCREngine(api_key) as mistral_ocr:
            
            # 测试不同任务类型
            task_types = [
                ("comprehensive", "综合OCR"),
                ("table_focus", "表格重点"),
                ("handwriting_focus", "手写重点"),
                ("form_focus", "表单重点")
            ]
            
            results = {}
            
            for task_type, description in task_types:
                print(f"\n🧪 测试: {description} ({task_type})")
                print("-" * 40)
                
                try:
                    result = await mistral_ocr.process_image(test_image, task_type)
                    
                    print(f"✅ 处理完成:")
                    print(f"   ⏱️ 时间: {result.processing_time:.2f}s")
                    print(f"   📊 置信度: {result.confidence:.2f}")
                    print(f"   📝 文本长度: {len(result.text)}")
                    print(f"   📋 文档类型: {result.metadata.get('document_type', 'unknown')}")
                    print(f"   🗂️ 结构化数据: {'是' if result.structured_data else '否'}")
                    print(f"   📊 表格数据: {'是' if result.table_data else '否'}")
                    print(f"   📄 文本预览: {result.text[:100]}...")
                    
                    results[task_type] = result
                    
                except Exception as e:
                    print(f"❌ 测试失败: {e}")
                    results[task_type] = None
            
            # 保存结果
            print(f"\n💾 保存测试结果...")
            with open("mistral_ocr_test_results.json", "w", encoding="utf-8") as f:
                test_data = {}
                for task_type, result in results.items():
                    if result:
                        test_data[task_type] = {
                            "text": result.text,
                            "confidence": result.confidence,
                            "processing_time": result.processing_time,
                            "structured_data": result.structured_data,
                            "table_data": result.table_data,
                            "metadata": result.metadata
                        }
                    else:
                        test_data[task_type] = {"error": "处理失败"}
                
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            
            print(f"📄 结果已保存: mistral_ocr_test_results.json")
            
    except Exception as e:
        print(f"❌ Mistral OCR测试失败: {e}")

if __name__ == "__main__":
    import os
    asyncio.run(test_mistral_ocr())

