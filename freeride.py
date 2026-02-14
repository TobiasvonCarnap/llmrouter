#!/usr/bin/env python3
"""
FreeRide - OpenRouter Free Models Manager for LLMRouter

Automatically fetches, ranks, and manages free AI models from OpenRouter.
Integrates with LLMRouter's config.yaml for seamless free model usage.

CHANGELOG:
- 2026-02-15: Kommentare in config.yaml werden nun bei Updates erhalten
- 2026-02-15: Duplikate werden verhindert (auskommentierte Modelle nicht als aktiv hinzufügen)
"""

import json
import os
import sys
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import yaml

try:
    import requests
except ImportError:
    requests = None

# Constants
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"
CACHE_DURATION_HOURS = 6

# Free model ranking criteria (higher is better)
RANKING_WEIGHTS = {
    "context_length": 0.4,      # Prefer longer context
    "capabilities": 0.3,        # Prefer more capabilities
    "recency": 0.2,            # Prefer newer models
    "provider_trust": 0.1       # Prefer trusted providers
}

# Trusted providers (in order of preference)
TRUSTED_PROVIDERS = [
    "google", "meta-llama", "mistralai", "deepseek",
    "nvidia", "qwen", "microsoft", "allenai", "arcee-ai",
    "liquid", "stepfun", "upstage"
]

# Default complexity tiers mapping
DEFAULT_TIER_MAPPING = {
    "super_easy": ["small", "fast", "light"],
    "easy": ["gemma", "llama-3.1", "llama-3.2", "nano", "mini", "small"],
    "medium": ["llama-3.3", "mistral", "gemini-2.0", "flash", "qwen2.5"],
    "hard": ["large", "coder", "thinking", "reasoning", "gemini-2.5"],
    "super_hard": ["opus", "o1", "o3", "deepseek-r1", "claude-opus", "qwen3-235b"]
}


def get_api_key(config: Optional[Dict] = None) -> Optional[str]:
    """Get OpenRouter API key from environment or config."""
    # Try environment first
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key

    # Try config providers section
    if config and "providers" in config:
        openrouter_config = config["providers"].get("openrouter", {})
        api_key = openrouter_config.get("api_key")
        if api_key:
            return api_key

    return None


