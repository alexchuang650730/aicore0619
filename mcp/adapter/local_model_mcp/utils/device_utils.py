"""
设备工具类 - 检测本地环境条件
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class DeviceUtils:
    """设备检测工具类"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_wsl = self._detect_wsl()
        self.device_info = {}
        
    async def detect_device(self) -> Dict[str, Any]:
        """
        检测设备环境
        
        Returns:
            Dict: 设备信息
        """
        try:
            device_info = {
                "platform": self.platform,
                "is_wsl": self.is_wsl,
                "gpu_available": await self._check_gpu_available(),
                "gpu_type": await self._detect_gpu_type(),
                "cpu_cores": os.cpu_count(),
                "python_version": sys.version,
                "architecture": platform.machine(),
                "recommended_mode": "local"  # 默认推荐本地模式
            }
            
            # 根据检测结果推荐运行模式
            device_info["recommended_mode"] = await self._recommend_mode(device_info)
            
            self.device_info = device_info
            logger.info(f"设备检测完成: {device_info}")
            
            return device_info
            
        except Exception as e:
            logger.error(f"设备检测失败: {e}")
            return {
                "platform": self.platform,
                "error": str(e),
                "recommended_mode": "cloud"  # 检测失败时推荐云端模式
            }
    
    def _detect_wsl(self) -> bool:
        """检测是否在WSL环境中运行"""
        try:
            if self.platform == "linux":
                with open('/proc/version', 'r') as f:
                    return 'microsoft' in f.read().lower()
        except:
            pass
        return False
    
    async def _check_gpu_available(self) -> bool:
        """检查GPU是否可用"""
        try:
            # 检查CUDA
            if await self._check_cuda():
                return True
            
            # 检查MPS (Apple Silicon)
            if await self._check_mps():
                return True
            
            # 检查其他GPU
            if await self._check_other_gpu():
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"GPU检测失败: {e}")
            return False
    
    async def _check_cuda(self) -> bool:
        """检查CUDA是否可用"""
        try:
            # 检查nvidia-smi命令
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                logger.info("检测到NVIDIA GPU")
                return True
        except:
            pass
        
        # 检查Python torch CUDA
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"CUDA可用，设备数量: {torch.cuda.device_count()}")
                return True
        except ImportError:
            pass
        
        return False
    
    async def _check_mps(self) -> bool:
        """检查MPS (Apple Silicon) 是否可用"""
        try:
            if self.platform == "darwin":  # macOS
                import torch
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    logger.info("检测到Apple Silicon MPS")
                    return True
        except ImportError:
            pass
        
        return False
    
    async def _check_other_gpu(self) -> bool:
        """检查其他GPU"""
        try:
            # 检查AMD GPU
            if self.platform == "linux":
                result = subprocess.run(['lspci'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=10)
                if result.returncode == 0 and 'VGA' in result.stdout:
                    if any(vendor in result.stdout.lower() for vendor in ['amd', 'radeon']):
                        logger.info("检测到AMD GPU")
                        return True
        except:
            pass
        
        return False
    
    async def _detect_gpu_type(self) -> str:
        """检测GPU类型"""
        try:
            # NVIDIA GPU
            if await self._check_cuda():
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        return f"NVIDIA {result.stdout.strip()}"
                except:
                    pass
                return "NVIDIA GPU"
            
            # Apple Silicon
            if await self._check_mps():
                return "Apple Silicon MPS"
            
            # AMD GPU
            if self.platform == "linux":
                try:
                    result = subprocess.run(['lspci'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'VGA' in line and any(vendor in line.lower() for vendor in ['amd', 'radeon']):
                                return f"AMD {line.split(':')[-1].strip()}"
                except:
                    pass
            
            return "CPU Only"
            
        except Exception as e:
            logger.warning(f"GPU类型检测失败: {e}")
            return "Unknown"
    
    async def _recommend_mode(self, device_info: Dict[str, Any]) -> str:
        """
        根据设备信息推荐运行模式
        
        Args:
            device_info: 设备信息
            
        Returns:
            str: 推荐模式 ("local" 或 "cloud")
        """
        try:
            # 检查内存
            memory_gb = await self._get_available_memory()
            
            # 决策逻辑
            if device_info.get("gpu_available", False):
                # 有GPU的情况
                if memory_gb >= 16:  # 16GB以上内存
                    return "local"
                elif memory_gb >= 8:  # 8-16GB内存
                    if "NVIDIA" in device_info.get("gpu_type", ""):
                        return "local"  # NVIDIA GPU优先本地
                    elif "Apple Silicon" in device_info.get("gpu_type", ""):
                        return "local"  # Apple Silicon优先本地
                    else:
                        return "hybrid"  # 其他GPU混合模式
                else:
                    return "cloud"  # 内存不足，云端模式
            else:
                # 无GPU的情况
                if memory_gb >= 32:  # 32GB以上内存，CPU也可以跑
                    return "local"
                elif memory_gb >= 16:  # 16GB内存，混合模式
                    return "hybrid"
                else:
                    return "cloud"  # 内存不足，云端模式
            
        except Exception as e:
            logger.warning(f"模式推荐失败: {e}")
            return "cloud"  # 出错时默认云端模式
    
    async def _get_available_memory(self) -> float:
        """获取可用内存 (GB)"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.total / (1024 ** 3)  # 转换为GB
        except ImportError:
            # 如果没有psutil，尝试其他方法
            try:
                if self.platform == "linux":
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if line.startswith('MemTotal:'):
                                kb = int(line.split()[1])
                                return kb / (1024 ** 2)  # 转换为GB
                elif self.platform == "darwin":  # macOS
                    result = subprocess.run(['sysctl', 'hw.memsize'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=5)
                    if result.returncode == 0:
                        bytes_mem = int(result.stdout.split(':')[1].strip())
                        return bytes_mem / (1024 ** 3)  # 转换为GB
            except:
                pass
            
            return 8.0  # 默认假设8GB
    
    def get_optimal_device(self) -> str:
        """获取最优设备"""
        if not self.device_info:
            return "cpu"
        
        if self.device_info.get("gpu_available", False):
            gpu_type = self.device_info.get("gpu_type", "")
            if "NVIDIA" in gpu_type:
                return "cuda"
            elif "Apple Silicon" in gpu_type:
                return "mps"
            else:
                return "cpu"
        else:
            return "cpu"
    
    def should_use_local_model(self, model_name: str = None) -> bool:
        """
        判断是否应该使用本地模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 是否使用本地模型
        """
        if not self.device_info:
            return False
        
        recommended_mode = self.device_info.get("recommended_mode", "cloud")
        
        if recommended_mode == "local":
            return True
        elif recommended_mode == "cloud":
            return False
        elif recommended_mode == "hybrid":
            # 混合模式下，根据模型类型决定
            if model_name == "qwen" and self.device_info.get("gpu_available", False):
                return True  # Qwen在有GPU时优先本地
            elif model_name == "mistral" and "NVIDIA" in self.device_info.get("gpu_type", ""):
                return True  # Mistral在NVIDIA GPU时优先本地
            else:
                return False
        
        return False

