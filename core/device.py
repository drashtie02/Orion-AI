import torch
import logging

logger = logging.getLogger(__name__)

class DeviceManager:
    def __init__(self):
        self._device = None
        self._device_name = None
        self._compute_capability = None
        self._initialize()
    
    def _initialize(self):
        if torch.cuda.is_available():
            try:
                self._device_name = torch.cuda.get_device_name(0)
                self._compute_capability = torch.cuda.get_device_capability(0)
                
                major, minor = self._compute_capability
                if major >= 12:
                    self._device = torch.device("cuda")
                    logger.info(f"GPU detected: {self._device_name} (sm_{major}{minor})")
                    self._enable_gpu_optimizations()
                else:
                    logger.warning(f"GPU compute capability {major}.{minor} < 12.0, falling back to CPU")
                    self._device = torch.device("cpu")
            except Exception as e:
                logger.warning(f"GPU initialization failed: {e}, falling back to CPU")
                self._device = torch.device("cpu")
        elif torch.backends.mps.is_available():
            self._device = torch.device("mps")
            self._device_name = "Apple MPS"
            logger.info("Apple MPS detected")
        else:
            self._device = torch.device("cpu")
            logger.info("Using CPU")
    
    def _enable_gpu_optimizations(self):
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        torch.set_float32_matmul_precision("high")
    
    def get_device(self) -> torch.device:
        return self._device
    
    def is_cuda(self) -> bool:
        return self._device.type == "cuda"
    
    def is_mps(self) -> bool:
        return self._device.type == "mps"
    
    def is_cpu(self) -> bool:
        return self._device.type == "cpu"
    
    def get_device_name(self) -> str:
        return self._device_name or "CPU"
    
    def get_compute_capability(self) -> tuple:
        return self._compute_capability

device_manager = DeviceManager()

def get_device():
    return device_manager.get_device().type
