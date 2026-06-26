from asyncio import run
import sys
from codedoctor.cli import initialize_config
from codedoctor.doctor.main import (
    create_graph,
    prepare_graph_input,
    run_graph,
    should_run_graph,
)
from codedoctor.utils import print_to_terminal


def main():
    cfg, user_prompt = initialize_config()
    cfg.subscribe(print_to_terminal)

    should_continue, pre_test_result = run(should_run_graph(cfg))
    if not should_continue:
        sys.exit(0)

    graph = create_graph(cfg)
    graph_input = prepare_graph_input(pre_test_result, user_prompt, cfg)
    run(run_graph(graph, graph_input, cfg))


if __name__ == "__main__":
    main()
