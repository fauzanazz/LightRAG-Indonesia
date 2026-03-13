"""Evidence ingestion into LightRAG knowledge graph.

Extracts unique evidence texts from MAFINDO CSV, then inserts them
into LightRAG for KG construction (entity extraction, relation
extraction, community detection).
"""

import csv
import json
import os
import time
from functools import partial

from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.llm.ollama import ollama_embed
from lightrag.utils import EmbeddingFunc


def _build_rag_instance(config: dict, config_dir: str) -> LightRAG:
    """Create and configure a LightRAG instance from experiment config."""
    lrag_cfg = config["lightrag"]
    llm_cfg = config["llm"]
    emb_cfg = config["embedding"]
    flags = config["flags"]

    # Resolve working directory
    working_dir = lrag_cfg["working_dir"]
    if not os.path.isabs(working_dir):
        working_dir = os.path.normpath(os.path.join(config_dir, working_dir))
    os.makedirs(working_dir, exist_ok=True)

    # Build LLM function
    if llm_cfg["provider"] == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY env var not set. "
                "Set it with: export OPENROUTER_API_KEY=your_key"
            )
        llm_model_func = partial(
            openai_complete_if_cache,
            model=llm_cfg["model"],
            base_url=llm_cfg["base_url"],
            api_key=api_key,
        )
    elif llm_cfg["provider"] == "ollama":
        from lightrag.llm.ollama import ollama_model_complete

        llm_model_func = partial(
            ollama_model_complete,
            host=llm_cfg.get("host", "http://localhost:11434"),
        )
    else:
        raise ValueError(f"Unknown LLM provider: {llm_cfg['provider']}")

    # Build embedding function
    if emb_cfg["provider"] == "ollama":
        embedding_func = EmbeddingFunc(
            embedding_dim=emb_cfg.get("dim", 1024),
            max_token_size=emb_cfg.get("max_tokens", 8192),
            func=partial(
                ollama_embed.func,
                embed_model=emb_cfg["model"],
                host=emb_cfg.get("host", "http://localhost:11434"),
            ),
        )
    elif emb_cfg["provider"] == "openai":
        from lightrag.llm.openai import openai_embed

        embedding_func = EmbeddingFunc(
            embedding_dim=emb_cfg.get("dim", 1536),
            max_token_size=emb_cfg.get("max_tokens", 8192),
            func=partial(
                openai_embed.func,
                model=emb_cfg["model"],
                base_url=emb_cfg.get("base_url"),
                api_key=os.getenv("OPENAI_API_KEY"),
            ),
        )
    else:
        raise ValueError(f"Unknown embedding provider: {emb_cfg['provider']}")

    # Build addon_params with feature flags
    addon_params = {
        "language": flags.get("summary_language", "English"),
        "use_indonesian_prompts": flags.get("use_indonesian_prompts", False),
        "use_factcheck_entities": flags.get("use_factcheck_entities", False),
        "use_indonesian_preprocessing": flags.get(
            "use_indonesian_preprocessing", True
        ),
    }

    # If factcheck entities are enabled, set entity_types
    if addon_params["use_factcheck_entities"]:
        from lightrag.constants import FACTCHECK_ENTITY_TYPES

        addon_params["entity_types"] = FACTCHECK_ENTITY_TYPES

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=llm_model_func,
        llm_model_name=llm_cfg["model"],
        embedding_func=embedding_func,
        chunk_token_size=lrag_cfg.get("chunk_size", 1200),
        chunk_overlap_token_size=lrag_cfg.get("chunk_overlap", 100),
        graph_storage=lrag_cfg.get("graph_storage", "NetworkXStorage"),
        vector_storage=lrag_cfg.get("vector_storage", "NanoVectorDBStorage"),
        kv_storage=lrag_cfg.get("kv_storage", "JsonKVStorage"),
        top_k=lrag_cfg.get("top_k", 5),
        entity_extract_max_gleaning=lrag_cfg.get("entity_extract_max_gleaning", 1),
        llm_model_max_async=llm_cfg.get("max_async", 4),
        default_llm_timeout=llm_cfg.get("timeout", 300),
        addon_params=addon_params,
    )

    return rag


def load_evidence_from_csv(csv_path: str) -> tuple[list[dict], dict[str, str]]:
    """Load claims and extract unique evidence texts from CSV.

    Returns:
        (claims, evidence_map) where:
        - claims: list of dicts with id, content, label, evidence_ids
        - evidence_map: dict mapping evidence_id -> evidence text
    """
    claims = []
    evidence_map = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence_list = json.loads(row["evidence"])
            evidence_ids = []

            for ev in evidence_list:
                eid = str(ev.get("evidence_id", ""))
                content = ev.get("content", "").strip()
                title = ev.get("title", "").strip()

                if not content:
                    continue

                # Build full evidence text with title
                if title:
                    full_text = f"{title}\n\n{content}"
                else:
                    full_text = content

                evidence_map[eid] = full_text
                evidence_ids.append(eid)

            claims.append(
                {
                    "id": row["id"],
                    "content": row["content"],
                    "title": row.get("title", ""),
                    "label": row.get("label", ""),
                    "label_original": row.get("label_original", row.get("label", "")),
                    "evidence_ids": evidence_ids,
                }
            )

    return claims, evidence_map


async def ingest_evidence(
    config: dict, dataset_path: str, config_dir: str
) -> dict:
    """Ingest all unique evidence texts into LightRAG.

    Returns stats dict with ingestion metrics.
    """
    # Load data
    print("  Loading dataset...")
    claims, evidence_map = load_evidence_from_csv(dataset_path)
    print(f"  Found {len(claims)} claims, {len(evidence_map)} unique evidence items")

    # Build RAG instance
    print("  Initializing LightRAG...")
    rag = _build_rag_instance(config, config_dir)
    await rag.initialize_storages()

    # Prepare evidence texts for insertion
    # Each evidence is inserted as a separate document with its ID
    evidence_texts = list(evidence_map.values())
    evidence_ids = list(evidence_map.keys())

    print(f"  Inserting {len(evidence_texts)} evidence documents...")
    t0 = time.time()

    # Insert in batches to avoid memory issues
    batch_size = config.get("ingestion", {}).get("batch_size", 50)
    total_inserted = 0

    for i in range(0, len(evidence_texts), batch_size):
        batch_texts = evidence_texts[i : i + batch_size]
        batch_ids = evidence_ids[i : i + batch_size]

        try:
            await rag.ainsert(
                batch_texts,
                ids=batch_ids,
            )
            total_inserted += len(batch_texts)
            print(
                f"    Batch {i // batch_size + 1}: "
                f"{total_inserted}/{len(evidence_texts)} inserted"
            )
        except Exception as e:
            print(f"    [ERROR] Batch {i // batch_size + 1} failed: {e}")
            # Continue with next batch
            continue

    insert_time = time.time() - t0

    # Finalize storage
    await rag.finalize_storages()

    stats = {
        "dataset_path": dataset_path,
        "total_claims": len(claims),
        "unique_evidence": len(evidence_map),
        "documents_inserted": total_inserted,
        "insert_time_seconds": round(insert_time, 2),
        "config_flags": config["flags"],
        "lightrag_config": {
            "chunk_size": config["lightrag"]["chunk_size"],
            "chunk_overlap": config["lightrag"]["chunk_overlap"],
            "graph_storage": config["lightrag"]["graph_storage"],
        },
    }

    return stats
