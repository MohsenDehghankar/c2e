from typing import List

"""
Use this class to implement all the methods.
A 'method' is a method(!) for solving the claim verification task.
"""


class BaseMethod:
    def __init__(self, config):
        self.config = config

    def setup(self):
        raise NotImplementedError("Subclasses must implement this method")

    def validate_claims(self, claims: List[str]):
        """
        This is the main function to call when you want to validate a claim with this method.

        Args:
            claims (List[str]): A list of claims to validate.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError("Subclasses must implement this method")

    def evaluate_method(self, claims: List[str], ground_truth: List[str]):
        """
        Evaluate the whole method by running on a dataset and reporting some metrics

        Args:
            claims (List[str]): List of claims to validate
            ground_truth (List[str]): List of ground truth values for the claims

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        # TODO: not sure what ground_truth should look like here
        raise NotImplementedError("Subclasses must implement this method")
