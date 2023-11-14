# -*- coding: UTF-8 -*-
'''
=================================================
@Author : TMG HITSZ
@Date   : 2023/10/28
@Desc   : evaluation
=================================================
'''
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from data_proc import check_dirs_files

import json
import jsonlines
import numpy as np
import re
from tqdm import tqdm

from params import eval_args


def read_json(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_jsonl(input_path):
    output_data = []
    with open(input_path, 'r+', encoding='utf-8') as f:
        for item in jsonlines.Reader(f):
            output_data.append(item)
    return output_data


def delete_extra_zero(n):
    try:
        n = float(n)
    except:
        # logging.warning("Not a float num: {}".format(n))
        return n
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        n = str(n).rstrip('0')
        n = int(n.rstrip('.')) if n.endswith('.') else float(n)
        n = str(n)
        return n


# def solve_math_problems(input_str):
#     pattern = r"\d+\.?\d*"
#
#     matches = re.findall(pattern, input_str)
#     if matches:
#         return matches[-1]
#
#     return None

# def parse_answer(input_str):
#     pattern = r"\{([0-9.,$]*)\}"
#     matches = re.findall(pattern, input_str)
#
#     solution = None
#
#     for match_str in matches[::-1]:
#         solution = re.sub(r"[^0-9.]", "", match_str)
#         if solution:
#             break
#
#     return solution


def parse_gt_answer(input_str, args):
    a = None

    if args.task == 'GSM8K': # GSM8K needs to parse answer
        # MAmmoTH Method
        a = delete_extra_zero(input_str.split("#### ")[-1].replace(",", ""))
    elif args.task in ['SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq', 'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins']: # do not need to parse answer
        a = input_str
    else:
        raise Exception('failed to parse the answer, unknown task!')

    assert a
    return a


def parse_pred_answer(input_str, args):
    solution = None

    if args.task in ['GSM8K', 'SVAMP', 'MultiArith', 'AddSub', 'SingleEq']: # number answer
        # (1) {number}  (2) number
        pattern = r"\{([-0-9.,$]*)\}" # (1) in the form \\boxed{{answer}}
        matches = re.findall(pattern, input_str)
        if not matches: # (2) answer doesn't include {}, directly match the numbers
            matches = re.findall(r'-?\d+(?:\.\d+)?', input_str)

        for match_str in matches[::-1]:
            solution = re.sub(r"[^-0-9.]", "", match_str)
            if solution:
                break
    elif args.task in ['AQuA', 'ARC-c', 'Colored_Objects', 'Penguins']: # multi-choice
        pattern = r'\((\w)\)' # choice (A)
        matches = re.findall(pattern, input_str)

        for match_str in matches[::-1]:
            solution = match_str.upper()
            if solution == 'X':
                continue
            if solution:
                break
    elif args.task in ['StrategyQA', ]: # yes or no
        pattern = r'\b(YES|Yes|yes|NO|No|no)\b'
        matches = re.findall(pattern, input_str)

        for match_str in matches[::-1]:
            if match_str in ['Yes', 'yes', 'YES']:
                solution = 'Yes'
            if match_str in ['No', 'no', 'NO']:
                solution = 'No'
            if solution:
                break
    else:
        raise Exception()

    return solution


def compute_accuracy(gt, pred_solutions, args):
    gt_answer = parse_gt_answer(gt, args)
    if gt_answer is None:
        raise Exception('could not parse ground truth answer!')

    if type(pred_solutions) == list: # multi-agent results
        pred_answers = []
        for pred_solution in pred_solutions:
            pred_answer = parse_pred_answer(pred_solution, args)
            if pred_answer: # valid vote
                pred_answers.append(pred_answer)
            # pred_answers.append(pred_answer)
        pred_answer = most_frequent(pred_answers)
    else: # single agent result
        pred_answer = parse_pred_answer(pred_solutions, args)

    if pred_answer is None: # not valid vote
        return 0

    if args.task in ['GSM8K', 'SVAMP', 'MultiArith', 'AddSub', 'SingleEq']:
        try:
            if float(gt_answer) == float(pred_answer): # number
                return 1
            else:
                return 0
        except:
            # logging.warning(f'could not parse answer string to number! {pred_answer}')
            return 0
    elif args.task in ['AQuA', 'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins']: # multi-choice & yes or no
        if gt_answer == pred_answer:
            return 1
        else:
            return 0
    else:
        raise Exception('failed to parse the answer, unknown task!')


def most_frequent(lst):
    if not lst:
        return None
    counter = 0
    num = lst[0]

    for i in lst:
        current_frequency = lst.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num


def log_param(args):
    args_str = f'\n--------------- evaluation parameters -----------------\n'
    for k, v in args.__dict__.items():
        args_str += f'{k} = {v}\n'
    args_str += f'-------------------------------------------------------'
    logging.info(args_str)


def evaluate_multi_agent(args):

    input_data = read_json(args.eval_file)
    assert len(input_data) == args.example_num

    accuracies = []
    index = 0
    for tmp_data in tqdm(input_data):
        index += 1
        responses = tmp_data['agent_contexts']
        gt = tmp_data['answer']

        pred_solutions = []
        for response in responses:
            pred_solution = response[-1]['content']
            pred_solutions.append(pred_solution)

        accurate = compute_accuracy(gt, pred_solutions, args)
        tmp_data['result'] = accurate
        if accurate:
            accuracies.append(float(accurate))
        else:
            accuracies.append(0.0)

        if index % 100 == 0 or index == args.example_num:
            print(f"{index} accuracy: {np.mean(accuracies) * 100:.4f} %, SEM: {np.std(accuracies) / (len(accuracies) ** 0.5) * 100:.4f} %")


def evaluate_single_agent(args):
    input_data = read_json(args.eval_file)
    assert len(input_data) == args.example_num

    gt_lst, pred_solutions_lst = [], []
    for tmp_data in tqdm(input_data):
        responses = tmp_data['agent_contexts']
        gt = tmp_data['answer']
        gt_lst.append(gt)
        pred_solutions = []
        for response in responses:
            pred_solution = response[-1]['content']
            pred_solutions.append(pred_solution)
        pred_solutions_lst.append(pred_solutions)

    single_agent_num = len(pred_solutions_lst[0])
    multi_agent_result = [{} for i in range(single_agent_num)]
    for agent_num in range(single_agent_num):
        print(f'-------------------------- agent {agent_num} -----------------------------')
        accuracies = []
        agent_pred_solutions = [item[agent_num] for item in pred_solutions_lst]
        index = 0
        for gt, pred_solution in zip(gt_lst, agent_pred_solutions):
            index += 1
            accurate = compute_accuracy(gt, pred_solution, args)
            if accurate:
                accuracies.append(float(accurate))
            else:
                accuracies.append(0.0)

            if index % 100 == 0 or index == args.example_num:
                acc, sem = np.mean(accuracies) * 100, np.std(accuracies) / (len(accuracies) ** 0.5) * 100
                print(f"{index} accuracy: {acc:.4f} %, SEM: {sem:.4f} %")
                multi_agent_result[agent_num][index] = (acc, sem)

    print(f'----------------------- mean multi-agent -----------------------')
    for key in multi_agent_result[0]:
        mean_acc = sum([multi_agent_result[i][key][0] for i in range(single_agent_num)]) / single_agent_num
        mean_sem = sum([multi_agent_result[i][key][1] for i in range(single_agent_num)]) / single_agent_num
        print(f"{key} accuracy: {mean_acc:.4f} %, SEM: {mean_sem:.4f} %")



if __name__ == "__main__":
    # 1. args
    args = eval_args()
    log_param(args)

    # 2. check dir and file
    check_dirs_files(dirs=[args.eval_dir, ], files=[args.eval_file, ])

    # 3. evaluation
    if args.method in ['single_agent', 'self_correction']:
        evaluate_single_agent(args)
    else:
        evaluate_multi_agent(args)