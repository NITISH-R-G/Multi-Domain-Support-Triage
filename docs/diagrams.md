# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["__init__.py"]
    click node_0 href "../automation/__init__.py"
    node_1["analyzer.py"]
    click node_1 href "../automation/analyzer.py"
    node_2["capture_baseline.py"]
    click node_2 href "../scripts/capture_baseline.py"
    node_3["retrieve.py"]
    click node_3 href "../code/retrieve.py"
    node_4["eval_metrics.py"]
    click node_4 href "../code/eval_metrics.py"
    node_5["taxonomy.py"]
    click node_5 href "../code/taxonomy.py"
    node_6["main.py"]
    click node_6 href "../code/main.py"
    node_7["answer_synthesis.py"]
    click node_7 href "../code/answer_synthesis.py"
    node_8["__main__.py"]
    click node_8 href "../code/__main__.py"
    node_9["ticket_hints.py"]
    click node_9 href "../code/ticket_hints.py"
    node_10["response_quality_report.py"]
    click node_10 href "../code/response_quality_report.py"
    node_11["corpus.py"]
    click node_11 href "../code/corpus.py"
    node_12["conftest.py"]
    click node_12 href "../code/conftest.py"
    node_13["eval_sample.py"]
    click node_13 href "../code/eval_sample.py"
    node_14["risk.py"]
    click node_14 href "../code/risk.py"
    node_15["__init__.py"]
    click node_15 href "../code/__init__.py"
    node_16["grounding.py"]
    click node_16 href "../code/grounding.py"
    node_17["config.py"]
    click node_17 href "../code/config.py"
    node_18["cross_ecosystem.py"]
    click node_18 href "../code/cross_ecosystem.py"
    node_19["openai_agent.py"]
    click node_19 href "../code/openai_agent.py"
    node_20["compare_outputs.py"]
    click node_20 href "../code/compare_outputs.py"
    node_21["csv_io.py"]
    click node_21 href "../code/csv_io.py"
    node_22["run_eval.py"]
    click node_22 href "../code/run_eval.py"
    node_23["postprocess.py"]
    click node_23 href "../code/postprocess.py"
    node_24["test_merge_cli.py"]
    click node_24 href "../code/tests/test_merge_cli.py"
    node_25["test_cli_main.py"]
    click node_25 href "../code/tests/test_cli_main.py"
    node_26["test_ticket_hints.py"]
    click node_26 href "../code/tests/test_ticket_hints.py"
    node_27["test_taxonomy.py"]
    click node_27 href "../code/tests/test_taxonomy.py"
    node_28["test_risk.py"]
    click node_28 href "../code/tests/test_risk.py"
    node_29["test_eval_metrics.py"]
    click node_29 href "../code/tests/test_eval_metrics.py"
    node_30["test_csv_io.py"]
    click node_30 href "../code/tests/test_csv_io.py"
    node_31["test_sample_routing_golden.py"]
    click node_31 href "../code/tests/test_sample_routing_golden.py"
    node_32["test_module_invocation.py"]
    click node_32 href "../code/tests/test_module_invocation.py"
    node_33["test_cross_ecosystem.py"]
    click node_33 href "../code/tests/test_cross_ecosystem.py"
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_17
    node_3 --> node_11
    node_3 --> node_11
    node_3 --> node_11
    node_5 --> node_11
    node_6 --> node_17
    node_6 --> node_17
    node_6 --> node_17
    node_6 --> node_17
    node_6 --> node_17
    node_6 --> node_17
    node_6 --> node_18
    node_6 --> node_21
    node_6 --> node_21
    node_6 --> node_21
    node_6 --> node_19
    node_6 --> node_19
    node_6 --> node_23
    node_6 --> node_3
    node_6 --> node_3
    node_6 --> node_3
    node_6 --> node_3
    node_6 --> node_14
    node_6 --> node_5
    node_6 --> node_9
    node_7 --> node_3
    node_8 --> node_6
    node_10 --> node_17
    node_10 --> node_17
    node_10 --> node_17
    node_10 --> node_21
    node_10 --> node_21
    node_10 --> node_11
    node_10 --> node_16
    node_10 --> node_16
    node_10 --> node_3
    node_10 --> node_3
    node_12 --> node_17
    node_12 --> node_17
    node_12 --> node_3
    node_13 --> node_21
    node_13 --> node_21
    node_13 --> node_21
    node_13 --> node_21
    node_13 --> node_4
    node_13 --> node_4
    node_13 --> node_4
    node_16 --> node_11
    node_16 --> node_3
    node_19 --> node_7
    node_19 --> node_17
    node_19 --> node_3
    node_19 --> node_3
    node_20 --> node_21
    node_20 --> node_21
    node_20 --> node_21
    node_20 --> node_21
    node_20 --> node_4
    node_20 --> node_4
    node_20 --> node_4
    node_23 --> node_17
    node_23 --> node_17
    node_23 --> node_16
    node_23 --> node_16
    node_23 --> node_3
    node_23 --> node_5
    node_23 --> node_5
    node_23 --> node_19
    node_26 --> node_9
    node_26 --> node_9
    node_27 --> node_5
    node_27 --> node_5
    node_27 --> node_5
    node_27 --> node_11
    node_28 --> node_14
    node_29 --> node_4
    node_29 --> node_4
    node_29 --> node_4
    node_30 --> node_21
    node_30 --> node_21
    node_30 --> node_21
    node_30 --> node_21
    node_31 --> node_17
    node_31 --> node_21
    node_31 --> node_21
    node_31 --> node_6
    node_33 --> node_18
```
