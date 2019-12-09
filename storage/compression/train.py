from tqdm import tqdm
import torch
import torch.nn as nn
import torchvision as tv
import torch.optim as optim
import torch.utils.data as utils
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
import torchvision.datasets as dset
from torchvision.utils import save_image
from torch.utils.data import DataLoader
from torch.utils.data import sampler
import torchvision.transforms as transforms
from load_data import load_data
from CAE import CAE

'''
A function that is used to train the model for a specified number of epochs

Inputs : 

    -path : to call the load_data function that returns the dataloader
    -DETRAC : True if being tested on DETRAC ( for development only )
    -train : 
    -epoch : Number of epochs to train for
    -verbose : True if loss is to be displayed at each epoch
    
Outputs : None
'''

def train(path,epoch,verbose=False,DETRAC=False):

    #Dataloading
    train_loader, _ = load_data(path,DETRAC,True)
    images, _ = next(iter(train_loader))  
    
    # Load pre-trained model 
    model_n = CAE()
    model_n.load_state_dict(torch.load("CAE_Full_data.pwf"))
    model_n.cuda()
    
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model_n.parameters(), lr=0.0001)

    #Function that runs one epoch
    def training(model):
        
        model.train()

        for batch_idx, batch in enumerate(tqdm(train_loader)):
            torch.cuda.empty_cache()
            images, targets = batch[0], batch[0]
            images, targets = images.cuda(), targets.cuda()

            output = model(images)

            loss = criterion(output, targets)
            loss = torch.sqrt(loss)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        return loss, model
    
    #Training loop 
    print('\nTraining ..\n')
    for e in range(epoch):
        loss, model = training(model_n)
        torch.save(model.state_dict(), "CAE_Full_data.pwf")
        if verbose : print("\nEpoch : ",epoch+1, " - Loss : ",loss)
