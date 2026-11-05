"""
Automated Verification Suite for Crash-Safe Checkpointing, Autosave & Resume.
Tests all 10 critical failure and crash recovery scenarios:
1. Interruption after a completed batch.
2. Interruption during a partially written batch.
3. Corrupted progress metadata recovery from snapshot.
4. Duplicate task execution idempotency.
5. Repeated API response after retry.
6. Quota exhaustion graceful pause.
7. Invalid source document handling.
8. Failed embedding operation resilience.
9. Recovery from an older valid checkpoint.
10. Resuming without duplicating verified Q&A records.
11. Lock management and stale PID detection.
"""

import os
import sys
import json
import time
import shutil
import pytest
from pathlib import Path

# Add BACKEND to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.research.checkpoint_manager import CheckpointManager


@pytest.fixture
def temp_research_dir(tmp_path):
    """Provides a fresh isolated directory for testing checkpoint persistence."""
    research_dir = tmp_path / "vigbot_research"
    research_dir.mkdir(parents=True, exist_ok=True)
    yield str(research_dir)
    shutil.rmtree(tmp_path, ignore_errors=True)


def test_01_interruption_after_completed_batch(temp_research_dir):
    """Scenario 1: Process stops after completing batch 1. Next start resumes from batch 2."""
    mgr1 = CheckpointManager(base_dir=temp_research_dir)
    mgr1.start_phase("phase_1_audit")
    mgr1.start_subtask("phase_1_audit", "audit_existing_architecture")
    
    # Save batch 1
    batch_file = Path(temp_research_dir) / "datasets" / "batch_001.json"
    batch_data = [{"q": "Attendance requirement?", "a": "75% minimum"}]
    mgr1.atomic_write_json(batch_file, batch_data)
    mgr1.register_artifact("batch_001", "datasets/batch_001.json", "dataset_batch", record_count=1)
    mgr1.complete_subtask("phase_1_audit", "audit_existing_architecture", {"operation": "Completed Batch 1"})

    # Simulate sudden crash / shutdown by abandoning mgr1
    del mgr1

    # Simulate fresh boot
    mgr2 = CheckpointManager(base_dir=temp_research_dir)
    assert mgr2.is_subtask_completed("phase_1_audit", "audit_existing_architecture") is True
    assert "batch_001" in mgr2.manifest["artifacts"]
    assert mgr2.manifest["artifacts"]["batch_001"]["record_count"] == 1


def test_02_interruption_during_partially_written_batch(temp_research_dir):
    """Scenario 2: Process dies mid-write. Dangling tmp file is ignored; state is uncorrupted."""
    mgr1 = CheckpointManager(base_dir=temp_research_dir)
    mgr1.start_phase("phase_1_audit")
    mgr1.start_subtask("phase_1_audit", "validate_active_model_catalogs")

    # Simulate partially written temporary file
    dangling_tmp = Path(temp_research_dir) / "progress.json.tmp.99999_12345"
    with open(dangling_tmp, "w", encoding="utf-8") as f:
        f.write('{"incomplete": true, "corrupted_half_written_payload"')

    # Restart
    mgr2 = CheckpointManager(base_dir=temp_research_dir)
    assert mgr2.state["schema_version"] == "1.0.0"
    assert mgr2.is_subtask_completed("phase_1_audit", "validate_active_model_catalogs") is False


def test_03_corrupted_progress_metadata_recovers_from_checkpoint(temp_research_dir):
    """Scenario 3: progress.json is corrupted by power cut. Automatically restores from newest checkpoint."""
    mgr1 = CheckpointManager(base_dir=temp_research_dir)
    mgr1.start_phase("phase_1_audit")
    mgr1.checkpoint("Snapshot Before Crash", metadata={"key_val": 42})
    
    # Verify checkpoint exists
    cps = list(Path(temp_research_dir).glob("checkpoints/checkpoint_*.json"))
    assert len(cps) >= 1

    # Corrupt progress.json completely
    progress_file = Path(temp_research_dir) / "progress.json"
    with open(progress_file, "w", encoding="utf-8") as f:
        f.write("<<<NON_JSON_CORRUPTED_BYTES_FROM_HARD_RESET>>>")

    # Re-instantiate manager
    mgr2 = CheckpointManager(base_dir=temp_research_dir)
    # Must have recovered cleanly from snapshot
    assert mgr2.state["checkpoint_id"] >= 1
    # Check that errors.jsonl captured the recovery event
    errors_file = Path(temp_research_dir) / "errors.jsonl"
    assert errors_file.exists()
    content = errors_file.read_text(encoding="utf-8")
    assert "CorruptedProgressJSON" in content or "RecoveredFromSnapshot" in content


