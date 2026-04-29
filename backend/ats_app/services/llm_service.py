import json
import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key=None, model=None):
        self.provider = getattr(settings, 'LLM_PROVIDER', 'ollama').lower()
        
        # Use user-specific API key and model if provided, otherwise use defaults
        user_api_key = api_key if api_key and api_key.strip() else None
        user_model = model if model and model.strip() else None
        
        if self.provider == 'openrouter':
            self.base_url = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
            self.model = user_model if user_model else getattr(settings, 'OPENROUTER_MODEL')
            self.api_key = user_api_key if user_api_key else getattr(settings, 'OPENROUTER_API_KEY', '')
            self.max_tokens = getattr(settings, 'OPENROUTER_MAX_TOKENS', 32768)
            logger.info(f"LLMService initialized with OpenRouter - Model: {self.model}, API Key: {'Custom' if user_api_key else 'Default'}")
        else:  # Default to Ollama
            self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
            self.model = user_model if user_model else getattr(settings, 'OLLAMA_MODEL', 'llama3.1')
            self.max_tokens = getattr(settings, 'OLLAMA_MAX_TOKENS', 32768)
            logger.info(f"LLMService initialized with Ollama - Model: {self.model}")

    def generate(self, prompt: str, system: str = "", temperature: float = None) -> str:
        if self.provider == 'openrouter':
            return self._generate_openrouter(prompt, system, temperature)
        else:
            return self._generate_ollama(prompt, system, temperature)
    
    def _generate_ollama(self, prompt: str, system: str = "", temperature: float = None) -> str:
        """Generate response using Ollama API."""
        options = {
            "num_predict": self.max_tokens,  # Increased to handle longer responses
        }
        if temperature is not None:
            options["temperature"] = temperature
        else:
            options["temperature"] = 0.3  # Default temperature
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": options,
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=600,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise
    
    def _generate_openrouter(self, prompt: str, system: str = "", temperature: float = None) -> str:
        """Generate response using OpenRouter API (OpenAI-compatible)."""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured in settings")
        
        if temperature is None:
            temperature = 0.3  # Default temperature
        
        payload = {
            "model": self.model,
            "messages": [],
            "temperature": temperature,
            "max_tokens": self.max_tokens,
        }
        
        # Add system message if provided
        if system:
            payload["messages"].append({
                "role": "system",
                "content": system
            })
        
        # Add user prompt
        payload["messages"].append({
            "role": "user",
            "content": prompt
        })
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",  # Optional: Helps OpenRouter know your app
            "X-Title": "ATS-Agentic"  # Optional: App name
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=600,
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract response from OpenAI-compatible format
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Unexpected OpenRouter response format: {data}")
                raise ValueError("Invalid response format from OpenRouter")
        except requests.RequestException as e:
            logger.error(f"OpenRouter request failed: {e}")
            raise

    def _sanitize_json_string(self, raw: str) -> str:
        """
        Sanitize JSON string to handle invalid escape sequences.
        
        Args:
            raw: The raw JSON string to sanitize
            
        Returns:
            Sanitized JSON string
        """
        # Simplified approach: Just return original for now
        # The complex sanitization was causing issues
        # If we need this in future, we can implement a cleaner version
        return raw

    def _is_truncated_json(self, json_str: str) -> bool:
        """
        Detect if JSON string is truncated.
        
        Args:
            json_str: The JSON string to check
            
        Returns:
            True if JSON appears truncated, False otherwise
        """
        # Check for unclosed structures
        open_braces = json_str.count("{") - json_str.count("}")
        open_brackets = json_str.count("[") - json_str.count("]")
        
        # Check for unclosed strings (look for unmatched quotes)
        quote_count = 0
        escaped = False
        for i, char in enumerate(json_str):
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if char == '"':
                quote_count += 1
        
        # If quote_count is odd, there's an unclosed string
        # If there are open braces or brackets, it's truncated
        is_truncated = open_braces > 0 or open_brackets > 0 or (quote_count % 2 != 0)
        
        if is_truncated:
            logger.debug(f"Truncated JSON detected - braces: {open_braces}, brackets: {open_brackets}, quotes: {quote_count}")
        
        return is_truncated

    def _complete_truncated_json(self, json_str: str) -> str:
        """
        Attempt to complete truncated JSON string.
        
        Args:
            json_str: The truncated JSON string
            
        Returns:
            Completed JSON string
        """
        completed = json_str
        
        # First, handle unclosed strings (most common truncation)
        # If we have an odd number of quotes, add a closing quote
        quote_count = completed.count('"')
        if quote_count % 2 != 0:
            completed += '"'
            logger.debug("Added closing quote for truncated string")
        
        # Then count and close unclosed structures
        # Count braces and brackets properly (accounting for escaped quotes)
        in_string = False
        escape_next = False
        brace_depth = 0
        bracket_depth = 0
        
        for char in completed:
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth = max(0, brace_depth - 1)
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth = max(0, bracket_depth - 1)
        
        # Add missing closing brackets in reverse order
        # Close brackets first (inner structures), then braces (outer structures)
        if bracket_depth > 0:
            completed += "]" * bracket_depth
            logger.debug(f"Added {bracket_depth} closing bracket(s)")
        if brace_depth > 0:
            completed += "}" * brace_depth
            logger.debug(f"Added {brace_depth} closing brace(s)")
        
        return completed

    def _ensure_dict_result(self, result) -> dict:
        """
        Ensure the result is always a dict.
        
        Args:
            result: The result to validate
            
        Returns:
            Always returns a dict
        """
        if isinstance(result, dict):
            return result
        
        # If result is a list, try to wrap it
        if isinstance(result, list):
            logger.warning(f"LLM returned list instead of dict, wrapping: {result[:100]}...")
            return {"data": result, "_type": "list_wrapped"}
        
        # If result is something else, convert to dict
        logger.warning(f"LLM returned unexpected type {type(result)}, converting to dict")
        return {"data": result, "_type": str(type(result)), "parse_error": "Unexpected return type"}

    def generate_json(self, prompt: str, system: str = "", temperature: float = None) -> dict:
        raw = self.generate(prompt, system, temperature)
        
        # Remove markdown code blocks if present
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]  # Remove ```json
        if raw.startswith("```"):
            raw = raw[3:]  # Remove ```
        if raw.endswith("```"):
            raw = raw[:-3]  # Remove trailing ```
        raw = raw.strip()
        
        # Try multiple parsing strategies
        try:
            # Strategy 1: Direct JSON parse
            result = json.loads(raw)
            return self._ensure_dict_result(result)
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 1 (direct parse) failed: {e}")
        except Exception as e:
            logger.debug(f"Strategy 1 unexpected error: {e}")
        
        try:
            # Strategy 2: Find JSON in markdown blocks
            json_start = raw.find("{")
            json_end = raw.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(raw[json_start:json_end])
                return self._ensure_dict_result(result)
            logger.debug(f"Strategy 2: No valid JSON boundaries found")
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 2 failed: {e}")
        except Exception as e:
            logger.debug(f"Strategy 2 unexpected error: {e}")
        
        try:
            # Strategy 3: Extract from code blocks
            if "```" in raw:
                # Find content between code blocks
                parts = raw.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Inside code block
                        try:
                            result = json.loads(part.strip())
                            return self._ensure_dict_result(result)
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.debug(f"Strategy 3 inner error: {e}")
                            continue
            logger.debug(f"Strategy 3: No code blocks found")
        except Exception as e:
            logger.debug(f"Strategy 3 failed: {e}")
        
        # Strategy 4: Fix incomplete JSON by closing brackets
        try:
            json_start = raw.find("{")
            if json_start != -1:
                # Count open and close brackets to find what's missing
                json_content = raw[json_start:]
                open_braces = json_content.count("{") - json_content.count("}")
                open_brackets = json_content.count("[") - json_content.count("]")
                
                # Add missing closing brackets
                if open_braces > 0:
                    json_content += "}" * open_braces
                if open_brackets > 0:
                    json_content += "]" * open_brackets
                
                # Try to parse the fixed JSON
                result = json.loads(json_content)
                return self._ensure_dict_result(result)
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 4 (fix incomplete JSON) failed: {e}")
        except Exception as e:
            logger.debug(f"Strategy 4 unexpected error: {e}")
        
        # Strategy 5: Sanitize JSON string and parse
        try:
            sanitized = self._sanitize_json_string(raw)
            json_start = sanitized.find("{")
            if json_start != -1:
                json_end = sanitized.rfind("}") + 1
                if json_end > json_start:
                    result = json.loads(sanitized[json_start:json_end])
                    return self._ensure_dict_result(result)
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 5 (sanitize JSON) failed: {e}")
        except Exception as e:
            logger.debug(f"Strategy 5 unexpected error: {e}")
        
        # Strategy 6: Handle truncated JSON
        try:
            json_start = raw.find("{")
            if json_start != -1:
                json_content = raw[json_start:]
                
                # Check if truncated by looking for unclosed structures
                if self._is_truncated_json(json_content):
                    completed = self._complete_truncated_json(json_content)
                    logger.debug(f"Attempting to parse completed JSON (length: {len(completed)})")
                    result = json.loads(completed)
                    return self._ensure_dict_result(result)
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 6 (handle truncated JSON) failed: {e}")
        except Exception as e:
            logger.debug(f"Strategy 6 unexpected error: {e}")
        
        # Strategy 7: Aggressive truncation completion - try adding all possible closing characters
        try:
            json_start = raw.find("{")
            if json_start != -1:
                json_content = raw[json_start:]
                
                # Check if we need truncation completion
                if self._is_truncated_json(json_content):
                    # Add closing quote if odd quotes
                    if json_content.count('"') % 2 != 0:
                        json_content += '"'
                        logger.debug("Added closing quote")
                    
                    # Count unclosed brackets and braces (accounting for strings)
                    in_string = False
                    escape_next = False
                    brace_count = 0
                    bracket_count = 0
                    
                    for char in json_content:
                        if escape_next:
                            escape_next = False
                            continue
                        if char == '\\':
                            escape_next = True
                            continue
                        if char == '"':
                            in_string = not in_string
                            continue
                        if not in_string:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count = max(0, brace_count - 1)
                            elif char == '[':
                                bracket_count += 1
                            elif char == ']':
                                bracket_count = max(0, bracket_count - 1)
                    
                    # Close all open structures in reverse order
                    # Close arrays first, then objects
                    for _ in range(bracket_count):
                        json_content += ']'
                        logger.debug("Added closing bracket")
                    for _ in range(brace_count):
                        json_content += '}'
                        logger.debug("Added closing brace")
                    
                    # Try to parse
                    result = json.loads(json_content)
                    logger.debug(f"Successfully parsed completed JSON (length: {len(json_content)})")
                    return self._ensure_dict_result(result)
        except json.JSONDecodeError as e:
            logger.debug(f"Strategy 7 (aggressive completion) failed: {e}")
        except Exception as e:
            logger.debug(f"Strategy 7 unexpected error: {e}")
        
        # All strategies failed
        logger.warning(f"JSON parse failed for all strategies, raw: {raw[:500]}...")
        return {"raw_response": raw, "parse_error": "Failed to extract valid JSON"}


llm_service = LLMService()