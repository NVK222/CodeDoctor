from asyncio import run

from codedoctor.cli import initialize_config
from codedoctor.engineer.main import create_graph, run_graph
from codedoctor.utils import print_to_terminal


def main():
    cfg, user_prompt = initialize_config()
    cfg.subscribe(print_to_terminal)
    graph = create_graph(cfg)
    run(run_graph(graph, user_prompt, cfg))


if __name__ == "__main__":
    main()
