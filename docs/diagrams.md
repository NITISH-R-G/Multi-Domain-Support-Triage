# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["fix.py"]
    click node_0 href "../fix.py"
    node_1["fix_type.py"]
    click node_1 href "../fix_type.py"
    node_2["main.py"]
    click node_2 href "../code/main.py"
    node_3["conftest.py"]
    click node_3 href "../code/conftest.py"
    node_4["answer_synthesis.py"]
    click node_4 href "../code/answer_synthesis.py"
    node_5["compare_outputs.py"]
    click node_5 href "../code/compare_outputs.py"
    node_6["eval_sample.py"]
    click node_6 href "../code/eval_sample.py"
    node_7["__main__.py"]
    click node_7 href "../code/__main__.py"
    node_8["config.py"]
    click node_8 href "../code/config.py"
    node_9["postprocess.py"]
    click node_9 href "../code/postprocess.py"
    node_10["ticket_hints.py"]
    click node_10 href "../code/ticket_hints.py"
    node_11["run_eval.py"]
    click node_11 href "../code/run_eval.py"
    node_12["retrieve.py"]
    click node_12 href "../code/retrieve.py"
    node_13["eval_metrics.py"]
    click node_13 href "../code/eval_metrics.py"
    node_14["grounding.py"]
    click node_14 href "../code/grounding.py"
    node_15["cross_ecosystem.py"]
    click node_15 href "../code/cross_ecosystem.py"
    node_16["response_quality_report.py"]
    click node_16 href "../code/response_quality_report.py"
    node_17["risk.py"]
    click node_17 href "../code/risk.py"
    node_18["taxonomy.py"]
    click node_18 href "../code/taxonomy.py"
    node_19["openai_agent.py"]
    click node_19 href "../code/openai_agent.py"
    node_20["corpus.py"]
    click node_20 href "../code/corpus.py"
    node_21["csv_io.py"]
    click node_21 href "../code/csv_io.py"
    node_22["test_module_invocation.py"]
    click node_22 href "../code/tests/test_module_invocation.py"
    node_23["test_eval_metrics.py"]
    click node_23 href "../code/tests/test_eval_metrics.py"
    node_24["test_risk.py"]
    click node_24 href "../code/tests/test_risk.py"
    node_25["test_merge_cli.py"]
    click node_25 href "../code/tests/test_merge_cli.py"
    node_26["test_sample_routing_golden.py"]
    click node_26 href "../code/tests/test_sample_routing_golden.py"
    node_27["test_csv_io.py"]
    click node_27 href "../code/tests/test_csv_io.py"
    node_28["test_taxonomy.py"]
    click node_28 href "../code/tests/test_taxonomy.py"
    node_29["test_cli_main.py"]
    click node_29 href "../code/tests/test_cli_main.py"
    node_30["test_cross_ecosystem.py"]
    click node_30 href "../code/tests/test_cross_ecosystem.py"
    node_31["test_ticket_hints.py"]
    click node_31 href "../code/tests/test_ticket_hints.py"
    node_32["capture_baseline.py"]
    click node_32 href "../scripts/capture_baseline.py"
    node_33["__init__.py"]
    click node_33 href "../automation/__init__.py"
    node_34["ai_agent.py"]
    click node_34 href "../automation/ai_agent.py"
    node_35["analyzer.py"]
    click node_35 href "../automation/analyzer.py"
    node_36["readme_generator.py"]
    click node_36 href "../automation/readme_generator.py"
    node_37["diagrams.py"]
    click node_37 href "../automation/diagrams.py"
    node_38["ai_qa_agent.py"]
    click node_38 href "../automation/ai_qa_agent.py"
    node_39["health_dashboard.py"]
    click node_39 href "../automation/health_dashboard.py"
    node_40["ai_maintainer.py"]
    click node_40 href "../automation/ai_maintainer.py"
    node_2 --> node_8
    node_2 --> node_8
    node_2 --> node_8
    node_2 --> node_8
    node_2 --> node_8
    node_2 --> node_8
    node_2 --> node_15
    node_2 --> node_21
    node_2 --> node_21
    node_2 --> node_21
    node_2 --> node_19
    node_2 --> node_34
    node_2 --> node_19
    node_2 --> node_34
    node_2 --> node_9
    node_2 --> node_12
    node_2 --> node_12
    node_2 --> node_12
    node_2 --> node_8
    node_2 --> node_17
    node_2 --> node_18
    node_2 --> node_10
    node_3 --> node_8
    node_3 --> node_8
    node_3 --> node_12
    node_4 --> node_12
    node_5 --> node_21
    node_5 --> node_21
    node_5 --> node_21
    node_5 --> node_21
    node_5 --> node_13
    node_5 --> node_13
    node_5 --> node_13
    node_6 --> node_21
    node_6 --> node_21
    node_6 --> node_21
    node_6 --> node_21
    node_6 --> node_13
    node_6 --> node_13
    node_6 --> node_13
    node_7 --> node_2
    node_9 --> node_8
    node_9 --> node_8
    node_9 --> node_14
    node_9 --> node_14
    node_9 --> node_12
    node_9 --> node_18
    node_9 --> node_18
    node_9 --> node_19
    node_9 --> node_34
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_8
    node_12 --> node_20
    node_12 --> node_20
    node_12 --> node_20
    node_14 --> node_20
    node_14 --> node_12
    node_16 --> node_8
    node_16 --> node_8
    node_16 --> node_8
    node_16 --> node_21
    node_16 --> node_21
    node_16 --> node_14
    node_16 --> node_14
    node_16 --> node_12
    node_16 --> node_12
    node_18 --> node_20
    node_19 --> node_4
    node_19 --> node_8
    node_19 --> node_12
    node_19 --> node_12
    node_23 --> node_13
    node_23 --> node_13
    node_23 --> node_13
    node_24 --> node_17
    node_26 --> node_8
    node_26 --> node_21
    node_26 --> node_21
    node_26 --> node_2
    node_27 --> node_21
    node_27 --> node_21
    node_27 --> node_21
    node_27 --> node_21
    node_28 --> node_18
    node_28 --> node_18
    node_28 --> node_18
    node_28 --> node_20
    node_30 --> node_15
    node_31 --> node_10
    node_31 --> node_10
```
