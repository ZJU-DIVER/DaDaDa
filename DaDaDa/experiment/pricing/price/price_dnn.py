import argparse
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

class PricePredictionDataset(Dataset):
    def __init__(self, features, target):
        self.features = features
        self.target = target

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        X = torch.tensor(self.features[idx], dtype=torch.float32)
        y = torch.tensor(self.target[idx], dtype=torch.float32)
        return X, y

class DNNModel(nn.Module):
    def __init__(self, input_dim):
        super(DNNModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 256)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.1)

        self.fc2 = nn.Linear(256, 128)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.1)

        self.fc3 = nn.Linear(128, 64)
        self.relu3 = nn.ReLU()
        self.dropout3 = nn.Dropout(0.1)

        self.fc4 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)

        x = self.fc3(x)
        x = self.relu3(x)
        x = self.dropout3(x)

        x = self.fc4(x)
        return x
def train(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    for features, target in dataloader:
        features, target = features.to(device), target.to(device)

        outputs = model(features)
        loss = criterion(outputs.squeeze(), target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    return running_loss / len(dataloader)

def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for features, target in dataloader:
            features, target = features.to(device), target.to(device)
            outputs = model(features)
            loss = criterion(outputs.squeeze(), target)
            running_loss += loss.item()

            all_preds.extend(outputs.cpu().numpy())
            all_targets.extend(target.cpu().numpy())

    avg_loss = running_loss / len(dataloader)
    mae = mean_absolute_error(all_targets, all_preds)
    mse = mean_squared_error(all_targets, all_preds)
    rmse = np.sqrt(mse)
    r2 = r2_score(all_targets, all_preds)
    # compute the std
    std = np.std(np.array(all_targets) - np.array(all_preds))

    return avg_loss, mae, mse, rmse, r2, std

def get_file_path_and_save_path(file_choice):
    if file_choice == 'price_12':
        return '../price_12.csv', 'saved_models_12'
    elif file_choice == 'price_24':
        return '../price_24.csv', 'saved_models_24'
    else:
        raise ValueError(f"Unknown file choice: {file_choice}")

if __name__ == '__main__':
    seed = 42
    parser = argparse.ArgumentParser(description="Choose a file to read.")
    parser.add_argument('--file', type=str, required=True, choices=['price_12', 'price_24'],
                        help="File choice: 'price_12' or 'price_24'")
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'test'],
                        help="Mode choice: 'train' or 'test'")


    args = parser.parse_args()

    mode = args.mode
    file_path, save_path = get_file_path_and_save_path(args.version)

    df = pd.read_csv(file_path)
    target = 'price_log'
    features = [col for col in df.columns if col != target]

    X = df[features].values
    y = df[target].values


    # create dataset
    dataset = PricePredictionDataset(X, y)

    # split the dataset
    train_size = int(0.6 * len(dataset))
    test_and_val_size = len(dataset) - train_size
    train_dataset, test_and_val_dataset = random_split(dataset, [train_size, test_and_val_size], generator=torch.Generator().manual_seed(seed))

    test_size = test_and_val_size // 2
    test_dataset, val_dataset = random_split(test_and_val_dataset, [test_size, test_and_val_size-test_size], generator=torch.Generator().manual_seed(seed))

    # create DataLoader
    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    if mode == 'train':
        model = DNNModel(input_dim=X.shape[1])

        # define loss function and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        num_epochs = 500

        for epoch in range(num_epochs):
            train_loss = train(model, train_loader, criterion, optimizer, device)
            val_metrics = validate(model, val_loader, criterion, device)
            val_loss, mae, mse, rmse, r2, std = val_metrics
            print(f"Epoch {epoch + 1}/{num_epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                  f"MAE: {mae:.4f}, MSE: {mse:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}, std: {std:.4f}")

        # test the final model
        final_metrics = validate(model, test_loader, criterion, device)
        final_loss, mae, mse, rmse, r2, std = final_metrics
        print(f"Final Test Loss: {final_loss:.4f}, MAE: {mae:.4f}, MSE: {mse:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}, std: {std:.4f}")

        # save the model
        torch.save(model.state_dict(), f"{save_path}/dnn_model_{num_epochs}.pth")
    else:
        # load the model
        model = DNNModel(input_dim=X.shape[1])
        num_epochs = 500
        model.load_state_dict(torch.load(f"{save_path}/dnn_model_{num_epochs}.pth"))
        model.eval()
        criterion = nn.MSELoss()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        final_metrics = validate(model, test_loader, criterion, device)
        final_loss, mae, mse, rmse, r2, std = final_metrics
        print(f"Final Test Loss: {final_loss:.4f}, MAE: {mae:.4f}, MSE: {mse:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}, std: {std:.4f}")
