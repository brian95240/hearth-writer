"""
Hearth Writer Inference Process
================================
Isolated multiprocessing worker for AI inference.

Key Design:
- Runs in separate OS process (bypasses Python GIL)
- Lazy imports prevent main thread blocking
- Supports grammar-constrained generation
- Mode-aware prompt augmentation

This process handles the "Hot Path" - active generation that requires GPU/CPU resources.
"""

import multiprocessing
from multiprocessing import Queue
import logging
import os
from typing import Dict, Any, Optional

# Configure logging for worker process
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - HEARTH-WORKER - %(message)s'
)


class InferenceWorker(multiprocessing.Process):
    """
    Isolated inference worker process.
    
    Runs completely separate from the main Flask process to avoid
    GIL contention during model loading and inference.
    """
    
    # Grammar file mappings
    GRAMMAR_FILES = {
        "screenplay": "./core/grammars/screenplay.gbnf",
        "comic": "./core/grammars/comic.gbnf",
        "playwright": "./core/grammars/playwright.gbnf",
        "lexile_simple": "./core/grammars/lexile_simple.gbnf",
    }
    
    # Mode-specific system prompts
    MODE_PROMPTS = {
        "prose": "You are a skilled author. Write vivid, engaging prose that captures the reader's imagination.",
        "screenplay": "You are a professional screenwriter. Format all output in proper Fountain screenplay format.",
        "comic": "You are a comic book writer. Include panel descriptions, visual cues, and dynamic dialogue.",
        "playwright": "You are a theatrical playwright. Include stage directions, blocking notes, and dramatic dialogue.",
        "children": "You are a children's book author. Use simple words (under 3 syllables) and engaging storytelling.",
        "game": "You are a game narrative designer. Support branching logic with {{conditional}} markers.",
    }
    
    def __init__(self, task_queue: Queue, result_queue: Queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.daemon = True  # Dies if main app dies
        self._llm = None
        self._current_model = None
    
    def _load_model(self, model_path: str = "./models/mistral-7b-quantized.gguf"):
        """
        Lazy load the LLM model.
        
        This is the heavy step - only called when needed.
        """
        if self._llm is None or self._current_model != model_path:
            logging.info(f"Loading model: {model_path}")
            
            try:
                from llama_cpp import Llama
                
                # Determine context size based on available memory
                n_ctx = 2048  # Default
                
                # Check for GPU layers (if available)
                n_gpu_layers = 0
                if os.environ.get("HEARTH_USE_GPU", "0") == "1":
                    n_gpu_layers = -1  # Use all available GPU layers
                
                self._llm = Llama(
                    model_path=model_path, 
                    n_ctx=n_ctx,
                    n_gpu_layers=n_gpu_layers,
                    verbose=False
                )
                self._current_model = model_path
                logging.info(f"Model loaded successfully (ctx={n_ctx}, gpu_layers={n_gpu_layers})")
                
            except Exception as e:
                logging.error(f"Model loading failed: {e}")
                raise
    
    def _get_grammar(self, mode: str, grammar_path: Optional[str] = None):
        """
        Load grammar constraints for the specified mode.
        
        Args:
            mode: Writing mode (screenplay, comic, etc.)
            grammar_path: Override path for custom grammar
            
        Returns:
            LlamaGrammar object or None
        """
        path = grammar_path or self.GRAMMAR_FILES.get(mode)
        
        if path and os.path.exists(path):
            try:
                from llama_cpp import LlamaGrammar
                return LlamaGrammar.from_file(path)
            except Exception as e:
                logging.warning(f"Grammar load failed ({path}): {e}")
        
        return None
    
    def _build_prompt(self, user_prompt: str, mode: str, 
                      context: Optional[str] = None,
                      shadow_nodes: Optional[str] = None) -> str:
        """
        Build the full prompt with mode-specific system prompt and context.
        
        Args:
            user_prompt: User's input text
            mode: Writing mode
            context: Retrieved context from series bible
            shadow_nodes: Shadow node data (Pro feature)
            
        Returns:
            Complete prompt string
        """
        parts = []
        
        # System prompt
        system_prompt = self.MODE_PROMPTS.get(mode, self.MODE_PROMPTS["prose"])
        parts.append(f"[SYSTEM]: {system_prompt}")
        
        # Context injection (if available)
        if context:
            parts.append(f"\n[CONTEXT]:\n{context}")
        
        # Shadow nodes (Pro feature - already validated by caller)
        if shadow_nodes:
            parts.append(f"\n[SHADOW NODES - OPEN LOOPS]:\n{shadow_nodes}")
        
        # User prompt
        parts.append(f"\n[USER]:\n{user_prompt}")
        
        # Response marker
        parts.append("\n[ASSISTANT]:")
        
        return "\n".join(parts)
    
    def _generate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute generation task.
        
        Args:
            task: Task dictionary with prompt, mode, etc.
            
        Returns:
            Generation result dictionary
        """
        # Ensure model is loaded
        model_path = task.get('model_path', "./models/mistral-7b-quantized.gguf")
        self._load_model(model_path)
        
        # Extract task parameters
        user_prompt = task.get('prompt', '')
        mode = task.get('mode', 'prose')
        max_tokens = task.get('max_tokens', 256)
        temperature = task.get('temperature', 0.7)
        
        # Build full prompt
        full_prompt = self._build_prompt(
            user_prompt=user_prompt,
            mode=mode,
            context=task.get('context'),
            shadow_nodes=task.get('shadow_nodes') if task.get('use_shadow_nodes') else None
        )
        
        # Load grammar (if applicable)
        grammar = self._get_grammar(mode, task.get('grammar_path'))
        
        # Execute inference
        logging.info(f"Generating ({mode} mode, {max_tokens} tokens)...")
        
        try:
            output = self._llm(
                full_prompt,
                grammar=grammar,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["[USER]:", "[SYSTEM]:", "\n\n\n"],  # Stop sequences
            )
            
            logging.info(f"Generation complete ({output.get('usage', {}).get('completion_tokens', 0)} tokens)")
            return output
            
        except Exception as e:
            logging.error(f"Generation error: {e}")
            return {"error": str(e), "choices": [{"text": f"Generation failed: {e}"}]}
    
    def _handle_batch_generate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle batch generation for branching narratives (Game Designer archetype).
        
        Generates multiple outcomes for {{conditional}} blocks.
        """
        prompts = task.get('prompts', [])
        results = []
        
        for i, prompt in enumerate(prompts):
            sub_task = {**task, 'prompt': prompt}
            result = self._generate(sub_task)
            results.append({
                'branch': i,
                'prompt': prompt,
                'output': result
            })
        
        return {'type': 'batch', 'results': results}
    
    def run(self):
        """
        Main worker loop.
        
        Continuously processes tasks from the queue until poison pill received.
        """
        logging.info("Inference Worker started")
        
        try:
            while True:
                task = self.task_queue.get()
                
                if task is None:
                    continue
                
                task_type = task.get('type', 'generate')
                
                if task_type == 'generate':
                    output = self._generate(task)
                    self.result_queue.put(output)
                    
                elif task_type == 'batch_generate':
                    output = self._handle_batch_generate(task)
                    self.result_queue.put(output)
                    
                elif task_type == 'reload_model':
                    # Force model reload (e.g., for LORA switching)
                    self._llm = None
                    self._current_model = None
                    model_path = task.get('model_path', "./models/mistral-7b-quantized.gguf")
                    self._load_model(model_path)
                    self.result_queue.put({'status': 'model_reloaded', 'path': model_path})
                    
                elif task_type == 'status':
                    self.result_queue.put({
                        'status': 'alive',
                        'model_loaded': self._llm is not None,
                        'current_model': self._current_model
                    })
                    
                elif task_type == 'poison_pill':
                    logging.info("Poison pill received. Shutting down worker.")
                    break
                    
                else:
                    logging.warning(f"Unknown task type: {task_type}")
                    self.result_queue.put({'error': f'Unknown task type: {task_type}'})
                    
        except Exception as e:
            logging.error(f"Worker fatal error: {e}")
            self.result_queue.put({"error": str(e)})
        
        finally:
            # Cleanup
            self._llm = None
            logging.info("Inference Worker terminated")
