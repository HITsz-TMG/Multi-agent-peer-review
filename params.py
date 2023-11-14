# -*- coding: UTF-8 -*-
'''
=================================================
@Author : TMG HITSZ
@Date   : 2023/10/28
@Desc   : parameters
=================================================
'''
import argparse
import os
from datetime import datetime

TASK_FILE = {
    'GSM8K': 'GSM8K.jsonl',         # 1319      https://github.com/openai/grade-school-math/blob/master/grade_school_math/data/test.jsonl
    'SVAMP': 'SVAMP.json',          # 1000      https://github.com/arkilpatel/SVAMP/blob/main/SVAMP.json
    'AQuA': 'AQuA.json',            # 254       https://github.com/google-deepmind/AQuA/blob/master/test.json    rename as AQuA.json
    'MultiArith': 'MultiArith.json',# 600       https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting/blob/main/dataset/MultiArith/MultiArith.json
    'AddSub': 'AddSub.json',        # 395       https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting/blob/main/dataset/AddSub/AddSub.json
    'SingleEq': 'SingleEq.json',    # 508       https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting/blob/main/dataset/SingleEq/SingleEq.json
    'ARC-c': 'ARC-c.jsonl',         # 1172      https://ai2-public-datasets.s3.amazonaws.com/arc/ARC-V1-Feb2018.zip   ARC-V1-Feb2018-2\ARC-Challenge\ARC-Challenge-Test.jsonl
    'StrategyQA': 'StrategyQA.json',# 2290      https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting/blob/main/dataset/StrategyQA/StrategyQA.json
    'Colored_Objects': 'Colored_Objects.json',  # 250     https://github.com/suzgunmirac/BIG-Bench-Hard/blob/main/bbh/reasoning_about_colored_objects.json
    'Penguins': 'Penguins.json',    # 146       https://github.com/suzgunmirac/BIG-Bench-Hard/blob/main/bbh/penguins_in_a_table.json
}

EXAMPLE_NUM = {
    'GSM8K': 500,
    'SVAMP': 500,
    'AQuA':  254,
    'MultiArith': 500,
    'AddSub': 395,
    'SingleEq': 500,
    'ARC-c': 500,
    'StrategyQA': 500,
    'Colored_Objects': 250,
    'Penguins': 146,
}


def data_args():
    args_parser = argparse.ArgumentParser(description='process_data')

    # dictionary or file
    args_parser.add_argument('--dataset_dir', type=str, default='datasets')
    args_parser.add_argument('--output_dir', type=str, default='processed_data')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--max_example_num', type=int, default=500)
    args_parser.add_argument('--random_seed', type=int, default=42)

    # parse
    args = args_parser.parse_args()
    args.task_file = os.path.join(os.path.join(args.dataset_dir, args.task), TASK_FILE[args.task])
    args.output_path = os.path.join(args.output_dir, args.task)
    return args


def single_agent_args():
    args_parser = argparse.ArgumentParser(description='single_agent')

    # dictionary or file
    args_parser.add_argument('--dataset_dir', type=str, default='processed_data')
    args_parser.add_argument('--output_dir', type=str, default='result')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--max_example_num', type=int, default=500) # AQuA: 254  AddSub: 395  Colored_Objects:250 Penguins: 146
    args_parser.add_argument('--openai_key', type=str, default='')
    args_parser.add_argument('--openai_organization', type=str, default='')

    # agent
    args_parser.add_argument('--agent_num', type=int, default=3) # single agent answer question for 3 times

    # reload data
    args_parser.add_argument('--reload_data', type=bool, default=False)

    # parse
    args = args_parser.parse_args()

    time = datetime.now().strftime("%m%d")
    args.task_file = os.path.join(os.path.join(args.dataset_dir, args.task), f'{args.task}_{args.max_example_num}.jsonl')
    args.output_file = os.path.join(os.path.join(args.output_dir, args.task), f'{args.task}_single_agent_{args.max_example_num}_{time}.json')

    return args


def self_correction():
    args_parser = argparse.ArgumentParser(description='self-correction')

    # dictionary or file
    args_parser.add_argument('--dataset_dir', type=str, default='processed_data')
    args_parser.add_argument('--output_dir', type=str, default='result')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--max_example_num', type=int, default=500) # AQuA: 254  AddSub: 395  Colored_Objects:250   Penguins 146
    args_parser.add_argument('--openai_key', type=str, default='')
    args_parser.add_argument('--openai_organization', type=str, default='')

    # agent
    args_parser.add_argument('--agent_num', type=int, default=3) # single agent answer question for 3 times

    # reload data
    args_parser.add_argument('--reload_data', type=bool, default=False)

    # parse
    args = args_parser.parse_args()

    time = datetime.now().strftime("%m%d")
    args.task_file = os.path.join(os.path.join(args.dataset_dir, args.task), f'{args.task}_{args.max_example_num}.jsonl')
    args.output_file = os.path.join(os.path.join(args.output_dir, args.task), f'{args.task}_self_correction_{args.max_example_num}_{time}.json')

    return args


