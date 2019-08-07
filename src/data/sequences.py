#!/usr/bin/env python
# coding: utf-8
import json
import logging
import pickle
import sys
from pathlib import Path

import click
import numpy as np
from sklearn.model_selection import train_test_split

sys.path.append("./")
from src.models.utils import concatenate_texts


DATA_PATH = "data/processed/"


@click.command()
@click.option("--settings", default="settings.json")
def main(settings):

    logger = logging.getLogger(__name__)

    # load settings
    settings_path = Path("settings/" + settings)
    with open(str(settings_path), "r") as file:
        settings_dict = json.load(file)

    logger.info(
        f"Generating sequence data for math module: {settings_dict['math_module']} and difficulty level: {settings_dict['train_level']}"
    )

    # define file paths
    raw_path = Path(settings_dict["data_path"])
    interpolate_path = raw_path / "interpolate"
    extrapolate_path = raw_path / "extrapolate"

    # configure module and train level
    math_module = settings_dict["math_module"]
    train_level = settings_dict["train_level"]

    datasets = {
        "train": (raw_path, "train-" + train_level + "/" + math_module),
        "interpolate": (interpolate_path, math_module),
        "extrapolate": (extrapolate_path, math_module),
    }

    # load raw data and split into input (questions) and target (answers)
    input_texts = {}
    target_texts = {}

    for k, v in datasets.items():
        input_texts[k], target_texts[k] = concatenate_texts(v[0], v[1])
        logger.info(f"Length of {k} set is {len(input_texts[k])} questions")

    random_idx = np.random.randint(1, len(input_texts["train"]))
    logger.info(f"Sample input: {input_texts['train'][random_idx]}")
    logger.info(f"Sample output: {target_texts['train'][random_idx].strip()}")

    # flatten
    all_input_texts = sum(input_texts.values(), [])
    all_target_texts = sum(target_texts.values(), [])

    input_characters = set("".join(all_input_texts))
    target_characters = set("".join(all_target_texts))

    input_characters = sorted(list(input_characters))
    target_characters = sorted(list(target_characters))
    num_encoder_tokens = len(input_characters)
    num_decoder_tokens = len(target_characters)
    max_encoder_seq_length = max([len(txt) for txt in all_input_texts])
    max_decoder_seq_length = max([len(txt) for txt in all_target_texts])

    logger.info(f"Number of unique input tokens: {num_encoder_tokens}")
    logger.info(f"Number of unique output tokens: {num_decoder_tokens}")
    logger.info(f"Max sequence length for inputs: {max_encoder_seq_length}")
    logger.info(f"Max sequence length for outputs: {max_decoder_seq_length}")

    input_texts_train, input_texts_valid, target_texts_train, target_texts_valid = train_test_split(
        input_texts["train"], target_texts["train"], test_size=0.2, random_state=42
    )

    logger.info(f"Number of training samples: {len(input_texts_train)}")

    logger.info(f"Number of validation samples: {len(input_texts_valid)}")

    # create a mapping from unique characters to indices
    input_token_index = dict([(char, i) for i, char in enumerate(input_characters)])
    target_token_index = dict([(char, i) for i, char in enumerate(target_characters)])

    sequence_data = {
        "input_token_index": input_token_index,
        "target_token_index": target_token_index,
        "input_texts": input_texts,
        "target_texts": target_texts,
        "max_encoder_seq_length": max_encoder_seq_length,
        "max_decoder_seq_length": max_decoder_seq_length,
        "num_encoder_tokens": num_encoder_tokens,
        "num_decoder_tokens": num_decoder_tokens,
        "input_token_index": input_token_index,
        "target_token_index": target_token_index,
        "num_thinking_steps": settings_dict["thinking_steps"],
    }

    # write sequence data to disk
    FILE_NAME = settings_dict["math_module"] + "-" + settings_dict["train_level"]

    with open(f"{DATA_PATH}{FILE_NAME}.pkl", "wb") as file:
        pickle.dump(sequence_data, file)

    with open(f"{DATA_PATH}{FILE_NAME}.pkl", "rb") as file:
        foo = pickle.load(file)

    print(foo["input_texts"]["train"][0])
    print(foo["input_token_index"])


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
