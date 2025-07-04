from helper_files.helper_functions import CognigyAPIClient
from dotenv import load_dotenv
import os
import sys
import shutil
import subprocess
from datetime import datetime, timezone

#Load environment variables
load_dotenv(override=True)
base_url_dev = os.getenv("COGNIGY_BASE_URL_DEV")
base_url_prod = os.getenv("COGNIGY_BASE_URL_PROD")
api_key_dev = os.getenv("COGNIGY_API_KEY_DEV")
api_key_prod = os.getenv("COGNIGY_API_KEY_PROD")
bot_name = os.getenv("USE_CASE")
project_id_dev = os.getenv("COGNIGY_PROJECT_ID_DEV")
project_id_prod = os.getenv("COGNIGY_PROJECT_ID_PROD")
max_snapshots = int(os.getenv("MAX_SNAPSHOTS"))
release_description = os.getenv("RELEASE_DESCRIPTION")

# --- Use bot_name for all use-case logic ---
if not bot_name:
    bot_name = "agent"

# --- Prepare agent folder structure ---
agent_folder = "agent"
if os.path.exists(agent_folder):
    shutil.rmtree(agent_folder)
os.makedirs("agent/flows", exist_ok=True)
os.makedirs("agent/connections", exist_ok=True)
os.makedirs("agent/snapshots", exist_ok=True)

#Instantiate Cognigy Dev Client
CognigyAPIClientDev = CognigyAPIClient(
    base_url=base_url_dev,
    api_key=api_key_dev,
    project_id=project_id_dev,
    bot_name=bot_name
)

#Start fetching data for package creation
flow_ids = CognigyAPIClientDev.get_flow_ids()
lexicon_ids = CognigyAPIClientDev.get_lexicon_ids()
connection_ids = CognigyAPIClientDev.get_connection_ids()
nlu_connector_ids = CognigyAPIClientDev.get_nluconnector_ids()
connection_details = CognigyAPIClientDev.get_connection_ids()
ai_agents = CognigyAPIClientDev.get_aiagent_ids()
large_language_models = CognigyAPIClientDev.get_largelanguagemodel_ids()
knowledge_stores = CognigyAPIClientDev.get_knowledgestore_ids()
functions = CognigyAPIClientDev.get_function_ids()

#Combine to package ressource list
package_ressource_ids = [
    *flow_ids,
    *lexicon_ids,
    *connection_ids,
    *nlu_connector_ids,
    *connection_details,
    *ai_agents,
    *large_language_models,
    *knowledge_stores
]

#Create package
CognigyAPIClientDev.create_package(
    resource_ids=package_ressource_ids
)

CognigyAPIClientDev.download_package()

snapshot_name = CognigyAPIClientDev.download_snapshot(
    max_snapshots=max_snapshots,
    release_description=release_description
)

# --- Git branch creation and commit logic ---
branch_name = snapshot_name

# Git config
subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)

# Ensure we are on main and up to date
subprocess.run(["git", "checkout", "main"], check=True)
subprocess.run(["git", "pull", "origin", "main"], check=True)

# Create new branch from main
subprocess.run(["git", "checkout", "-b", branch_name], check=True)

# Stage and commit new agent export
subprocess.run(["git", "add", agent_folder], check=True)
subprocess.run(["git", "commit", "-m", f"Update agent export for {bot_name}"], check=True)

# Push the new branch
subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)