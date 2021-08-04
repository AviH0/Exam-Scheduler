from dataloader import Dataloader
from solver import Solver


class ExamScheduler:


    def __init__(self, dataloader: Dataloader, solver: Solver):

        self.solver = solver(dataloader, evaluator)