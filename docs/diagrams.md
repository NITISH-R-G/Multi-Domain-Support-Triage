# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["custom_types.py"]
    click node_0 href "../custom_types.py"
    node_1["fix_type.py"]
    click node_1 href "../fix_type.py"
    node_2["conftest.py"]
    click node_2 href "../code/conftest.py"
    node_3["csv_io.py"]
    click node_3 href "../code/csv_io.py"
    node_4["compare_outputs.py"]
    click node_4 href "../code/compare_outputs.py"
    node_5["risk.py"]
    click node_5 href "../code/risk.py"
    node_6["openai_agent.py"]
    click node_6 href "../code/openai_agent.py"
    node_7["main.py"]
    click node_7 href "../code/main.py"
    node_8["eval_sample.py"]
    click node_8 href "../code/eval_sample.py"
    node_9["grounding.py"]
    click node_9 href "../code/grounding.py"
    node_10["eval_metrics.py"]
    click node_10 href "../code/eval_metrics.py"
    node_11["__main__.py"]
    click node_11 href "../code/__main__.py"
    node_12["run_eval.py"]
    click node_12 href "../code/run_eval.py"
    node_13["response_quality_report.py"]
    click node_13 href "../code/response_quality_report.py"
    node_14["ticket_hints.py"]
    click node_14 href "../code/ticket_hints.py"
    node_15["cross_ecosystem.py"]
    click node_15 href "../code/cross_ecosystem.py"
    node_16["postprocess.py"]
    click node_16 href "../code/postprocess.py"
    node_17["corpus.py"]
    click node_17 href "../code/corpus.py"
    node_18["config.py"]
    click node_18 href "../code/config.py"
    node_19["answer_synthesis.py"]
    click node_19 href "../code/answer_synthesis.py"
    node_20["retrieve.py"]
    click node_20 href "../code/retrieve.py"
    node_21["taxonomy.py"]
    click node_21 href "../code/taxonomy.py"
    node_22["test_sample_routing_golden.py"]
    click node_22 href "../code/tests/test_sample_routing_golden.py"
    node_23["test_ticket_hints.py"]
    click node_23 href "../code/tests/test_ticket_hints.py"
    node_24["test_eval_metrics.py"]
    click node_24 href "../code/tests/test_eval_metrics.py"
    node_25["test_csv_io.py"]
    click node_25 href "../code/tests/test_csv_io.py"
    node_26["test_cli_main.py"]
    click node_26 href "../code/tests/test_cli_main.py"
    node_27["test_module_invocation.py"]
    click node_27 href "../code/tests/test_module_invocation.py"
    node_28["test_merge_cli.py"]
    click node_28 href "../code/tests/test_merge_cli.py"
    node_29["test_taxonomy.py"]
    click node_29 href "../code/tests/test_taxonomy.py"
    node_30["test_risk.py"]
    click node_30 href "../code/tests/test_risk.py"
    node_31["test_cross_ecosystem.py"]
    click node_31 href "../code/tests/test_cross_ecosystem.py"
    node_32["capture_baseline.py"]
    click node_32 href "../scripts/capture_baseline.py"
    node_33["ai_qa_agent.py"]
    click node_33 href "../automation/ai_qa_agent.py"
    node_34["diagrams.py"]
    click node_34 href "../automation/diagrams.py"
    node_35["readme_generator.py"]
    click node_35 href "../automation/readme_generator.py"
    node_36["ai_maintainer.py"]
    click node_36 href "../automation/ai_maintainer.py"
    node_37["analyzer.py"]
    click node_37 href "../automation/analyzer.py"
    node_38["__init__.py"]
    click node_38 href "../automation/__init__.py"
    node_39["health_dashboard.py"]
    click node_39 href "../automation/health_dashboard.py"
    node_40["ai_agent.py"]
    click node_40 href "../automation/ai_agent.py"
    node_2 --> node_18
    node_2 --> node_18
    node_2 --> node_20
    node_4 --> node_3
    node_4 --> node_3
    node_4 --> node_3
    node_4 --> node_3
    node_4 --> node_10
    node_4 --> node_10
    node_4 --> node_10
    node_6 --> node_19
    node_6 --> node_18
    node_6 --> node_20
    node_6 --> node_20
    node_7 --> node_18
    node_7 --> node_18
    node_7 --> node_18
    node_7 --> node_18
    node_7 --> node_18
    node_7 --> node_18
    node_7 --> node_15
    node_7 --> node_3
    node_7 --> node_3
    node_7 --> node_3
    node_7 --> node_6
    node_7 --> node_40
    node_7 --> node_6
    node_7 --> node_40
    node_7 --> node_16
    node_7 --> node_20
    node_7 --> node_20
    node_7 --> node_20
    node_7 --> node_18
    node_7 --> node_5
    node_7 --> node_21
    node_7 --> node_14
    node_8 --> node_3
    node_8 --> node_3
    node_8 --> node_3
    node_8 --> node_3
    node_8 --> node_10
    node_8 --> node_10
    node_8 --> node_10
    node_9 --> node_17
    node_9 --> node_20
    node_11 --> node_7
    node_13 --> node_18
    node_13 --> node_18
    node_13 --> node_18
    node_13 --> node_3
    node_13 --> node_3
    node_13 --> node_9
    node_13 --> node_9
    node_13 --> node_20
    node_13 --> node_20
    node_16 --> node_18
    node_16 --> node_18
    node_16 --> node_9
    node_16 --> node_9
    node_16 --> node_20
    node_16 --> node_21
    node_16 --> node_21
    node_16 --> node_6
    node_16 --> node_40
    node_19 --> node_20
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_18
    node_20 --> node_17
    node_20 --> node_17
    node_20 --> node_17
    node_21 --> node_17
    node_22 --> node_18
    node_22 --> node_3
    node_22 --> node_3
    node_22 --> node_7
    node_23 --> node_14
    node_23 --> node_14
    node_24 --> node_10
    node_24 --> node_10
    node_24 --> node_10
    node_25 --> node_3
    node_25 --> node_3
    node_25 --> node_3
    node_25 --> node_3
    node_29 --> node_21
    node_29 --> node_21
    node_29 --> node_21
    node_29 --> node_17
    node_30 --> node_5
    node_31 --> node_15
```
