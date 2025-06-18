"""
内存管理工具类
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MemoryUtils:
    """内存管理工具类"""
    
    def __init__(self):
        self.memory_info = {}
        
    async def get_memory_info(self) -> Dict[str, Any]:
        """
        获取内存信息
        
        Returns:
            Dict: 内存信息
        """
        try:
            memory_info = {
                "total_memory_gb": await self._get_total_memory(),
                "available_memory_gb": await self._get_available_memory(),
                "used_memory_gb": await self._get_used_memory(),
                "memory_usage_percent": await self._get_memory_usage_percent(),
                "gpu_memory": await self._get_gpu_memory(),
                "swap_info": await self._get_swap_info()
            }
            
            self.memory_info = memory_info
            return memory_info
            
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {"error": str(e)}
    
    async def _get_total_memory(self) -> float:
        """获取总内存 (GB)"""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024 ** 3)
        except ImportError:
            return await self._get_memory_fallback("total")
    
    async def _get_available_memory(self) -> float:
        """获取可用内存 (GB)"""
        try:
            import psutil
            return psutil.virtual_memory().available / (1024 ** 3)
        except ImportError:
            return await self._get_memory_fallback("available")
    
    async def _get_used_memory(self) -> float:
        """获取已用内存 (GB)"""
        try:
            import psutil
            return psutil.virtual_memory().used / (1024 ** 3)
        except ImportError:
            total = await self._get_total_memory()
            available = await self._get_available_memory()
            return total - available
    
    async def _get_memory_usage_percent(self) -> float:
        """获取内存使用百分比"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            total = await self._get_total_memory()
            used = await self._get_used_memory()
            return (used / total) * 100 if total > 0 else 0
    
    async def _get_gpu_memory(self) -> Dict[str, Any]:
        """获取GPU内存信息"""
        gpu_memory = {
            "cuda_available": False,
            "mps_available": False,
            "total_gpu_memory": 0,
            "used_gpu_memory": 0,
            "free_gpu_memory": 0
        }
        
        try:
            import torch
            
            # 检查CUDA
            if torch.cuda.is_available():
                gpu_memory["cuda_available"] = True
                gpu_memory["total_gpu_memory"] = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                gpu_memory["used_gpu_memory"] = torch.cuda.memory_allocated(0) / (1024 ** 3)
                gpu_memory["free_gpu_memory"] = gpu_memory["total_gpu_memory"] - gpu_memory["used_gpu_memory"]
            
            # 检查MPS (Apple Silicon)
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                gpu_memory["mps_available"] = True
                # MPS内存信息较难获取，使用估算
                gpu_memory["total_gpu_memory"] = 8.0  # 估算值
                
        except ImportError:
            pass
        
        return gpu_memory
    
    async def _get_swap_info(self) -> Dict[str, Any]:
        """获取交换空间信息"""
        try:
            import psutil
            swap = psutil.swap_memory()
            return {
                "total_swap_gb": swap.total / (1024 ** 3),
                "used_swap_gb": swap.used / (1024 ** 3),
                "free_swap_gb": swap.free / (1024 ** 3),
                "swap_percent": swap.percent
            }
        except ImportError:
            return {
                "total_swap_gb": 0,
                "used_swap_gb": 0,
                "free_swap_gb": 0,
                "swap_percent": 0
            }
    
    async def _get_memory_fallback(self, memory_type: str) -> float:
        """备用内存获取方法"""
        try:
            platform = sys.platform.lower()
            
            if platform.startswith("linux"):
                return await self._get_linux_memory(memory_type)
            elif platform == "darwin":
                return await self._get_macos_memory(memory_type)
            elif platform.startswith("win"):
                return await self._get_windows_memory(memory_type)
            else:
                return 8.0  # 默认值
                
        except Exception as e:
            logger.warning(f"备用内存获取失败: {e}")
            return 8.0
    
    async def _get_linux_memory(self, memory_type: str) -> float:
        """获取Linux内存信息"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    key, value = line.split(':')
                    meminfo[key.strip()] = int(value.split()[0]) * 1024  # 转换为字节
                
                if memory_type == "total":
                    return meminfo.get('MemTotal', 0) / (1024 ** 3)
                elif memory_type == "available":
                    return meminfo.get('MemAvailable', meminfo.get('MemFree', 0)) / (1024 ** 3)
                
        except Exception as e:
            logger.warning(f"Linux内存获取失败: {e}")
        
        return 8.0
    
    async def _get_macos_memory(self, memory_type: str) -> float:
        """获取macOS内存信息"""
        try:
            import subprocess
            
            if memory_type == "total":
                result = subprocess.run(['sysctl', 'hw.memsize'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    bytes_mem = int(result.stdout.split(':')[1].strip())
                    return bytes_mem / (1024 ** 3)
            
            # macOS的可用内存较难获取，使用vm_stat
            result = subprocess.run(['vm_stat'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # 解析vm_stat输出（这里简化处理）
                return 8.0  # 简化返回
                
        except Exception as e:
            logger.warning(f"macOS内存获取失败: {e}")
        
        return 8.0
    
    async def _get_windows_memory(self, memory_type: str) -> float:
        """获取Windows内存信息"""
        try:
            import subprocess
            
            # 使用wmic命令
            result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    bytes_mem = int(lines[1].strip())
                    return bytes_mem / (1024 ** 3)
                    
        except Exception as e:
            logger.warning(f"Windows内存获取失败: {e}")
        
        return 8.0
    
    def check_memory_sufficient(self, required_gb: float) -> bool:
        """
        检查内存是否足够
        
        Args:
            required_gb: 需要的内存 (GB)
            
        Returns:
            bool: 内存是否足够
        """
        if not self.memory_info:
            return False
        
        available = self.memory_info.get("available_memory_gb", 0)
        return available >= required_gb
    
    def get_memory_recommendation(self) -> str:
        """
        获取内存使用建议
        
        Returns:
            str: 建议
        """
        if not self.memory_info:
            return "无法获取内存信息"
        
        usage_percent = self.memory_info.get("memory_usage_percent", 0)
        available_gb = self.memory_info.get("available_memory_gb", 0)
        
        if usage_percent > 90:
            return "内存使用率过高，建议使用云端模式"
        elif usage_percent > 80:
            return "内存使用率较高，建议使用轻量级模型"
        elif available_gb < 4:
            return "可用内存不足4GB，建议使用云端模式"
        elif available_gb < 8:
            return "可用内存不足8GB，建议使用小型模型"
        else:
            return "内存充足，可以使用本地模型"

