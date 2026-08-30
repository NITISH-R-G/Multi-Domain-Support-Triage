# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["fix_type.py"]
    click node_0 href "../fix_type.py"
    node_1["main.py"]
    click node_1 href "../code/main.py"
    node_2["conftest.py"]
    click node_2 href "../code/conftest.py"
    node_3["answer_synthesis.py"]
    click node_3 href "../code/answer_synthesis.py"
    node_4["compare_outputs.py"]
    click node_4 href "../code/compare_outputs.py"
    node_5["eval_sample.py"]
    click node_5 href "../code/eval_sample.py"
    node_6["__main__.py"]
    click node_6 href "../code/__main__.py"
    node_7["config.py"]
    click node_7 href "../code/config.py"
    node_8["postprocess.py"]
    click node_8 href "../code/postprocess.py"
    node_9["ticket_hints.py"]
    click node_9 href "../code/ticket_hints.py"
    node_10["run_eval.py"]
    click node_10 href "../code/run_eval.py"
    node_11["retrieve.py"]
    click node_11 href "../code/retrieve.py"
    node_12["eval_metrics.py"]
    click node_12 href "../code/eval_metrics.py"
    node_13["grounding.py"]
    click node_13 href "../code/grounding.py"
    node_14["cross_ecosystem.py"]
    click node_14 href "../code/cross_ecosystem.py"
    node_15["response_quality_report.py"]
    click node_15 href "../code/response_quality_report.py"
    node_16["risk.py"]
    click node_16 href "../code/risk.py"
    node_17["taxonomy.py"]
    click node_17 href "../code/taxonomy.py"
    node_18["openai_agent.py"]
    click node_18 href "../code/openai_agent.py"
    node_19["corpus.py"]
    click node_19 href "../code/corpus.py"
    node_20["csv_io.py"]
    click node_20 href "../code/csv_io.py"
    node_21["test_module_invocation.py"]
    click node_21 href "../code/tests/test_module_invocation.py"
    node_22["test_eval_metrics.py"]
    click node_22 href "../code/tests/test_eval_metrics.py"
    node_23["test_risk.py"]
    click node_23 href "../code/tests/test_risk.py"
    node_24["test_merge_cli.py"]
    click node_24 href "../code/tests/test_merge_cli.py"
    node_25["test_sample_routing_golden.py"]
    click node_25 href "../code/tests/test_sample_routing_golden.py"
    node_26["test_csv_io.py"]
    click node_26 href "../code/tests/test_csv_io.py"
    node_27["test_taxonomy.py"]
    click node_27 href "../code/tests/test_taxonomy.py"
    node_28["test_cli_main.py"]
    click node_28 href "../code/tests/test_cli_main.py"
    node_29["test_cross_ecosystem.py"]
    click node_29 href "../code/tests/test_cross_ecosystem.py"
    node_30["test_ticket_hints.py"]
    click node_30 href "../code/tests/test_ticket_hints.py"
    node_31["capture_baseline.py"]
    click node_31 href "../scripts/capture_baseline.py"
    node_32["__init__.py"]
    click node_32 href "../automation/__init__.py"
    node_33["ai_agent.py"]
    click node_33 href "../automation/ai_agent.py"
    node_34["analyzer.py"]
    click node_34 href "../automation/analyzer.py"
    node_35["readme_generator.py"]
    click node_35 href "../automation/readme_generator.py"
    node_36["diagrams.py"]
    click node_36 href "../automation/diagrams.py"
    node_37["ai_qa_agent.py"]
    click node_37 href "../automation/ai_qa_agent.py"
    node_38["health_dashboard.py"]
    click node_38 href "../automation/health_dashboard.py"
    node_39["ai_maintainer.py"]
    click node_39 href "../automation/ai_maintainer.py"
    node_1 --> node_7
    node_1 --> node_7
    node_1 --> node_7
    node_1 --> node_7
    node_1 --> node_7
    node_1 --> node_7
    node_1 --> node_14
    node_1 --> node_20
    node_1 --> node_20
    node_1 --> node_20
    node_1 --> node_18
    node_1 --> node_33
    node_1 --> node_18
    node_1 --> node_33
    node_1 --> node_8
    node_1 --> node_11
    node_1 --> node_11
    node_1 --> node_11
    node_1 --> node_7
    node_1 --> node_16
    node_1 --> node_17
    node_1 --> node_9
    node_2 --> node_7
    node_2 --> node_7
    node_2 --> node_11
    node_3 --> node_11
    node_4 --> node_20
    node_4 --> node_20
    node_4 --> node_20
    node_4 --> node_20
    node_4 --> node_12
    node_4 --> node_12
    node_4 --> node_12
    node_5 --> node_20
    node_5 --> node_20
    node_5 --> node_20
    node_5 --> node_20
    node_5 --> node_12
    node_5 --> node_12
    node_5 --> node_12
    node_6 --> node_1
    node_8 --> node_7
    node_8 --> node_7
    node_8 --> node_13
    node_8 --> node_13
    node_8 --> node_11
    node_8 --> node_17
    node_8 --> node_17
    node_8 --> node_18
    node_8 --> node_33
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_19
    node_11 --> node_19
    node_11 --> node_19
    node_13 --> node_19
    node_13 --> node_11
    node_15 --> node_7
    node_15 --> node_7
    node_15 --> node_7
    node_15 --> node_20
    node_15 --> node_20
    node_15 --> node_13
    node_15 --> node_13
    node_15 --> node_11
    node_15 --> node_11
    node_17 --> node_19
    node_18 --> node_3
    node_18 --> node_7
    node_18 --> node_11
    node_18 --> node_11
    node_22 --> node_12
    node_22 --> node_12
    node_22 --> node_12
    node_23 --> node_16
    node_25 --> node_7
    node_25 --> node_20
    node_25 --> node_20
    node_25 --> node_1
    node_26 --> node_20
    node_26 --> node_20
    node_26 --> node_20
    node_26 --> node_20
    node_27 --> node_17
    node_27 --> node_17
    node_27 --> node_17
    node_27 --> node_19
    node_29 --> node_14
    node_30 --> node_9
    node_30 --> node_9
```
