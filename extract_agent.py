from helper_files.helper_functions import CognigyAPIClient
from dotenv import load_dotenv
import os

#Cehck for arguments
#Todo: Implement argument parsing to allow for different environments (dev/prod) and other configurations
#For Testing:
project_id_dev = "6853e4773ea509ac11dc4444"
project_id_dev = "68499f9e62b02399a43dacb3"
bot_name = "Intelligent Routing"

#Load environment variables
load_dotenv(override=True)
base_url_dev = os.getenv("cognigy_base_url_dev")
base_url_prod = os.getenv("cognigy_base_url_prod")
api_key_dev = os.getenv("cognigy_api_key_dev")
api_key_prod = os.getenv("cognigy_api_key_prod")

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

CognigyAPIClientDev.download_snapshot(
    max_snapshots=10,
    release_description="Test Release"
)