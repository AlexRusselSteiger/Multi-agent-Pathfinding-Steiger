import subprocess
from argparse import ArgumentParser

def load_instance(input_file):
    global LEN_OF_GRID
    global WIDTH_OF_GRID
    global NR_OF_AGENTS
    global MAKESPAN

    grid = []
    agents_starts = []
    agents_targets = []
