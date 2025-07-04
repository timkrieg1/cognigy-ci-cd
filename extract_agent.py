from helper_files.helper_functions import CognigyAPIClient
from dotenv import load_dotenv
import os

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
    max_snapshots=max_snapshots,
    release_description=release_description
)