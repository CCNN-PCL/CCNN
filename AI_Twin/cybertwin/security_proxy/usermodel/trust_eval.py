# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import torch 
import json
import time
import argparse
import logging


class ZeroTrustModel(torch.nn.Module):

    def predict(self, x):
        output = self(x)
        return output
        
    def save_model(self, model_path):
        torch.save(self.state_dict(), model_path)
        print('Model Saved: {}'.format(model_path))

    def load_model(self, model_path):
        self.load_state_dict(torch.load(model_path, weights_only=True))
        # print('Model loaded: {}'.format(model_path))


class UserTrust(ZeroTrustModel):

    def __init__(self, input_size, output_size):
        super(UserTrust, self).__init__()
        self.fc1 = torch.nn.Linear(input_size, 64)
        self.fc2 = torch.nn.Linear(64, 32)
        self.fc3 = torch.nn.Linear(32, output_size)
        self.relu = torch.nn.ReLU()
        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, x):
        out = self.relu(self.fc1(x))
        out = self.relu(self.fc2(out))
        out = self.fc3(out)
        out = self.sigmoid(out)

        return out


logging.basicConfig(
        filename='./TrustEval.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s'
)

SLEEP_TIME = 0

user_trust_model_config = {
    'model_path': './UserTrustEval.pth',
    'input_size': 7,
    'output_size': 1,
    'active_time_table_path': './Tables/time_active.json',
    'active_location_table_path': './Tables/location_time_active.json'
}

def print_dict(dict_data):
    for key in dict_data:
        print('\t', key, ':', dict_data[key])

def print_bar():
    print('-'*50)

class UserTrustEval:
    def __init__(self, config):
        self.model = UserTrust(config['input_size'], config['output_size'])
        time.sleep(SLEEP_TIME)
        print('Loading Model:', config['model_path'])
        self.model.load_model(config['model_path'])

    def pre_processing(self, input_data):
        common_device = float(input_data[0])
        time_active = input_data[1]
        location_active = input_data[2]
        bio_score = input_data[3]
        pswd = float(input_data[4])
        access_network_score = input_data[5]
        network_risk = input_data[6]
        data_processed = [
            common_device,
            time_active,
            location_active,
            bio_score,
            pswd,
            access_network_score,
            network_risk
        ]

        return [round(i, 2) for i in data_processed]

    def evaluate(self, input_data):
        input_data = self.pre_processing(input_data)
        input_data = torch.tensor(input_data).unsqueeze(0)
        output = self.model(input_data)

        return round(output[0].item(), 2)


def user_trust_eval(data, config):
    # read active table
    time_active_table = json.load(open(config['active_time_table_path']))
    location_active_table = json.load(open(config['active_location_table_path']))

    # query active table
    time = str(data['time'])
    location = data['location']
    data['time'] = time_active_table[time]
    data['location'] = location_active_table[location+'-'+time]

    print('\nUser Attributes Data:')
    print_dict(data)
    input_data = [data[key] for key in data]
    trust_eval = UserTrustEval(config)

    return trust_eval.evaluate(input_data)


def trust_eval(input_data):

    attributes_data = {
        'common_device': input_data['common_device'],
        'time': input_data['time'],
        'location': input_data['location'],
        'bio': input_data['bio'],
        'pswd': input_data['pswd'],
        'access_network_score': input_data['access_network_score'],
        'network_risk': input_data['network_risk'],
    }

    user_trust_score = user_trust_eval(attributes_data, user_trust_model_config)
    print('User Trust Score:', user_trust_score)

    logging.info('Mode: User-CT, CommonDev: %s, Time: %s, Location: %s, Bio: %s, PSWD: %s, AccessNetwork: %s, NetworkRisk: %s, UserTrustScore: %s', attributes_data['common_device'], attributes_data['time'], attributes_data['location'], attributes_data['bio'], attributes_data['pswd'], attributes_data['access_network_score'], attributes_data['network_risk'], user_trust_score)
    
    return user_trust_score


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='User Trust Evaluation')
    parser.add_argument('--input', type=str, help='Path to a JSON File Containing Input Attributes')
    args = parser.parse_args()
    input_data_path = args.input

    # load input json data
    try:
        input_data = json.load(open(input_data_path))
    except:
        raise ValueError('E: Input File Not Found!')
    else:
        print('\nInput Data:')
        print_dict(input_data)
    
    subject_type = input_data['subject_type']

    if subject_type == 'user':
        # Cybertwin <--> User
        res = trust_eval(input_data)
    
    elif subject_type == 'app':
        # Cybertwin <--> App
        pass
        
    else:
        raise ValueError('E: Invalid Subject Type!')
    
    print_bar()
    print('Model Result:', res)