def debate_args():
    args_parser = argparse.ArgumentParser(description='debate')

    # dictionary or file
    args_parser.add_argument('--dataset_dir', type=str, default='processed_data')
    args_parser.add_argument('--output_dir', type=str, default='result')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--max_example_num', type=int, default=500) # AQuA: 254  AddSub: 395  Colored_Objects:250
    args_parser.add_argument('--openai_key', type=str, default='')
    args_parser.add_argument('--openai_organization', type=str, default='')

    # agent
    args_parser.add_argument('--agent_num', type=int, default=3)
    args_parser.add_argument('--rounds', type=int, default=2)

    # reload data
    args_parser.add_argument('--reload_data', type=bool, default=False)

    # parse
    args = args_parser.parse_args()

    time = datetime.now().strftime("%m%d")
    args.task_file = os.path.join(os.path.join(args.dataset_dir, args.task), f'{args.task}_{args.max_example_num}.jsonl')
    args.output_file = os.path.join(os.path.join(args.output_dir, args.task), f'{args.task}_debate_{args.max_example_num}_{time}.json')

    return args


def feedback_args():
    args_parser = argparse.ArgumentParser(description='feedback')

    # dictionary or file
    args_parser.add_argument('--dataset_dir', type=str, default='processed_data')
    args_parser.add_argument('--output_dir', type=str, default='result')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--max_example_num', type=int, default=500) # AQuA: 254  AddSub: 395  Colored_Objects:250
    args_parser.add_argument('--openai_key', type=str, default='')
    args_parser.add_argument('--openai_organization', type=str, default='')

    # agent
    args_parser.add_argument('--agent_num', type=int, default=3)
    args_parser.add_argument('--rounds', type=int, default=3) # fix rounds = 3

    # reload data
    args_parser.add_argument('--reload_data', type=bool, default=False)

    # parse
    args = args_parser.parse_args()

    time = datetime.now().strftime("%m%d")
    args.task_file = os.path.join(os.path.join(args.dataset_dir, args.task), f'{args.task}_{args.max_example_num}.jsonl')
    args.output_file = os.path.join(os.path.join(args.output_dir, args.task), f'{args.task}_feedback_{args.max_example_num}_{time}.json')

    return args


def peer_review_args():
    args_parser = argparse.ArgumentParser(description='peer_review')

    # dictionary or file
    args_parser.add_argument('--dataset_dir', type=str, default='processed_data')
    args_parser.add_argument('--output_dir', type=str, default='result')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--max_example_num', type=int, default=500) # AQuA: 254  AddSub: 395  Colored_Objects:250
    args_parser.add_argument('--openai_key', type=str, default='')
    args_parser.add_argument('--openai_organization', type=str, default='')

    # agent
    args_parser.add_argument('--agent_num', type=int, default=3)
    args_parser.add_argument('--rounds', type=int, default=3) # fix rounds = 3

    # reload data
    args_parser.add_argument('--reload_data', type=bool, default=False)

    # parse
    args = args_parser.parse_args()

    time = datetime.now().strftime("%m%d")
    args.task_file = os.path.join(os.path.join(args.dataset_dir, args.task), f'{args.task}_{args.max_example_num}.jsonl')
    args.output_file = os.path.join(os.path.join(args.output_dir, args.task), f'{args.task}_peer_review_{args.max_example_num}_{time}.json')

    return args


def eval_args():
    args_parser = argparse.ArgumentParser(description='evaluation')

    # dictionary or file
    args_parser.add_argument('--eval_dir', type=str, default='result')

    args_parser.add_argument('--task', type=str, default='GSM8K',
                             choices=['GSM8K', 'SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq',
                                      'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins'])
    args_parser.add_argument('--method', type=str, default='peer_review',
                             choices=['single_agent', 'self_correction', 'majority', 'debate', 'feedback', 'peer_review'])
    args_parser.add_argument('--time_flag', type=str, default='1113')

    # parse
    args = args_parser.parse_args()
    args.example_num = EXAMPLE_NUM[args.task]
    if args.method in ['majority', 'single_agent']:
        args.eval_file = os.path.join(os.path.join(args.eval_dir, args.task),
                                      f'{args.task}_single_agent_{args.example_num}_{args.time_flag}.json')
    else:
        args.eval_file = os.path.join(os.path.join(args.eval_dir, args.task),
                                      f'{args.task}_{args.method}_{args.example_num}_{args.time_flag}.json')

    return args