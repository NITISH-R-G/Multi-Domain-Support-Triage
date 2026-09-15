# Architecture Diagrams

## Dependency Graph

```mermaid
graph TD
    node_0["analyzer.py"]
    click node_0 href "../automation/analyzer.py"
    node_1["__init__.py"]
    click node_1 href "../automation/__init__.py"
    node_2["ai_maintainer.py"]
    click node_2 href "../automation/ai_maintainer.py"
    node_3["ai_agent.py"]
    click node_3 href "../automation/ai_agent.py"
    node_4["ai_qa_agent.py"]
    click node_4 href "../automation/ai_qa_agent.py"
    node_5["health_dashboard.py"]
    click node_5 href "../automation/health_dashboard.py"
    node_6["diagrams.py"]
    click node_6 href "../automation/diagrams.py"
    node_7["readme_generator.py"]
    click node_7 href "../automation/readme_generator.py"
    node_8["risk.py"]
    click node_8 href "../code/risk.py"
    node_9["csv_io.py"]
    click node_9 href "../code/csv_io.py"
    node_10["retrieve.py"]
    click node_10 href "../code/retrieve.py"
    node_11["corpus.py"]
    click node_11 href "../code/corpus.py"
    node_12["eval_metrics.py"]
    click node_12 href "../code/eval_metrics.py"
    node_13["run_eval.py"]
    click node_13 href "../code/run_eval.py"
    node_14["answer_synthesis.py"]
    click node_14 href "../code/answer_synthesis.py"
    node_15["config.py"]
    click node_15 href "../code/config.py"
    node_16["taxonomy.py"]
    click node_16 href "../code/taxonomy.py"
    node_17["grounding.py"]
    click node_17 href "../code/grounding.py"
    node_18["postprocess.py"]
    click node_18 href "../code/postprocess.py"
    node_19["cross_ecosystem.py"]
    click node_19 href "../code/cross_ecosystem.py"
    node_20["eval_sample.py"]
    click node_20 href "../code/eval_sample.py"
    node_21["ticket_hints.py"]
    click node_21 href "../code/ticket_hints.py"
    node_22["main.py"]
    click node_22 href "../code/main.py"
    node_23["openai_agent.py"]
    click node_23 href "../code/openai_agent.py"
    node_24["response_quality_report.py"]
    click node_24 href "../code/response_quality_report.py"
    node_25["conftest.py"]
    click node_25 href "../code/conftest.py"
    node_26["__main__.py"]
    click node_26 href "../code/__main__.py"
    node_27["compare_outputs.py"]
    click node_27 href "../code/compare_outputs.py"
    node_28["test_cli_main.py"]
    click node_28 href "../code/tests/test_cli_main.py"
    node_29["test_merge_cli.py"]
    click node_29 href "../code/tests/test_merge_cli.py"
    node_30["test_module_invocation.py"]
    click node_30 href "../code/tests/test_module_invocation.py"
    node_31["test_taxonomy.py"]
    click node_31 href "../code/tests/test_taxonomy.py"
    node_32["test_risk.py"]
    click node_32 href "../code/tests/test_risk.py"
    node_33["test_csv_io.py"]
    click node_33 href "../code/tests/test_csv_io.py"
    node_34["test_eval_metrics.py"]
    click node_34 href "../code/tests/test_eval_metrics.py"
    node_35["test_sample_routing_golden.py"]
    click node_35 href "../code/tests/test_sample_routing_golden.py"
    node_36["test_ticket_hints.py"]
    click node_36 href "../code/tests/test_ticket_hints.py"
    node_37["test_cross_ecosystem.py"]
    click node_37 href "../code/tests/test_cross_ecosystem.py"
    node_38["capture_baseline.py"]
    click node_38 href "../scripts/capture_baseline.py"
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_15
    node_10 --> node_11
    node_10 --> node_11
    node_10 --> node_11
    node_14 --> node_10
    node_16 --> node_11
    node_17 --> node_11
    node_17 --> node_10
    node_18 --> node_15
    node_18 --> node_15
    node_18 --> node_17
    node_18 --> node_17
    node_18 --> node_10
    node_18 --> node_16
    node_18 --> node_16
    node_18 --> node_3
    node_18 --> node_23
    node_20 --> node_9
    node_20 --> node_9
    node_20 --> node_9
    node_20 --> node_9
    node_20 --> node_12
    node_20 --> node_12
    node_20 --> node_12
    node_22 --> node_15
    node_22 --> node_15
    node_22 --> node_15
    node_22 --> node_15
    node_22 --> node_15
    node_22 --> node_15
    node_22 --> node_19
    node_22 --> node_9
    node_22 --> node_9
    node_22 --> node_9
    node_22 --> node_3
    node_22 --> node_23
    node_22 --> node_3
    node_22 --> node_23
    node_22 --> node_18
    node_22 --> node_10
    node_22 --> node_10
    node_22 --> node_10
    node_22 --> node_15
    node_22 --> node_8
    node_22 --> node_16
    node_22 --> node_21
    node_23 --> node_14
    node_23 --> node_15
    node_23 --> node_10
    node_23 --> node_10
    node_24 --> node_15
    node_24 --> node_15
    node_24 --> node_15
    node_24 --> node_9
    node_24 --> node_9
    node_24 --> node_17
    node_24 --> node_17
    node_24 --> node_10
    node_24 --> node_10
    node_25 --> node_15
    node_25 --> node_15
    node_25 --> node_10
    node_26 --> node_22
    node_27 --> node_9
    node_27 --> node_9
    node_27 --> node_9
    node_27 --> node_9
    node_27 --> node_12
    node_27 --> node_12
    node_27 --> node_12
    node_31 --> node_16
    node_31 --> node_16
    node_31 --> node_16
    node_31 --> node_11
    node_32 --> node_8
    node_33 --> node_9
    node_33 --> node_9
    node_33 --> node_9
    node_33 --> node_9
    node_34 --> node_12
    node_34 --> node_12
    node_34 --> node_12
    node_35 --> node_15
    node_35 --> node_9
    node_35 --> node_9
    node_35 --> node_22
    node_36 --> node_21
    node_36 --> node_21
    node_37 --> node_19
```
