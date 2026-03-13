"""Claim classification using LightRAG retrieval.

For each claim in the dataset:
1. Query LightRAG to retrieve relevant evidence context
2. Use LLM to classify the claim as Supported or Refuted
"""

import csv
import json
import os
import time
from functools import partial

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache

from experiments.ingest import _build_rag_instance, load_evidence_from_csv


async def _classify_single_claim(
    claim: dict,
    rag: LightRAG,
    config: dict,
    query_mode: str,
) -> dict:
    """Classify a single claim using LightRAG retrieval + LLM.

    Returns prediction dict with claim info, retrieved context, and prediction.
    """
    cls_cfg = config["classification"]
    claim_text = claim["content"]
    claim_title = claim.get("title", "")

    # Build query from claim
    if claim_title:
        query_text = f"{claim_title}: {claim_text}"
    else:
        query_text = claim_text

    # Step 1: Retrieve relevant context from LightRAG
    try:
        param = QueryParam(
            mode=query_mode,
            only_need_context=True,
            top_k=config["lightrag"].get("top_k", 5),
        )
        context = await rag.aquery(query_text, param=param)

        if not context or context.strip() == "":
            context = "(Tidak ada bukti yang ditemukan)"
    except Exception as e:
        context = f"(Error retrieving context: {e})"

    # Step 2: Classify using LLM with retrieved context
    system_prompt = cls_cfg["system_prompt"]
    user_prompt = cls_cfg["user_prompt"].format(
        claim=claim_text,
        evidence_context=context,
    )

    try:
        llm_cfg = config["llm"]

        if llm_cfg["provider"] == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY", "")
            response = await openai_complete_if_cache(
                model=llm_cfg["model"],
                prompt=user_prompt,
                system_prompt=system_prompt,
                base_url=llm_cfg["base_url"],
                api_key=api_key,
                timeout=llm_cfg.get("timeout", 300),
            )
        elif llm_cfg["provider"] == "ollama":
            # Use OpenAI-compatible endpoint that Ollama provides
            response = await openai_complete_if_cache(
                model=llm_cfg["model"],
                prompt=user_prompt,
                system_prompt=system_prompt,
                base_url=f"{llm_cfg.get('host', 'http://localhost:11434')}/v1",
                api_key="ollama",  # Ollama accepts any non-empty key
                timeout=llm_cfg.get("timeout", 300),
            )
        else:
            response = "Refuted"  # fallback

        # Parse classification from response
        prediction = _parse_classification(response)

    except Exception as e:
        prediction = "Refuted"  # default on error
        response = f"(Error: {e})"

    result = {
        "claim_id": claim["id"],
        "claim_text": claim_text,
        "gold_label": claim["label"],
        "gold_label_original": claim.get("label_original", ""),
        "prediction": prediction,
        "raw_response": str(response)[:500],
        "query_mode": query_mode,
    }

    # Optionally save retrieval context
    if config["output"].get("save_retrieval_context", True):
        result["retrieval_context"] = str(context)[:2000]

    return result


def _parse_classification(response: str) -> str:
    """Parse LLM response into Supported/Refuted label."""
    response_lower = response.strip().lower()

    if "supported" in response_lower:
        return "Supported"
    elif "refuted" in response_lower:
        return "Refuted"
    else:
        # Default to Refuted if unclear (conservative approach,
        # following Momii et al. 2024)
        return "Refuted"


async def classify_claims(
    config: dict, dataset_path: str, config_dir: str
) -> list[dict]:
    """Classify all claims using LightRAG retrieval.

    Returns list of prediction dicts.
    """
    # Load data
    print("  Loading dataset...")
    claims, _ = load_evidence_from_csv(dataset_path)

    # Apply sample size limit
    sample_size = config["evaluation"].get("sample_size")
    if sample_size and sample_size < len(claims):
        claims = claims[:sample_size]
        print(f"  Using subset: {sample_size} claims")

    # Build RAG instance (reuse existing KG)
    print("  Initializing LightRAG (loading existing KG)...")
    rag = _build_rag_instance(config, config_dir)
    await rag.initialize_storages()

    query_mode = config["query"]["default_mode"]
    print(f"  Query mode: {query_mode}")
    print(f"  Classifying {len(claims)} claims...")

    predictions = []
    t0 = time.time()

    for i, claim in enumerate(claims):
        pred = await _classify_single_claim(claim, rag, config, query_mode)
        predictions.append(pred)

        if (i + 1) % 50 == 0 or (i + 1) == len(claims):
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(
                f"    Progress: {i + 1}/{len(claims)} "
                f"({elapsed:.1f}s, {rate:.1f} claims/s)"
            )

    await rag.finalize_storages()
    return predictions
