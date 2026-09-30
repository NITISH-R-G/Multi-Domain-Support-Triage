# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["fix_type.py"]
    click node_0 href "../fix_type.py"
    node_1["hybrid_types.py"]
    click node_1 href "../hybrid_types.py"
    node_2["__init__.py"]
    click node_2 href "../automation/__init__.py"
    node_3["readme_generator.py"]
    click node_3 href "../automation/readme_generator.py"
    node_4["analyzer.py"]
    click node_4 href "../automation/analyzer.py"
    node_5["ai_qa_agent.py"]
    click node_5 href "../automation/ai_qa_agent.py"
    node_6["ai_agent.py"]
    click node_6 href "../automation/ai_agent.py"
    node_7["ai_maintainer.py"]
    click node_7 href "../automation/ai_maintainer.py"
    node_8["diagrams.py"]
    click node_8 href "../automation/diagrams.py"
    node_9["health_dashboard.py"]
    click node_9 href "../automation/health_dashboard.py"
    node_10["capture_baseline.py"]
    click node_10 href "../scripts/capture_baseline.py"
    node_11["retrieve.py"]
    click node_11 href "../code/retrieve.py"
    node_12["eval_metrics.py"]
    click node_12 href "../code/eval_metrics.py"
    node_13["taxonomy.py"]
    click node_13 href "../code/taxonomy.py"
    node_14["main.py"]
    click node_14 href "../code/main.py"
    node_15["answer_synthesis.py"]
    click node_15 href "../code/answer_synthesis.py"
    node_16["__main__.py"]
    click node_16 href "../code/__main__.py"
    node_17["ticket_hints.py"]
    click node_17 href "../code/ticket_hints.py"
    node_18["response_quality_report.py"]
    click node_18 href "../code/response_quality_report.py"
    node_19["corpus.py"]
    click node_19 href "../code/corpus.py"
    node_20["conftest.py"]
    click node_20 href "../code/conftest.py"
    node_21["eval_sample.py"]
    click node_21 href "../code/eval_sample.py"
    node_22["risk.py"]
    click node_22 href "../code/risk.py"
    node_23["grounding.py"]
    click node_23 href "../code/grounding.py"
    node_24["config.py"]
    click node_24 href "../code/config.py"
    node_25["cross_ecosystem.py"]
    click node_25 href "../code/cross_ecosystem.py"
    node_26["openai_agent.py"]
    click node_26 href "../code/openai_agent.py"
    node_27["compare_outputs.py"]
    click node_27 href "../code/compare_outputs.py"
    node_28["csv_io.py"]
    click node_28 href "../code/csv_io.py"
    node_29["run_eval.py"]
    click node_29 href "../code/run_eval.py"
    node_30["postprocess.py"]
    click node_30 href "../code/postprocess.py"
    node_31["test_merge_cli.py"]
    click node_31 href "../code/tests/test_merge_cli.py"
    node_32["test_cli_main.py"]
    click node_32 href "../code/tests/test_cli_main.py"
    node_33["test_ticket_hints.py"]
    click node_33 href "../code/tests/test_ticket_hints.py"
    node_34["test_taxonomy.py"]
    click node_34 href "../code/tests/test_taxonomy.py"
    node_35["test_risk.py"]
    click node_35 href "../code/tests/test_risk.py"
    node_36["test_eval_metrics.py"]
    click node_36 href "../code/tests/test_eval_metrics.py"
    node_37["test_csv_io.py"]
    click node_37 href "../code/tests/test_csv_io.py"
    node_38["test_sample_routing_golden.py"]
    click node_38 href "../code/tests/test_sample_routing_golden.py"
    node_39["test_module_invocation.py"]
    click node_39 href "../code/tests/test_module_invocation.py"
    node_40["test_cross_ecosystem.py"]
    click node_40 href "../code/tests/test_cross_ecosystem.py"
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_24
    node_11 --> node_19
    node_11 --> node_19
    node_11 --> node_19
    node_13 --> node_19
    node_14 --> node_24
    node_14 --> node_24
    node_14 --> node_24
    node_14 --> node_24
    node_14 --> node_24
    node_14 --> node_24
    node_14 --> node_25
    node_14 --> node_28
    node_14 --> node_28
    node_14 --> node_28
    node_14 --> node_6
    node_14 --> node_26
    node_14 --> node_6
    node_14 --> node_26
    node_14 --> node_30
    node_14 --> node_11
    node_14 --> node_11
    node_14 --> node_11
    node_14 --> node_24
    node_14 --> node_22
    node_14 --> node_13
    node_14 --> node_17
    node_15 --> node_11
    node_16 --> node_14
    node_18 --> node_24
    node_18 --> node_24
    node_18 --> node_24
    node_18 --> node_28
    node_18 --> node_28
    node_18 --> node_23
    node_18 --> node_23
    node_18 --> node_11
    node_18 --> node_11
    node_20 --> node_24
    node_20 --> node_24
    node_20 --> node_11
    node_21 --> node_28
    node_21 --> node_28
    node_21 --> node_28
    node_21 --> node_28
    node_21 --> node_12
    node_21 --> node_12
    node_21 --> node_12
    node_23 --> node_19
    node_23 --> node_11
    node_26 --> node_15
    node_26 --> node_24
    node_26 --> node_11
    node_26 --> node_11
    node_27 --> node_28
    node_27 --> node_28
    node_27 --> node_28
    node_27 --> node_28
    node_27 --> node_12
    node_27 --> node_12
    node_27 --> node_12
    node_30 --> node_24
    node_30 --> node_24
    node_30 --> node_23
    node_30 --> node_23
    node_30 --> node_11
    node_30 --> node_13
    node_30 --> node_13
    node_30 --> node_6
    node_30 --> node_26
    node_33 --> node_17
    node_33 --> node_17
    node_34 --> node_13
    node_34 --> node_13
    node_34 --> node_13
    node_34 --> node_19
    node_35 --> node_22
    node_36 --> node_12
    node_36 --> node_12
    node_36 --> node_12
    node_37 --> node_28
    node_37 --> node_28
    node_37 --> node_28
    node_37 --> node_28
    node_38 --> node_24
    node_38 --> node_28
    node_38 --> node_28
    node_38 --> node_14
    node_40 --> node_25
```
