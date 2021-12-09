import torch
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self,X1,X2,Y):
        self.X1 = X1
        self.X2 = X2
        self.Y = Y
    def __len__(self):
        return len(self.X1)
    def __getitem__(self, idx):
        text_data = self.X1[idx]
        meta_data = self.X2[idx]
        label = self.Y[idx]
        return text_data, meta_data, label