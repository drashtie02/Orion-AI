#!/usr/bin/env python3
import sys
import torch

def validate_environment():
    print("=" * 80)
    print("OrionAI Environment Validation")
    print("=" * 80)
    
    print(f"\nPyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"cuDNN version: {torch.backends.cudnn.version()}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"\nGPU {i}: {torch.cuda.get_device_name(i)}")
            capability = torch.cuda.get_device_capability(i)
            print(f"  Compute capability: {capability[0]}.{capability[1]} (sm_{capability[0]}{capability[1]})")
            
            if capability[0] < 12:
                print(f"  WARNING: Compute capability {capability[0]}.{capability[1]} < 12.0")
                print(f"  RTX 5050 requires sm_120 or higher")
                print(f"  System will fall back to CPU")
            else:
                print(f"  ✓ Compatible with RTX 5050 (sm_120)")
    else:
        print("\nNo CUDA GPU detected. System will run on CPU.")
    
    print("\n" + "=" * 80)
    print("Recommended PyTorch Installation:")
    print("=" * 80)
    print("\nFor CUDA 12.x (RTX 5050):")
    print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    print("\nFor CPU only:")
    print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    validate_environment()