def fetch_all_models(api_key: str) -> List[Dict]:
    """Fetch all models from OpenRouter API."""
    if not requests:
        print("Error: requests library required. Install with: pip install requests")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(OPENROUTER_API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.RequestException as e:
        print(f"Error fetching models from OpenRouter: {e}")
        return []


def filter_free_models(models: List[Dict]) -> List[Dict]:
    """Filter models to only include free ones (pricing.prompt == 0 or :free suffix)."""
    free_models = []

    for model in models:
        model_id = model.get("id", "")
        pricing = model.get("pricing", {})

        # Check if model is free (prompt cost is 0 or None)
        prompt_cost = pricing.get("prompt")
        if prompt_cost is not None:
            try:
                if float(prompt_cost) == 0:
                    free_models.append(model)
                    continue
            except (ValueError, TypeError):
                pass

        # Also include models with :free suffix
        if ":free" in model_id and model not in free_models:
            free_models.append(model)

    return free_models


def calculate_model_score(model: Dict) -> float:
    """Calculate a ranking score for a model based on multiple criteria."""
    score = 0.0

    # Context length score (normalized to 0-1, max 1M tokens)
    context_length = model.get("context_length", 0)
    context_score = min(context_length / 1_000_000, 1.0)
    score += context_score * RANKING_WEIGHTS["context_length"]

    # Capabilities score
    capabilities = model.get("supported_parameters", [])
    capability_count = len(capabilities) if capabilities else 0
    capability_score = min(capability_count / 10, 1.0)  # Normalize to max 10 capabilities
    score += capability_score * RANKING_WEIGHTS["capabilities"]

    # Recency score (based on creation date)
    created = model.get("created", 0)
    if created:
        days_old = (time.time() - created) / 86400
        recency_score = max(0, 1 - (days_old / 365))  # Newer models score higher
        score += recency_score * RANKING_WEIGHTS["recency"]

    # Provider trust score
    model_id = model.get("id", "")
    provider = model_id.split("/")[0] if "/" in model_id else ""
    if provider in TRUSTED_PROVIDERS:
        trust_index = TRUSTED_PROVIDERS.index(provider)
        trust_score = 1 - (trust_index / len(TRUSTED_PROVIDERS))
        score += trust_score * RANKING_WEIGHTS["provider_trust"]

    return score


def rank_free_models(models: List[Dict]) -> List[Dict]:
    """Rank free models by quality score."""
    scored_models = []
    for model in models:
        score = calculate_model_score(model)
        scored_models.append({**model, "_score": score})

    # Sort by score descending
    scored_models.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return scored_models


def format_model_for_router(model_id: str) -> str:
    """Format model ID for LLMRouter config.
    
    Returns format: "openrouter:<author>/<model>:free"
    """
    # Ensure :free suffix
    if ":free" not in model_id:
        base_id = f"{model_id}:free"
    else:
        base_id = model_id

    # Remove existing openrouter/ prefix if present (we add :free format)
    if base_id.startswith("openrouter/"):
        base_id = base_id[len("openrouter/"):]

    return f"openrouter:{base_id}"


def categorize_model(model: Dict) -> str:
    """Categorize a model into complexity tier based on its properties."""
    model_id = model.get("id", "").lower()
    context_length = model.get("context_length", 0)
    score = model.get("_score", 0)

    # Check for specific model patterns
    model_name = model_id.split("/")[-1] if "/" in model_id else model_id

    # Super hard: Large reasoning models, top-tier models
    if any(x in model_name for x in ["opus", "o1", "o3", "deepseek-r1", "qwen3-235b", "thinking"]):
        if score > 0.5 or context_length > 100000:
            return "super_hard"

    # Hard: Coder models, large models
    if any(x in model_name for x in ["coder", "65b", "70b", "405b", "large", "gemini-2.5"]):
        if score > 0.4:
            return "hard"

    # Super easy: Very small models (1B-3B)
    if any(x in model_name for x in ["1b", "1.5b", "2b", "3b", "gemma-2b", "nano"]):
        return "super_easy"

    # Easy: Small to medium models (7B-9B)
    if any(x in model_name for x in ["7b", "8b", "9b", "nano", "mini", "small", "gemma"]):
        return "easy"

    # Medium: Mid-range models
    if any(x in model_name for x in ["14b", "27b", "32b", "flash", "mistral", "llama-3.3"]):
        return "medium"

    # Hard: Larger models (by context or score)
    if context_length >= 128000 or score > 0.6:
        return "hard"

    # Default based on score
    if score > 0.7:
        return "hard"
    elif score > 0.5:
        return "medium"
    elif score > 0.3:
        return "easy"
    else:
        return "super_easy"


def distribute_to_tiers(ranked_models: List[Dict], config: Optional[Dict] = None) -> Dict[str, List[str]]:
    """Distribute ranked free models into complexity tiers."""
    tiers = {
        "super_easy": [],
        "easy": [],
        "medium": [],
        "hard": [],
        "super_hard": []
    }

    # Get user preferences from config if available
    tier_mapping = DEFAULT_TIER_MAPPING
    if config and "freeride" in config:
        user_mapping = config["freeride"].get("tier_mapping", {})
        tier_mapping.update(user_mapping)

    # Categorize each model
    for model in ranked_models:
        tier = categorize_model(model)
        formatted = format_model_for_router(model["id"])
        if formatted not in tiers[tier]:
            tiers[tier].append(formatted)

    # Ensure openrouter/free is in each tier as ultimate fallback
    free_router = "openrouter:openrouter/free:free"
    for tier_name in tiers:
        if free_router not in tiers[tier_name]:
            tiers[tier_name].append(free_router)

    return tiers


def parse_yaml_with_comments(config_path: str) -> Tuple[Dict, Dict[str, List[Tuple[str, bool]]]]:
    """
    Parse YAML file and extract comments per tier.
    
    Returns:
        - parsed config dict
        - dict mapping tier names to lists of (model_string, is_commented) tuples
    """
    config_file = Path(config_path)
    if not config_file.exists():
        return {}, {}
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Parse the YAML to get the structure
    config = yaml.safe_load(content) or {}
    
    # Extract commented lines per tier
    tier_comments = {}
    models_section = config.get("models", {})
    
    for tier_name in ["super_easy", "easy", "medium", "hard", "super_hard"]:
        tier_comments[tier_name] = []
        
        # Find the tier in the file
        tier_pattern = rf"^{re.escape(tier_name)}:\s*$"
        lines = content.split('\n')
        in_tier = False
        indent_level = None
        
        for i, line in enumerate(lines):
            # Check if we found the tier start
            if re.match(tier_pattern, line.strip()):
                in_tier = True
                # Determine indent level from next non-empty line
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    if next_line.strip():
                        indent_level = len(next_line) - len(next_line.lstrip())
                        break
                continue
            
            if in_tier:
                # Check if we're still in the tier (same or greater indent, or empty line)
                stripped = line.strip()
                current_indent = len(line) - len(line.lstrip())
                
                # Exit tier if we hit another top-level key
                if stripped and current_indent <= 0 and ':' in stripped:
                    # Check if it's another tier or different section
                    if not any(stripped.startswith(t) for t in models_section.keys()):
                        break
                    if stripped.split(':')[0] != tier_name:
                        break
                
                # Process model lines
                if stripped:
                    # Check if commented
                    if stripped.startswith('#') or stripped.startswith('- #'):
                        # Extract the model string from comment
                        match = re.search(r'#\s*(-\s*)?(.+)', stripped)
                        if match:
                            model_str = match.group(2).strip()
                            tier_comments[tier_name].append((model_str, True))
                    elif stripped.startswith('- '):
                        # Active model entry
                        model_str = stripped[2:].strip()
                        tier_comments[tier_name].append((model_str, False))
    
    return config, tier_comments


def normalize_model_id(model_id: str) -> str:
    """Normalize model ID for comparison (remove provider prefix for matching)."""
    # Remove common prefixes for comparison
    normalized = model_id.strip()
    
    # Remove provider prefixes for comparison
    prefixes = ['openrouter:', 'anthropic:', 'google:', 'kimi:', 'exo:', 'nvidia:', 'lmstudio:']
    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
            break
    
    # Remove :free suffix for comparison
    if normalized.endswith(':free'):
        normalized = normalized[:-5]
    
    return normalized.lower()


def has_duplicate(tier_entries: List[Tuple[str, bool]], new_model: str) -> bool:
    """
    Check if a model already exists in the tier (either active or commented).
    Returns True if the normalized model ID matches any existing entry.
    """
    new_normalized = normalize_model_id(new_model)
    
    for existing_model, is_commented in tier_entries:
        existing_normalized = normalize_model_id(existing_model)
        if new_normalized == existing_normalized:
            return True
    
    return False


def merge_models_with_comments(
    tier_entries: List[Tuple[str, bool]], 
    new_models: List[str]
) -> List[str]:
    """
    Merge new models with existing entries, preserving comments and avoiding duplicates.
    
    Args:
        tier_entries: List of (model_string, is_commented) tuples from existing config
        new_models: List of new models to add
        
    Returns:
        List of YAML lines for the tier
    """
    result = []
    added_models = set()  # Track normalized IDs to avoid duplicates
    
    # First pass: add all existing entries (preserving comments)
    for model_str, is_commented in tier_entries:
        normalized = normalize_model_id(model_str)
        
        if is_commented:
            # Keep the comment as-is
            result.append(f"  # - {model_str}")
        else:
            # Keep active model
            result.append(f"  - {model_str}")
        
        added_models.add(normalized)
    
    # Second pass: add new models that aren't already present
    for new_model in new_models:
        normalized = normalize_model_id(new_model)
        
        if normalized not in added_models:
            result.append(f"  - {new_model}")
            added_models.add(normalized)
    
    return result


def save_config_with_comments(
    config_path: str,
    config: Dict,
    tier_comments: Dict[str, List[Tuple[str, bool]]],
    new_tiers: Dict[str, List[str]]
) -> bool:
    """
    Save config while preserving YAML structure and comments.
    
    This function intelligently merges new models with existing entries,
    keeping comments intact and avoiding duplicates.
    """
    config_file = Path(config_path)
    
    # Read original file
    with open(config_file, 'r') as f:
        original_content = f.read()
    
    lines = original_content.split('\n')
    result_lines = []
    i = 0
    current_tier = None
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this is a tier start
        tier_match = None
        for tier_name in ["super_easy", "easy", "medium", "hard", "super_hard"]:
            if re.match(rf"^{re.escape(tier_name)}:\s*$", stripped):
                tier_match = tier_name
                break
        
        if tier_match:
            current_tier = tier_match
            result_lines.append(line)
            
            # Find the end of this tier section
            tier_end = i + 1
            tier_indent = None
            
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                next_stripped = next_line.strip()
                
                if not next_stripped:
                    tier_end = j
                    continue
                
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Check if we've left the tier section
                if next_indent <= 0 and ':' in next_stripped:
                    # Check if it's another model tier
                    key = next_stripped.split(':')[0]
                    if key not in ["super_easy", "easy", "medium", "hard", "super_hard"]:
                        tier_end = j
                        break
                
                tier_end = j + 1
            
            # Merge existing entries with new models
            existing_entries = tier_comments.get(current_tier, [])
            new_models = new_tiers.get(current_tier, [])
            merged = merge_models_with_comments(existing_entries, new_models)
            
            # Add merged lines
            for merged_line in merged:
                result_lines.append(merged_line)
            
            # Skip original tier lines
            i = tier_end
            current_tier = None
            continue
        
        result_lines.append(line)
        i += 1
    
    # Write the result
    with open(config_file, 'w') as f:
        f.write('\n'.join(result_lines))
    
    return True


def update_config_with_freeride(
    config_path: str,
    api_key: Optional[str] = None,
    force_refresh: bool = False,
    preserve_existing: bool = True
) -> Dict[str, Any]:
    """Update LLMRouter config.yaml with free models from OpenRouter.
    
    Args:
        config_path: Path to config.yaml
        api_key: OpenRouter API key (optional, will try to get from config)
        force_refresh: Force API refresh even if cache is valid
        preserve_existing: Keep existing non-openrouter models in tiers
        
    Returns:
        Dict with status info
    """
    config_file = Path(config_path)
    if not config_file.exists():
        return {"success": False, "error": f"Config file not found: {config_path}"}

    # Load existing config with comments preserved
    try:
        config, tier_comments = parse_yaml_with_comments(config_path)
    except Exception as e:
        return {"success": False, "error": f"Error reading config: {e}"}

    # Get API key
    if not api_key:
        api_key = get_api_key(config)

    if not api_key:
        return {
            "success": False, 
            "error": "No OpenRouter API key found. Set OPENROUTER_API_KEY env var or add to config.providers.openrouter.api_key"
        }

    # Fetch and process models
    print("Fetching models from OpenRouter...")
    all_models = fetch_all_models(api_key)
    if not all_models:
        return {"success": False, "error": "Failed to fetch models from OpenRouter"}

    free_models = filter_free_models(all_models)
    if not free_models:
        return {"success": False, "error": "No free models found on OpenRouter"}

    print(f"Found {len(free_models)} free models")
    
    ranked_models = rank_free_models(free_models)
    print(f"Top model: {ranked_models[0]['id']} (score: {ranked_models[0].get('_score', 0):.3f})")

    # Distribute to tiers
    new_tiers = distribute_to_tiers(ranked_models, config)

    # Update tiers while preserving comments and avoiding duplicates
    stats = {"added": 0, "preserved": 0, "skipped_duplicates": 0, "tiers_updated": 0}

    for tier_name in new_tiers:
        existing_entries = tier_comments.get(tier_name, [])
        
        # Count preserved entries (comments + existing non-openrouter models)
        for model_str, is_commented in existing_entries:
            if is_commented or not model_str.startswith("openrouter:"):
                stats["preserved"] += 1
        
        # Count new models that will be added (not duplicates)
        for new_model in new_tiers[tier_name]:
            if not has_duplicate(existing_entries, new_model):
                stats["added"] += 1
            else:
                stats["skipped_duplicates"] += 1
        
        stats["tiers_updated"] += 1

    # Save config with comments preserved
    try:
        save_config_with_comments(config_path, config, tier_comments, new_tiers)
    except Exception as e:
        return {"success": False, "error": f"Error saving config: {e}"}

    # Add freeride metadata to config (need to reload and update)
    try:
        with open(config_file) as f:
            updated_content = f.read()
        
        # Update freeride section in the YAML
        updated_config = yaml.safe_load(updated_content) or {}
        if "freeride" not in updated_config:
            updated_config["freeride"] = {}
        
        updated_config["freeride"].update({
            "enabled": True,
            "last_update": datetime.now().isoformat(),
            "total_free_models": len(free_models),
            "api_url": OPENROUTER_API_URL
        })
        
        # Re-write with updated freeride section
        with open(config_file, 'w') as f:
            yaml.dump(updated_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Re-apply comments (they were lost in the yaml.dump)
        # This is a simplified approach - we'll re-parse and merge
        config, tier_comments = parse_yaml_with_comments(config_path)
        save_config_with_comments(config_path, updated_config, tier_comments, new_tiers)
        
    except Exception as e:
        print(f"Warning: Could not update freeride metadata: {e}")

    return {
        "success": True,
        "message": f"Updated {stats['tiers_updated']} tiers with {stats['added']} new free models, preserved {stats['preserved']} existing entries",
        "stats": stats,
        "top_models": [m["id"] for m in ranked_models[:5]]
    }


def get_freeride_status(config_path: str) -> Dict[str, Any]:
    """Get current FreeRide status from config."""
    config_file = Path(config_path)
    if not config_file.exists():
        return {"error": "Config file not found"}

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        return {"error": f"Error reading config: {e}"}

    freeride_config = config.get("freeride", {})
    
    status = {
        "enabled": freeride_config.get("enabled", False),
        "last_update": freeride_config.get("last_update"),
        "total_free_models": freeride_config.get("total_free_models", 0),
        "api_key_configured": bool(get_api_key(config)),
        "tiers": {}
    }

    # Count openrouter models per tier
    models = config.get("models", {})
    for tier in ["super_easy", "easy", "medium", "hard", "super_hard"]:
        tier_models = models.get(tier, [])
        if isinstance(tier_models, str):
            tier_models = [tier_models]
        openrouter_count = sum(1 for m in tier_models if m.startswith("openrouter:"))
        status["tiers"][tier] = {
            "total": len(tier_models),
            "openrouter_free": openrouter_count
        }

    return status


def list_free_models(config_path: str, limit: int = 20) -> List[Dict]:
    """List available free models from cache or API."""
    config_file = Path(config_path)
    config = {}
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f) or {}
        except:
            pass

    api_key = get_api_key(config)
    if not api_key:
        print("Error: No OpenRouter API key configured")
        return []

    all_models = fetch_all_models(api_key)
    free_models = filter_free_models(all_models)
    ranked = rank_free_models(free_models)
    
    return ranked[:limit]


if __name__ == "__main__":
    # Simple CLI for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="FreeRide - OpenRouter Free Models Manager")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--update", "-u", action="store_true", help="Update config with free models")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    parser.add_argument("--list", "-l", action="store_true", help="List free models")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Limit for list command")
    parser.add_argument("--force", "-f", action="store_true", help="Force refresh")
    
    args = parser.parse_args()
    
    if args.update:
        result = update_config_with_freeride(args.config, force_refresh=args.force)
        if result["success"]:
            print(f"✓ {result['message']}")
            print(f"  Stats: {result.get('stats', {})}")
            print(f"  Top models: {', '.join(result['top_models'][:3])}")
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)
    elif args.status:
        status = get_freeride_status(args.config)
        print(json.dumps(status, indent=2))
    elif args.list:
        models = list_free_models(args.config, limit=args.limit)
        print(f"{'#':<3} {'Model ID':<50} {'Score':<8} {'Context'}")
        print("-" * 80)
        for i, m in enumerate(models, 1):
            ctx = m.get('context_length', 0)
            ctx_str = f"{ctx//1000}K" if ctx >= 1000 else str(ctx)
            print(f"{i:<3} {m['id']:<50} {m.get('_score', 0):.3f}    {ctx_str}")
    else:
        parser.print_help()
