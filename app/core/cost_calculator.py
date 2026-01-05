class CostCalculator:
    """Calculate costs based on token usage"""
    
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-sonnet": {"input": 0.003, "output": 0.015},
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
    }
    
    @classmethod
    def calculate(cls, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost in USD"""
        pricing = cls.PRICING.get(model, cls.PRICING["gpt-3.5-turbo"])
        cost = (prompt_tokens * pricing["input"] / 1000) + (completion_tokens * pricing["output"] / 1000)
        return round(cost, 6)