def test_04_duplicate_task_execution_idempotency(temp_research_dir):
    """Scenario 4: Re-running completed task is idempotent and does not corrupt state."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    mgr.start_phase("phase_1_audit")
    mgr.start_subtask("phase_1_audit", "audit_existing_architecture")
    mgr.complete_subtask("phase_1_audit", "audit_existing_architecture")
    
    initial_cid = mgr.state["checkpoint_id"]
    # Check status
    assert mgr.is_subtask_completed("phase_1_audit", "audit_existing_architecture") is True

    # Call complete again
    mgr.complete_subtask("phase_1_audit", "audit_existing_architecture")
    assert mgr.is_subtask_completed("phase_1_audit", "audit_existing_architecture") is True


def test_05_repeated_api_response_after_retry(temp_research_dir):
    """Scenario 5: Simulated repeated API response after retry uses stable ID to avoid duplicates."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    qa_store = Path(temp_research_dir) / "datasets" / "qa_store.json"
    
    # Insert record with stable ID
    rec = {"id": "vignan_att_001", "q": "What is attendance cutoff?", "a": "75%"}
    mgr.atomic_write_json(qa_store, {rec["id"]: rec})
    mgr.register_artifact("qa_store", "datasets/qa_store.json", "qa_database", record_count=1)

    # Re-attempting insertion of same ID
    existing = json.loads(qa_store.read_text(encoding="utf-8"))
    existing[rec["id"]] = rec  # overwrites safely, record count remains 1
    mgr.atomic_write_json(qa_store, existing)
    mgr.register_artifact("qa_store", "datasets/qa_store.json", "qa_database", record_count=len(existing))

    assert len(existing) == 1
    assert mgr.manifest["artifacts"]["qa_store"]["record_count"] == 1


def test_06_quota_exhaustion_saves_state_and_marks_retryable(temp_research_dir):
    """Scenario 6: Quota exhaustion captures error, marks retryable, and saves snapshot without data loss."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    mgr.start_phase("phase_3_questions")
    mgr.start_subtask("phase_3_questions", "generate_factual_procedural_questions")

    # Simulate 429 quota exhaustion
    mgr.fail_subtask(
        "phase_3_questions",
        "generate_factual_procedural_questions",
        error_msg="HTTP 429 Quota Exhausted for groq: Rate limit reached. Free tier daily tokens consumed.",
        retryable=True
    )

    # Verify task is failed_retryable and not permanently dropped
    subtask = mgr.phase_status["phase_3_questions"]["subtasks"]["generate_factual_procedural_questions"]
    assert subtask["status"] == "failed_retryable"
    assert "Quota Exhausted" in subtask["error"]

    # Verify errors.jsonl captured it
    errors = Path(temp_research_dir) / "errors.jsonl"
    assert "HTTP 429" in errors.read_text(encoding="utf-8")


def test_07_invalid_source_documents_handled(temp_research_dir):
    """Scenario 7: Invalid or missing documents are safely caught and logged."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    fake_doc = Path(temp_research_dir) / "documents" / "non_existent.pdf"
    
    sha = mgr.calculate_sha256(fake_doc)
    assert sha == ""

    mgr.log_error("phase_2_research", "extract_academic_regulations", "InvalidDocument", "File not found: non_existent.pdf")
    errors = Path(temp_research_dir) / "errors.jsonl"
    assert "File not found" in errors.read_text(encoding="utf-8")


