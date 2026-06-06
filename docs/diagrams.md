# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["conftest.py"]
    click node_0 href "../code/conftest.py"
    node_1["csv_io.py"]
    click node_1 href "../code/csv_io.py"
    node_2["compare_outputs.py"]
    click node_2 href "../code/compare_outputs.py"
    node_3["risk.py"]
    click node_3 href "../code/risk.py"
    node_4["openai_agent.py"]
    click node_4 href "../code/openai_agent.py"
    node_5["main.py"]
    click node_5 href "../code/main.py"
    node_6["eval_sample.py"]
    click node_6 href "../code/eval_sample.py"
    node_7["grounding.py"]
    click node_7 href "../code/grounding.py"
    node_8["eval_metrics.py"]
    click node_8 href "../code/eval_metrics.py"
    node_9["__main__.py"]
    click node_9 href "../code/__main__.py"
    node_10["run_eval.py"]
    click node_10 href "../code/run_eval.py"
    node_11["response_quality_report.py"]
    click node_11 href "../code/response_quality_report.py"
    node_12["ticket_hints.py"]
    click node_12 href "../code/ticket_hints.py"
    node_13["cross_ecosystem.py"]
    click node_13 href "../code/cross_ecosystem.py"
    node_14["postprocess.py"]
    click node_14 href "../code/postprocess.py"
    node_15["corpus.py"]
    click node_15 href "../code/corpus.py"
    node_16["config.py"]
    click node_16 href "../code/config.py"
    node_17["answer_synthesis.py"]
    click node_17 href "../code/answer_synthesis.py"
    node_18["retrieve.py"]
    click node_18 href "../code/retrieve.py"
    node_19["taxonomy.py"]
    click node_19 href "../code/taxonomy.py"
    node_20["test_sample_routing_golden.py"]
    click node_20 href "../code/tests/test_sample_routing_golden.py"
    node_21["test_ticket_hints.py"]
    click node_21 href "../code/tests/test_ticket_hints.py"
    node_22["test_eval_metrics.py"]
    click node_22 href "../code/tests/test_eval_metrics.py"
    node_23["test_csv_io.py"]
    click node_23 href "../code/tests/test_csv_io.py"
    node_24["test_cli_main.py"]
    click node_24 href "../code/tests/test_cli_main.py"
    node_25["test_module_invocation.py"]
    click node_25 href "../code/tests/test_module_invocation.py"
    node_26["test_merge_cli.py"]
    click node_26 href "../code/tests/test_merge_cli.py"
    node_27["test_taxonomy.py"]
    click node_27 href "../code/tests/test_taxonomy.py"
    node_28["test_risk.py"]
    click node_28 href "../code/tests/test_risk.py"
    node_29["test_cross_ecosystem.py"]
    click node_29 href "../code/tests/test_cross_ecosystem.py"
    node_30["capture_baseline.py"]
    click node_30 href "../scripts/capture_baseline.py"
    node_31["ai_qa_agent.py"]
    click node_31 href "../automation/ai_qa_agent.py"
    node_32["diagrams.py"]
    click node_32 href "../automation/diagrams.py"
    node_33["readme_generator.py"]
    click node_33 href "../automation/readme_generator.py"
    node_34["analyzer.py"]
    click node_34 href "../automation/analyzer.py"
    node_35["__init__.py"]
    click node_35 href "../automation/__init__.py"
    node_36["ai_agent.py"]
    click node_36 href "../automation/ai_agent.py"
    node_0 --> node_16
    node_0 --> node_16
    node_0 --> node_18
    node_2 --> node_1
    node_2 --> node_1
    node_2 --> node_1
    node_2 --> node_1
    node_2 --> node_8
    node_2 --> node_8
    node_2 --> node_8
    node_4 --> node_17
    node_4 --> node_16
    node_4 --> node_18
    node_4 --> node_18
    node_5 --> node_16
    node_5 --> node_16
    node_5 --> node_16
    node_5 --> node_16
    node_5 --> node_16
    node_5 --> node_16
    node_5 --> node_16
    node_5 --> node_13
    node_5 --> node_1
    node_5 --> node_1
    node_5 --> node_1
    node_5 --> node_4
    node_5 --> node_36
    node_5 --> node_4
    node_5 --> node_36
    node_5 --> node_14
    node_5 --> node_18
    node_5 --> node_18
    node_5 --> node_18
    node_5 --> node_18
    node_5 --> node_3
    node_5 --> node_19
    node_5 --> node_12
    node_6 --> node_1
    node_6 --> node_1
    node_6 --> node_1
    node_6 --> node_1
    node_6 --> node_8
    node_6 --> node_8
    node_6 --> node_8
    node_7 --> node_15
    node_7 --> node_18
    node_9 --> node_5
    node_11 --> node_16
    node_11 --> node_16
    node_11 --> node_16
    node_11 --> node_1
    node_11 --> node_1
    node_11 --> node_7
    node_11 --> node_7
    node_11 --> node_18
    node_11 --> node_18
    node_11 --> node_18
    node_14 --> node_16
    node_14 --> node_16
    node_14 --> node_7
    node_14 --> node_7
    node_14 --> node_18
    node_14 --> node_19
    node_14 --> node_19
    node_14 --> node_4
    node_14 --> node_36
    node_17 --> node_18
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_15
    node_18 --> node_15
    node_18 --> node_15
    node_19 --> node_15
    node_20 --> node_16
    node_20 --> node_1
    node_20 --> node_1
    node_20 --> node_5
    node_20 --> node_18
    node_21 --> node_12
    node_21 --> node_12
    node_22 --> node_8
    node_22 --> node_8
    node_22 --> node_8
    node_23 --> node_1
    node_23 --> node_1
    node_23 --> node_1
    node_23 --> node_1
    node_27 --> node_19
    node_27 --> node_19
    node_27 --> node_19
    node_27 --> node_15
    node_28 --> node_3
    node_29 --> node_13
```
