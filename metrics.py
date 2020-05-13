import numpy as np
from abc import abstractmethod
from collections import defaultdict
from scipy import stats


class Metric:

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    @abstractmethod
    def reset_state(self):
        pass

    @abstractmethod
    def update_state(self, *args, **kwargs):
        pass

    @abstractmethod
    def result(self):
        pass
    

class UUAS(Metric):

    def __init__(self):
        self.all_correct = 0
        self.all_predicted = 0
        self.all_gold = 0
        super().__init__()

    def __call__(self, gold, predicted):
        for sent_gold, sent_predicted_relations in zip(gold, predicted):
            self.update_state(sent_gold, sent_predicted_relations)

    def reset_state(self):
        self.all_correct = 0
        self.all_predicted = 0
        self.all_gold = 0

    def update_state(self, sent_gold, sent_predicted):
        
        self.all_gold += len(sent_gold)
        self.all_predicted += len(sent_predicted)
        self.all_correct += len(sent_gold.intersection(sent_predicted))

    def result(self):
        if not self.all_correct:
            return 0.
        return 2. / (self.all_predicted / self.all_correct + self.all_gold / self.all_correct)


class RootAcc(Metric):
    def __init__(self):
        self.all_correct = 0
        self.all_predicted = 0
        super().__init__()

    def __call__(self,gold, predicted):
        for sent_gold, sent_predicted in zip(gold, predicted):
            self.update_state(sent_gold, sent_predicted)

    def reset_state(self):
        self.all_correct = 0
        self.all_predicted = 0

    def update_state(self, sent_gold, sent_predicted):
        if sent_gold == sent_predicted:
            self.all_correct += 1
        self.all_predicted += 1

    def result(self):
        if not self.all_predicted:
            return 0.
        return self.all_correct / self.all_predicted
    
    
class Spearman(Metric):
    
    def __init__(self, min_len=5, max_len=50):
        self.per_sent_len = defaultdict(list)
        self.min_len = min_len
        self.max_len = max_len
        
        super().__init__()

    def __call__(self, gold, predicted):
        for sent_gold, sent_predicted in zip(gold, predicted):
            self.update_state(sent_gold, sent_predicted)
            
    def reset_state(self):
        self.per_sent_len = defaultdict(list)

    def update_state(self, sent_gold, sent_predicted):
        sent_len = sent_gold.shape[0]
        if self.min_len <= sent_len <= self.max_len:
            rho, _ = stats.spearmanr(sent_gold, sent_predicted, axis=None)
            self.per_sent_len[sent_len].append(rho)

    def result(self):
        return {sent_len: np.array(self.per_sent_len[sent_len]).mean() for sent_len in range(self.min_len, self.max_len +1)}

