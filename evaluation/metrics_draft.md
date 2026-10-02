# SupplyTwinAI — Phase 5 Evaluation Design & Ground-Truth Specification

**Document Path:** `evaluation/metrics_draft.md`  
**Phase:** Phase 5 (Knowledge Graph Construction & Evaluation Harness Design)  
**Authors:** Team 12 Lead Engineer  

---

## 1. Goal of the Evaluation Harness

Per `DECISIONS.md` §5, the evaluation harness measures and compares four system configurations:
* **Configuration A:** Base LLM only (Zero-shot / Direct Gemini API prompt without Knowledge Graph context).
* **Configuration B:** LLM + GraphRAG (Gemini API with retrieved sub-graph context from Neo4j).
* **Configuration C:** LLM + GraphRAG + Persistent Disruption Memory (Full system with past disruption memory retrieval).
* **Configuration D (Optional Baseline):** Deterministic Rule-Based Engine (No LLM).

---

## 2. Injected Scenario Catalog & Ground Truth Labels

Every injected disruption records exact ground-truth affected entities and acceptable action classes (§4.6 REQ-1/REQ-2):

```json
[
  {
    "scenario_id": "SCENARIO-SUP-01",
    "event_type": "SUPPLIER_FAILURE",
    "target_global_id": "supplier:1",
    "acceptable_action_class": "SWITCH_SUPPLIER",
    "ground_truth_impacted_entities": ["supplier:1", "product:1", "warehouse:1", "order:1", "shipment:1"]
  },
  {
    "scenario_id": "SCENARIO-LOG-01",
    "event_type": "SHIPMENT_DELAY_CLUSTER",
    "target_global_id": "shipment:77202",
    "acceptable_action_class": "REROUTE_SHIPMENT",
    "ground_truth_impacted_entities": ["shipment:77202", "order:77202", "vehicle:5"]
  },
  {
    "scenario_id": "SCENARIO-WTH-01",
    "event_type": "WEATHER_EVENT",
    "target_global_id": "warehouse:1",
    "acceptable_action_class": "EXPEDITE_SHIPPING",
    "ground_truth_impacted_entities": ["warehouse:1", "product:10", "order:5", "shipment:5"]
  }
]
```

---

## 3. Evaluation Metrics & Programmatic Formulas

1. **Affected Entity Precision ($P_{\text{entity}}$):**
   $$P_{\text{entity}} = \frac{|\text{Identified Affected Entities} \cap \text{Ground Truth Entities}|}{|\text{Identified Affected Entities}|}$$

2. **Affected Entity Recall ($R_{\text{entity}}$):**
   $$R_{\text{entity}} = \frac{|\text{Identified Affected Entities} \cap \text{Ground Truth Entities}|}{|\text{Ground Truth Entities}|}$$

3. **Hallucinated-ID Rate ($H_{\text{rate}}$):**
   Fraction of cited `global_id` entities in the response/recommendation that do not exist in the Neo4j Knowledge Graph:
   $$H_{\text{rate}} = \frac{|\{e \in \text{Cited IDs} \mid e \notin \text{Neo4j KG}\}|}{|\text{Cited IDs}|}$$

4. **Grounding Rate ($G_{\text{rate}}$):**
   Fraction of factual claims in recommendations traceable directly to stored retrieved Neo4j GraphRAG facts.

5. **Recommendation Action Validity ($V_{\text{action}}$):**
   Binary check (0 or 1) verifying that the recommended alternate supplier supplies the required product and possesses higher reliability than the disrupted primary supplier.

6. **Graph Sync Latency ($T_{\text{sync}}$):**
   Time taken for PostgreSQL entity mutations to reflect in Neo4j graph nodes ($T_{\text{sync}} < 30.0\text{ s}$ per NFR-P3).
