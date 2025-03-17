import torch
import torch.nn as nn
import torch.optim as optim
from settings import MAX_ZOMBIES
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MLPAgent(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)

    def save_model(self, filename="model.pth"):
        torch.save(self.state_dict(), filename)

    def load_model(self, filename="model.pth"):
        if os.path.exists(filename):
            self.load_state_dict(torch.load(filename))
            self.eval()

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

    def predict(self, state):
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)

        action_outputs = self.forward(state_tensor)
        move_x, move_y, angle, shoot = action_outputs[0].cpu().detach()

        move_x = torch.tanh(move_x).item()
        move_y = torch.tanh(move_y).item()
        
        move_x = -1 if move_x < -0.5 else 1 if move_x > 0.5 else 0
        move_y = -1 if move_y < -0.5 else 1 if move_y > 0.5 else 0
        angle = torch.tanh(angle) * 180
        shoot = 1 if shoot > 0.5 else 0

        return [move_x, move_y, angle, shoot]

    def reward(self, state, reward, next_state, gamma=0.99):
        self.optimizer.zero_grad()

        predicted_values = torch.tensor(state, dtype=torch.float32, device=device, requires_grad=True).unsqueeze(0)

        future_values = self.predict(next_state)

        target_values = reward + gamma * max(future_values)
        target_values = torch.tensor(target_values, dtype=torch.float32, device=device)

        loss = self.criterion(predicted_values, target_values)

        loss.backward()
        self.optimizer.step()

        self.save_model()
        
        return loss.item()

Agent = MLPAgent(6 + MAX_ZOMBIES * 2, 4).to(device)
Agent.load_model("model.pth")