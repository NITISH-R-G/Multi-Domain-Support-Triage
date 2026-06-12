# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["custom_types.py"]
    click node_0 href "../custom_types.py"
    node_1["fix_type.py"]
    click node_1 href "../fix_type.py"
    node_2["capture_baseline.py"]
    click node_2 href "../scripts/capture_baseline.py"
    node_3["diagrams.py"]
    click node_3 href "../automation/diagrams.py"
    node_4["__init__.py"]
    click node_4 href "../automation/__init__.py"
    node_5["ai_maintainer.py"]
    click node_5 href "../automation/ai_maintainer.py"
    node_6["analyzer.py"]
    click node_6 href "../automation/analyzer.py"
    node_7["readme_generator.py"]
    click node_7 href "../automation/readme_generator.py"
    node_8["health_dashboard.py"]
    click node_8 href "../automation/health_dashboard.py"
    node_9["ai_qa_agent.py"]
    click node_9 href "../automation/ai_qa_agent.py"
    node_10["ai_agent.py"]
    click node_10 href "../automation/ai_agent.py"
    node_11["response_quality_report.py"]
    click node_11 href "../code/response_quality_report.py"
    node_12["config.py"]
    click node_12 href "../code/config.py"
    node_13["eval_metrics.py"]
    click node_13 href "../code/eval_metrics.py"
    node_14["compare_outputs.py"]
    click node_14 href "../code/compare_outputs.py"
    node_15["run_eval.py"]
    click node_15 href "../code/run_eval.py"
    node_16["postprocess.py"]
    click node_16 href "../code/postprocess.py"
    node_17["grounding.py"]
    click node_17 href "../code/grounding.py"
    node_18["corpus.py"]
    click node_18 href "../code/corpus.py"
    node_19["ticket_hints.py"]
    click node_19 href "../code/ticket_hints.py"
    node_20["retrieve.py"]
    click node_20 href "../code/retrieve.py"
    node_21["eval_sample.py"]
    click node_21 href "../code/eval_sample.py"
    node_22["risk.py"]
    click node_22 href "../code/risk.py"
    node_23["conftest.py"]
    click node_23 href "../code/conftest.py"
    node_24["main.py"]
    click node_24 href "../code/main.py"
    node_25["openai_agent.py"]
    click node_25 href "../code/openai_agent.py"
    node_26["csv_io.py"]
    click node_26 href "../code/csv_io.py"
    node_27["cross_ecosystem.py"]
    click node_27 href "../code/cross_ecosystem.py"
    node_28["taxonomy.py"]
    click node_28 href "../code/taxonomy.py"
    node_29["__main__.py"]
    click node_29 href "../code/__main__.py"
    node_30["answer_synthesis.py"]
    click node_30 href "../code/answer_synthesis.py"
    node_31["test_merge_cli.py"]
    click node_31 href "../code/tests/test_merge_cli.py"
    node_32["test_cli_main.py"]
    click node_32 href "../code/tests/test_cli_main.py"
    node_33["test_risk.py"]
    click node_33 href "../code/tests/test_risk.py"
    node_34["test_taxonomy.py"]
    click node_34 href "../code/tests/test_taxonomy.py"
    node_35["test_csv_io.py"]
    click node_35 href "../code/tests/test_csv_io.py"
    node_36["test_ticket_hints.py"]
    click node_36 href "../code/tests/test_ticket_hints.py"
    node_37["test_sample_routing_golden.py"]
    click node_37 href "../code/tests/test_sample_routing_golden.py"
    node_38["test_cross_ecosystem.py"]
    click node_38 href "../code/tests/test_cross_ecosystem.py"
    node_39["test_module_invocation.py"]
    click node_39 href "../code/tests/test_module_invocation.py"
    node_40["test_eval_metrics.py"]
    click node_40 href "../code/tests/test_eval_metrics.py"
    node_11 --> node_12
    node_11 --> node_12
    node_11 --> node_12
    node_11 --> node_26
    node_11 --> node_26
    node_11 --> node_17
    node_11 --> node_17
    node_11 --> node_20
    node_11 --> node_20
    node_14 --> node_26
    node_14 --> node_26
    node_14 --> node_26
    node_14 --> node_26
    node_14 --> node_13
    node_14 --> node_13
    node_14 --> node_13
    node_16 --> node_12
    node_16 --> node_12
    node_16 --> node_17
    node_16 --> node_17
    node_16 --> node_20
    node_16 --> node_28
    node_16 --> node_28
    node_16 --> node_10
    node_16 --> node_25
    node_17 --> node_18
    node_17 --> node_20
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_21 --> node_26
    node_21 --> node_26
    node_21 --> node_26
    node_21 --> node_26
    node_21 --> node_13
    node_21 --> node_13
    node_21 --> node_13
    node_23 --> node_12
    node_23 --> node_12
    node_23 --> node_20
    node_24 --> node_12
    node_24 --> node_12
    node_24 --> node_12
    node_24 --> node_12
    node_24 --> node_12
    node_24 --> node_12
    node_24 --> node_27
    node_24 --> node_26
    node_24 --> node_26
    node_24 --> node_26
    node_24 --> node_10
    node_24 --> node_25
    node_24 --> node_10
    node_24 --> node_25
    node_24 --> node_16
    node_24 --> node_20
    node_24 --> node_20
    node_24 --> node_20
    node_24 --> node_12
    node_24 --> node_22
    node_24 --> node_28
    node_24 --> node_19
    node_25 --> node_30
    node_25 --> node_12
    node_25 --> node_20
    node_25 --> node_20
    node_28 --> node_18
    node_29 --> node_24
    node_30 --> node_20
    node_33 --> node_22
    node_34 --> node_28
    node_34 --> node_28
    node_34 --> node_28
    node_34 --> node_18
    node_35 --> node_26
    node_35 --> node_26
    node_35 --> node_26
    node_35 --> node_26
    node_36 --> node_19
    node_36 --> node_19
    node_37 --> node_12
    node_37 --> node_26
    node_37 --> node_26
    node_37 --> node_24
    node_38 --> node_27
    node_40 --> node_13
    node_40 --> node_13
    node_40 --> node_13
```
