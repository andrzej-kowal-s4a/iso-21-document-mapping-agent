"""
AI Agent utilities for initializing and managing agents.
"""

import logging
from typing import Dict, Optional
from strands import Agent
from strands.models.bedrock import BedrockModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MODEL_NAME = "arn:aws:bedrock:eu-west-1:655604747460:inference-profile/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
NOVA_2_OMNI = "global.amazon.nova-2-lite-v1:0"
CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

MODEL_NAME = NOVA_2_OMNI

# list of supported models are here https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html#inference-profiles-support-system
AWS_REGION = "us-east-1"  # US East (N. Virginia)

# AWS Bedrock pricing per 1000 tokens (as of 2025)
# Prices are in USD per 1000 tokens
# Source: https://aws.amazon.com/bedrock/pricing/
# Note: Prices may vary by region and can change. Update these values as needed.
BEDROCK_PRICING: Dict[str, Dict[str, float]] = {
    # Claude 3.7 Sonnet
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0": {
        "input": 0.003,  # $0.003 per 1000 input tokens ($3.00 per million)
        "output": 0.015,  # $0.015 per 1000 output tokens ($15.00 per million)
    },
    # Claude Sonnet 4.5 (inference profile)
    "eu.anthropic.claude-sonnet-4-5-20250929-v1:0": {
        "input": 0.003,  # $0.003 per 1000 input tokens ($3.00 per million)
        "output": 0.015,  # $0.015 per 1000 output tokens ($15.00 per million)
    },
    # Amazon Nova 2 Omni (Preview)
    NOVA_2_OMNI: {
        "input": 0.0003,  # $0.0003 per 1000 input tokens ($0.30 per million)
        "output": 0.0025,  # $0.0025 per 1000 output tokens ($2.50 per million)
    },
    # Default/fallback pricing (Claude 3.7 Sonnet)
    "default": {
        "input": 0.003,  # $0.003 per 1000 input tokens ($3.00 per million)
        "output": 0.015,  # $0.015 per 1000 output tokens ($15.00 per million)
    },
}


def initialize_agent(
    model_name=MODEL_NAME,
    aws_region=AWS_REGION,
):
    """
    Initialize an Agent.

    Args:
        model_name: The Bedrock model ID to use
        aws_region: The AWS region for Bedrock

    Returns:
        Initialized Agent instance

    Raises:
        Exception: If initialization fails
    """
    try:
        logger.info("Initializing Agent...")
        logger.info(f"Using model: {model_name}")
        logger.info(f"Using AWS region: {aws_region}")
        # Create BedrockModel with specific region
        bedrock_model = BedrockModel(
            model_id=model_name,
            region_name=aws_region,
        )
        agent = Agent(
            model=bedrock_model,
            tools=[],
        )
        # agent.verbose = True
        logger.info("Agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize Agent: {str(e)}", exc_info=True)
        raise e


def calculate_token_cost(
    usage: Dict[str, int],
    model_name: Optional[str] = None,
    pricing: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, float]:
    """
    Calculate the cost of token usage based on AWS Bedrock pricing.

    Args:
        usage: Dictionary with token usage information containing:
            - inputTokens: Number of input tokens
            - outputTokens: Number of output tokens
            - totalTokens: Total tokens (optional, calculated if not provided)
        model_name: Model identifier to look up pricing. If None, uses default pricing.
        pricing: Optional custom pricing dictionary. If None, uses BEDROCK_PRICING.

    Returns:
        Dictionary with cost breakdown:
            - input_cost: Cost for input tokens in USD
            - output_cost: Cost for output tokens in USD
            - total_cost: Total cost in USD
            - input_tokens: Number of input tokens
            - output_tokens: Number of output tokens
            - total_tokens: Total number of tokens
    """
    if pricing is None:
        pricing = BEDROCK_PRICING

    # Get pricing for the model, or use default
    model_pricing = pricing.get(model_name or MODEL_NAME, pricing.get("default", {}))
    if not model_pricing:
        logger.warning(
            f"No pricing found for model {model_name or MODEL_NAME}, using default"
        )
        model_pricing = pricing.get("default", {"input": 0.003, "output": 0.015})

    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    total_tokens = usage.get("totalTokens", input_tokens + output_tokens)

    # Calculate costs (pricing is per 1000 tokens)
    input_cost = (input_tokens / 1_000) * model_pricing.get("input", 0)
    output_cost = (output_tokens / 1_000) * model_pricing.get("output", 0)
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def print_agent_usage(agent: Agent) -> None:
    """
    Print the details of the token usage by the agent.
    """
    result = agent("a")
    # print details of the token usage by the agent
    print("Agent details:")
    print("--------------------------------")
    print(f"Model: {agent.model}")
    print("--------------------------------")
    print(f"Model config: {agent.model.config}")
    print("--------------------------------")

    # Token usage is in result.metrics.accumulated_usage
    usage = result.metrics.accumulated_usage
    print("Token usage:")
    print("--------------------------------")
    print(f"Input tokens: {usage.get('inputTokens', 0):,}")
    print(f"Output tokens: {usage.get('outputTokens', 0):,}")
    print(f"Total tokens: {usage.get('totalTokens', 0):,}")
    if "cacheReadInputTokens" in usage:
        print(f"Cache read input tokens: {usage.get('cacheReadInputTokens', 0):,}")
    if "cacheWriteInputTokens" in usage:
        print(f"Cache write input tokens: {usage.get('cacheWriteInputTokens', 0):,}")
    print("--------------------------------")

    # Calculate and display costs
    cost_info = calculate_token_cost(usage, model_name=MODEL_NAME)
    print("Cost breakdown:")
    print("--------------------------------")
    print(f"Input cost: ${cost_info['input_cost']:.6f}")
    print(f"Output cost: ${cost_info['output_cost']:.6f}")
    print(f"Total cost: ${cost_info['total_cost']:.6f}")
    print("--------------------------------")
