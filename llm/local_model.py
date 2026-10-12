from typing import Dict
from llm.base_model import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from core.device import device_manager
from core.config import config

class LocalModel(BaseModel):
    def __init__(self, model_name: str, device: str = 'auto', cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0):
        super().__init__()
        self.model_name = model_name
        self.cost_per_1k_input_tokens = cost_per_1k_input
        self.cost_per_1k_output_tokens = cost_per_1k_output
        self.device = device_manager.get_device()
        self.use_mixed_precision = config.use_mixed_precision and device_manager.is_cuda()
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if self.use_mixed_precision else torch.float32)
        self.model = self.model.to(self.device)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate(self, prompt: str) -> Dict:
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        input_tokens = inputs['input_ids'].shape[1]
        
        with torch.no_grad():
            if self.use_mixed_precision:
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=512,
                        temperature=0.0,
                        do_sample=False,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
            else:
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.0,
                    do_sample=False,
                    pad_token_id=self.tokenizer.pad_token_id
                )
        
        output_tokens = outputs.shape[1] - input_tokens
        generated_text = self.tokenizer.decode(outputs[0][input_tokens:], skip_special_tokens=True)
        
        return {
            'text': generated_text,
            'tokens_input': input_tokens,
            'tokens_output': output_tokens,
            'model_name': self.model_name
        }
    
    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
