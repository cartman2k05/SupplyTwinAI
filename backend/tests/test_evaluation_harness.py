import pytest
from backend.app.db.database import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.db_loader_helper import ensure_db_initialized
from backend.app.models.user import User
from backend.app.models.recommendation import Recommendation, DisruptionMemory
from backend.app.models.audit import AuditLog
from evaluation.scenario_generator import scenario_generator
from evaluation.metrics import metrics_engine
from evaluation.oracle_manager import oracle_manager
from evaluation.run_eval import EvaluationHarness

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_db_initialized(db)
    finally:
        db.close()

def test_scenario_generator():
    scenarios = scenario_generator.generate_scenarios(seed=42, target_count=60)
    assert len(scenarios) == 60
    first = scenarios[0]
    assert "scenario_id" in first
    assert "target_global_id" in first
    assert "acceptable_action_class" in first
    assert "ground_truth_impacted_entities" in first
    assert len(first["ground_truth_impacted_entities"]) >= 3

def test_metrics_engine_formulas():
    # Precision / Recall test
    gt = ["supplier:1", "product:1", "warehouse:1"]
    pred = ["supplier:1", "product:1", "supplier:99"]

    pr = metrics_engine.calculate_precision_recall(pred, gt)
    assert pr["precision"] == round(2 / 3, 4)
    assert pr["recall"] == round(2 / 3, 4)
    assert pr["f1_score"] == round(2 / 3, 4)

    # Hallucination rate test
    valid_ids = {"supplier:1", "product:1", "warehouse:1"}
    hall_rate = metrics_engine.calculate_hallucination_rate(["supplier:1", "supplier:999"], valid_ids)
    assert hall_rate == 0.5

    # Recommendation validity test
    val_score = metrics_engine.calculate_recommendation_validity("SWITCH_SUPPLIER", "SWITCH_SUPPLIER")
    assert val_score == 1.0

    val_invalid = metrics_engine.calculate_recommendation_validity("REROUTE_SHIPMENT", "SWITCH_SUPPLIER")
    assert val_invalid == 0.0

def test_oracle_manager_policy():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "manager").first()
        rec = Recommendation(
            global_id="recommendation:eval_test_1",
            entity_global_id="supplier:1",
            action_type="SWITCH_SUPPLIER",
            title="Switch Supplier",
            description="Test description",
            confidence_score=0.90,
            status="pending"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

        res = oracle_manager.evaluate_and_decide(db, rec.recommendation_id, "SWITCH_SUPPLIER", user)
        assert res["decision"] == "accepted"
        assert res["is_valid"] is True

        # Check DB audit & memory
        audit = db.query(AuditLog).filter(AuditLog.resource_id == rec.global_id).first()
        assert audit is not None
        assert "RECOMMENDATION_ACCEPTED" in audit.action

        mem = db.query(DisruptionMemory).filter(DisruptionMemory.entity_global_id == "supplier:1").first()
        assert mem is not None
    finally:
        db.close()

def test_evaluation_harness_mini_run():
    harness = EvaluationHarness()
    summary = harness.run_benchmark(scenario_count=5, seed=42)
    assert summary["scenarios_evaluated"] == 5
    assert "config_a" in summary["configurations"]
    assert "config_b" in summary["configurations"]
    assert "config_c" in summary["configurations"]

    cfg_b = summary["configurations"]["config_b"]
    assert cfg_b["mean_precision"] >= 0.0
    assert cfg_b["grounding_rate"] > 0.5