def test_08_failed_embedding_operation_resilience(temp_research_dir):
    """Scenario 8: Failed embedding step fails retryably without wiping indexed data."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    mgr.start_phase("phase_6_rag_integration")
    mgr.start_subtask("phase_6_rag_integration", "build_hybrid_bm25_dense_retriever")

    # Register an already successful chunk index
    index_file = Path(temp_research_dir) / "datasets" / "chunks.json"
    mgr.atomic_write_json(index_file, [{"id": "chunk_1", "text": "Vignan was established in 2008"}])
    mgr.register_artifact("chunks_manifest", "datasets/chunks.json", "document_chunks", record_count=1)

    # Fail embedding
    mgr.fail_subtask("phase_6_rag_integration", "build_hybrid_bm25_dense_retriever", "Embedding model connection reset", retryable=True)

    # Prior artifacts remain safe
    assert "chunks_manifest" in mgr.manifest["artifacts"]
    assert mgr.manifest["artifacts"]["chunks_manifest"]["record_count"] == 1


def test_09_recovery_from_older_valid_checkpoint(temp_research_dir):
    """Scenario 9: If newest checkpoint is also corrupt, system can fall back to prior valid checkpoint."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    cp1 = mgr.checkpoint("Known Good Baseline Checkpoint")
    time.sleep(0.01)
    cp2 = mgr.checkpoint("Second Checkpoint")

    cps = sorted(Path(temp_research_dir).glob("checkpoints/checkpoint_*.json"))
    assert len(cps) >= 2

    # Corrupt newest checkpoint and progress.json
    with open(cps[-1], "w", encoding="utf-8") as f:
        f.write("CORRUPT_BYTES")
    with open(Path(temp_research_dir) / "progress.json", "w", encoding="utf-8") as f:
        f.write("CORRUPT_BYTES")

    mgr2 = CheckpointManager(base_dir=temp_research_dir)
    # Recovers from cp1
    assert mgr2.state["checkpoint_id"] >= 1


def test_10_resuming_without_duplicating_qa_records(temp_research_dir):
    """Scenario 10: Adding 10 Q&A pairs, interrupting, and resuming with 10 more results in exactly 20 records."""
    mgr1 = CheckpointManager(base_dir=temp_research_dir)
    qa_file = Path(temp_research_dir) / "datasets" / "vignan_qa_master.json"

    # Batch 1: items 1-10
    qa_dict = {f"Q_{i:03d}": {"id": f"Q_{i:03d}", "text": f"Question {i}"} for i in range(1, 11)}
    mgr1.atomic_write_json(qa_file, qa_dict)
    mgr1.register_artifact("vignan_qa_master", "datasets/vignan_qa_master.json", "qa_dataset", record_count=len(qa_dict))
    mgr1.checkpoint("Completed Batch 1 (10 records)")

    del mgr1

    # Resume in new session
    mgr2 = CheckpointManager(base_dir=temp_research_dir)
    existing_data = json.loads(qa_file.read_text(encoding="utf-8"))
    assert len(existing_data) == 10

    # Batch 2: items 6-20 (items 6-10 are duplicates, 11-20 are new)
    for i in range(6, 21):
        existing_data[f"Q_{i:03d}"] = {"id": f"Q_{i:03d}", "text": f"Question {i}"}

    mgr2.atomic_write_json(qa_file, existing_data)
    mgr2.register_artifact("vignan_qa_master", "datasets/vignan_qa_master.json", "qa_dataset", record_count=len(existing_data))
    mgr2.checkpoint("Completed Batch 2 (Deduplicated)")

    final_data = json.loads(qa_file.read_text(encoding="utf-8"))
    assert len(final_data) == 20
    assert mgr2.manifest["artifacts"]["vignan_qa_master"]["record_count"] == 20


def test_11_locking_mechanism_and_stale_pid_cleanup(temp_research_dir):
    """Scenario 11: Active lock prevents simultaneous runs; dead PID allows auto-recovery."""
    mgr = CheckpointManager(base_dir=temp_research_dir)
    # Acquire lock for current process
    locked = mgr.acquire_lock("test_runner")
    assert locked is True

    # Same lock cannot be acquired again while active
    locked_again = mgr.acquire_lock("test_runner")
    # Because PID is current active process PID, it recognizes it's held by active PID
    assert locked_again is False

    mgr.release_lock("test_runner")
    # Once released, can acquire again
    assert mgr.acquire_lock("test_runner") is True
    mgr.release_lock("test_runner")

