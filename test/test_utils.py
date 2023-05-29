from unittest import TestCase

from dev_tools import generate_nhs_num
from utils import validate_postcode
from utils import validate_patient_id


class Test(TestCase):
    def test_validate_postcode(self):
        assert validate_postcode("S1 3QX")
        assert validate_postcode("LN20 4JZ")
        assert not validate_postcode("S1 3Q")
        assert not validate_postcode("LN20 4J")

    def test_validate_patient_id(self):
        valid_nums = [
            "3315040893",
            "2119596395",
            "7932861047",
            "8430820655",
            "4742003179",
            "7061756330"
         ]

        for valid_num in valid_nums:
            assert validate_patient_id(valid_num)

        invalid_nums = [
            "1315040893",
            "4119596395",
            "5932861047",
            "6430820655",
            "7742003179",
            "9061756330"
         ]

        for valid_num in invalid_nums:
            assert not validate_patient_id(valid_num)

        # Test NHS Num generator
        for i in range(1000):
            assert validate_patient_id(generate_nhs_num())
