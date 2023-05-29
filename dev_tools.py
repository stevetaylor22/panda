from random import randint, seed
from typing import Set
from typing import Tuple
import json

# Initialise pseudo-random number gen
seed()

################################
# Utils to analyse example data
################################


def enum_json_field(json_file_path: str, field_name: str) -> Set[str]:
    ret: Set[str] = set()

    with open(json_file_path, "r") as json_file:
        contents = json.load(json_file)
        for jDict in contents:
            ret.add(jDict[field_name])

    return ret


def generate_nhs_num() -> str:
    nhs_num = ""
    acc = 0
    attempts = 100     # safety net, chances of 100 fails very remote
    csum = 0
    while attempts > 0:
        for idx in range(9):
            next_digit = randint(0, 9)
            acc += next_digit * (10 - idx)
            nhs_num += str(next_digit)
        chk_digit = 11 - acc % 11
        csum = 0 if chk_digit == 11 else chk_digit
        if csum < 10:
            break
        nhs_num = ""
        acc = 0
        attempts -= 1

    return nhs_num + str(csum)


def generate_test_nhs_num(**kwargs) -> Tuple[dict, int]:
    """
    Function to generate HNS numbers to make testing of FE
    a bit easier
    :param kwargs: - unused
    :return: Tuple of: dict containing NHS number, response code
    """
    return {"nhs_number": generate_nhs_num()}, 200


if __name__ == "__main__":

    print(generate_nhs_num())
