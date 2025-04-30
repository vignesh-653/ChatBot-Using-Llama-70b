import subprocess
import time

# Common commands for all servers
base_commands = [
    "conda deactivate",
    r"call cb_venv\Scripts\activate",
    "cd agents"
]

# List of servers with different agent names and ports
servers = [
    {"agent": "menu_agent", "port": 8001},
    {"agent": "order_agent", "port": 8002},
    {"agent": " recommendation_agent", "port": 8003},
    {"agent": "chatbot", "port": 8004}
]

processes = []

for server in servers:
    # Construct the full command
    agent_cmd = f'uvicorn {server["agent"]}:app --host 127.0.0.1 --port {server["port"]} --reload'
    
    # Combine all commands into one execution string
    full_command = " && ".join(base_commands + [agent_cmd])
    
    # Open a new terminal and execute the command
    command = f'start cmd /k "{full_command}"'
    process = subprocess.Popen(command, shell=True)
    processes.append(process)
    
    time.sleep(2)  # Give some time for the server to start

print("All API servers started successfully!")





