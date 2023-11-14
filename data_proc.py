# -*- coding: UTF-8 -*-
'''
=================================================
@Author : TMG HITSZ
@Date   : 2023/10/28
@Desc   : data processor
=================================================
'''
import json
import os
import params
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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


def check_dirs_files(dirs, files):
    if dirs:
        for dir in dirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
                logging.info(f'create directory: {dir}')
            else:
                logging.info(f'existing dir: {dir}')
    if files:
        for file in files:
            if not os.path.exists(file):
                raise Exception(f'missing file: {file}')
            else:
                logging.info(f'existing file: {file}')


def format_process(task, raw_data):
    result = []
    if task in ['SVAMP', ]:
        for data in raw_data:
            q = data["Body"].strip() + " " + data["Question"].strip()
            a = str(data["Answer"])
            if a[-2:] == ".0":
                a = a[:-2]
            a = delete_extra_zero(a)
            result.append({'question': q, 'answer': a})
    elif task in ['AQuA', ]:
        # MAmmoTH format
        for data in raw_data:
            choice = "(" + "(".join(data["options"])
            choice = choice.replace("(", " (").replace(")", ") ")
            choice = "Answer Choices:" + choice
            question = data["question"].strip() + "\n" + choice + "\n"
            answer = data["correct"]
            result.append({'question': question, 'answer': answer})
    elif task in ['MultiArith', 'AddSub', 'SingleEq']:
        for data in raw_data:
            answer = data['lSolutions'][0]
            question = data['sQuestion']
            result.append({'question': question, 'answer': answer})
    elif task in ['ARC-c', ]:
        for data in raw_data:
            question = data['question']['stem']
            answer = data['answerKey']
            choices = data['question']['choices']
            question = f"{question} \n"
            for t in choices:
                question += f"({t['label']}) {t['text']} \n"
            result.append({'question': question, 'answer': answer})
    elif task in ['Colored_Objects', 'Penguins']:
        for data in raw_data:
            question = data['input'] + '\n'
            answer = data['target'].strip(')').strip('(')
            result.append({'question': question, 'answer': answer})
    elif task in ['StrategyQA', ]:
        for data in raw_data:
            question = data['input']
            answer = None
            for an in data['target_scores'].keys():
                if an not in ['Yes', 'No']:
                    assert Exception('Answer not found')
                if data['target_scores'][an] == 1:
                    answer = an
                    break
            assert answer
            result.append({'question': question, 'answer': answer})
    else:
        raise Exception('failed to process data, unknown task!')

    assert len(result) == len(raw_data)
    return result


def show_data_format(args, raw_data, raw_data_len):
    logging.info(f'{args.task} all examples num: {raw_data_len}')
    data_format = '\n--------------------- data format ---------------------\n'
    for key, value in raw_data[0].items():
        data_format += f'[{key}]: {value}\n'
    data_format += f'-------------------------------------------------------'
    logging.info(data_format)


def process_raw_data(args):

    if args.task in ['GSM8K', 'AQuA', 'ARC-c']:
        with open(args.task_file, encoding="utf-8") as f:
            raw_data = [json.loads(line) for line in f]
    elif args.task in ['SVAMP', 'MultiArith', 'AddSub', 'SingleEq', 'StrategyQA', 'Colored_Objects', 'Penguins']:
        with open(args.task_file, encoding='utf-8') as f:
            raw_data = json.load(f)
        if args.task in ['StrategyQA', 'Colored_Objects', 'Penguins']:
            raw_data = raw_data['examples']
    else:
        raise Exception('failed to read input data, unknown task!')
    raw_data_len = len(raw_data)

    show_data_format(args, raw_data, raw_data_len)

    # format process
    if args.task in ['SVAMP', 'AQuA', 'MultiArith', 'AddSub', 'SingleEq', 'ARC-c', 'StrategyQA', 'Colored_Objects', 'Penguins']:
        raw_data = format_process(args.task, raw_data)

    # select max_example_num
    if len(raw_data) > 200:
        import random
        random.seed(args.random_seed)
        random.shuffle(raw_data)
    if raw_data_len <= args.max_example_num:
        examples = raw_data
        logging.info(f'select all {raw_data_len} examples in {args.task}')
    else:
        examples = raw_data[: args.max_example_num]
        logging.info(f'randomly select {len(examples)} examples in {args.task}')

    # save file
    output_file = os.path.join(args.output_path, f'{args.task}_{len(examples)}.jsonl')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in examples)
    logging.info(f'{args.task} examples save to {output_file}')


def log_param(args):
    args_str = f'\n------------- data processing parameters --------------\n'
    for k, v in args.__dict__.items():
        args_str += f'{k} = {v}\n'
    args_str += f'-------------------------------------------------------'
    logging.info(args_str)


if __name__ == '__main__':
    # 1. args
    args = params.data_args()
    log_param(args)

    # 2. check dir and file
    check_dirs_files(dirs=[args.dataset_dir, args.output_dir, args.output_path], files=[args.task_file, ])

    # 3. process raw data
    process_raw_data(args)

