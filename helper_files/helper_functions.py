import requests
import json
import os
import dotenv
from typing import List
import re
from datetime import datetime
import time

def clean_base_url(base_url: str) -> str:
    """
    Cleans the base URL by removing trailing slashes.
    """
    return re.sub(r'/new/?$|/$', '', base_url.strip())

class CognigyAPIClient:

    """A client for interacting with the Cognigy API.
    Attributes:
        base_url (str): The base URL for the Cognigy API.
        api_key (dict): The API key for authentication.
        project_id (str): The ID of the Cognigy project.
        bot_name (str): The name of the bot.
    
    Returns:
        Instance of CognigyAPIClient
    
    Methods:
        get(endpoint: str, params: dict = None) -> List[dict]:
            Sends a GET request to the specified endpoint with optional parameters.
        post(endpoint: str, data: dict = None) -> List[dict]:
            Sends a POST request to the specified endpoint with optional data.
    """

    def __init__(self, base_url: str = None, api_key: dict = None, project_id: str = None, bot_name: str = None):
        if (not base_url or not api_key or not project_id or not bot_name):
            raise ValueError("Cannot instantiate Congigy API Client. Base URL, API Key, and Project ID and Bot Name must be provided.")
        
        self.base_url = f"{clean_base_url(base_url)}/new/v2.0"
        self.api_key = api_key
        self.project_id = project_id
        self.bot_name = bot_name
        self.package_name = ""
        self.snapshot_name = ""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": self.api_key,
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.params = {
            "limit": 100,
            "projectId": self.project_id
        }

    def get(self, endpoint: str) -> List[dict]:
        url = f"{self.base_url}/{endpoint}"
        next_cursor = None
        current_params = self.params.copy()
        all_items = []

        while True:
            if next_cursor:
                current_params["next"] = next_cursor

            #Fetch data from the API
            response = self.session.get(url = url, params=current_params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            
            items = data.get("items", [])
            all_items.extend(items)
            total = data.get("total", 0)
            next_cursor = data.get("nextCursor")

            #End the loop when 
            if not next_cursor or len(items) >= total:
                break

        return all_items
        
    def get_flow_ids(self) -> List[dict]:
        """
        Fetches all flows from the Cognigy API.
        """
        flow_ids = []
        flows = self.get("flows")

        for flow in flows:
            flow_ids.append(flow["_id"])
        
        return flow_ids

    
    def get_lexicon_ids(self) -> List[dict]:
        """
        Fetches all lexicons from the Cognigy API.
        """
        lexcion_ids = []
        lexcions = self.get("lexicons")

        for lexcion in lexcions:
            lexcion_ids.extend(lexcion["_id"])
        
        return lexcion_ids
    
    def get_nluconnector_ids(self) -> List[dict]:
        """
        Fetches all NLU connectors from the Cognigy API.
        """
        nluconnector_ids = []
        nluconnectors = self.get("nluconnectors")

        for nluconnector in nluconnectors:
            nluconnector_ids.append(nluconnector["_id"])

        return nluconnector_ids

    def get_connection_ids(self) -> List[dict]:
        """
        Fetches all connections from the Cognigy API.
        """
        connection_ids = []
        connections = self.get("connections")

        for connection in connections:
            connection_ids.append(connection["_id"])

        return connection_ids

    def get_aiagent_ids(self) -> List[dict]:
        """
        Fetches all AI agents from the Cognigy API.
        """
        aiagent_ids = []
        aiagents = self.get("aiagents")

        for aiagent in aiagents:
            aiagent_ids.append(aiagent["_id"])

        return aiagent_ids

    def get_largelanguagemodel_ids(self) -> List[dict]:
        """
        Fetches all large language models from the Cognigy API.
        """
        llm_ids = []
        llms = self.get("largelanguagemodels")

        for llm in llms:
            llm_ids.append(llm["_id"])

        return llm_ids

    def get_knowledgestore_ids(self) -> List[dict]:
        """
        Fetches all knowledge stores from the Cognigy API.
        """
        knowledgestore_ids = []
        knowledgestores = self.get("knowledgestores")

        for knowledgestore in knowledgestores:
            knowledgestore_ids.append(knowledgestore["_id"])

        return knowledgestore_ids

    def get_function_ids(self) -> List[dict]:
        """
        Fetches all functions from the Cognigy API.
        """
        function_ids = []
        functions = self.get("functions")

        for function in functions:
            function_ids.append(function["_id"])

        return function_ids
    
    def create_package(self, resource_ids: List[str]) -> dict:
        """
        Creates a new package with the specified resources.
        """
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.package_name = f"Cognigy-CI-CD-Package_{self.bot_name}_{now}"
        payload = {
            "name": self.package_name,
            "description": "Automated package creation by CI/CD pipeline",
            "resourceIds": resource_ids,
            "projectId": self.project_id
        }

        response = self.session.post(f"{self.base_url}/packages", json=payload)
        response.raise_for_status()
        return response.json
    
    def download_package(self) -> dict:
        """
        Downloads the package created by the CI/CD pipeline.
        """
        #Fetch the latest package to get the package ID
        params = {
            "limit": 1,
            "projectId": self.project_id
        }
        package_id = ""
        while True:
            response = self.session.get(
                url=f"{self.base_url}/packages",
                params=params
            )

            response.raise_for_status()
            data = response.json().get("items", [])
            package_name = data[0].get("name", "") if len(data) > 0 else ""

            if package_name == self.package_name:
                package_id = data[0]["_id"]
                break
        
        prev_size = 0
        while True:
            # Create download link
            response = self.session.post(
            url=f"{self.base_url}/packages/{package_id}/downloadLink",
            json={
                "packageId": package_id
            }
            )

            response.raise_for_status()
            download_link = response.json().get("downloadLink", "")
            print(download_link)
            # Download the file
            target_dir = os.path.join("agent", "package")
            os.makedirs(target_dir, exist_ok=True)
            package_path = os.path.join(target_dir, f"{self.package_name}.zip")
            with self.session.get(download_link, stream=True) as r:
                r.raise_for_status()
                with open(package_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            curr_size = os.path.getsize(package_path) / 1000
            print(f"Downloaded zip size: {curr_size} kilobytes")
            if curr_size == 0:
                print("Downloaded zip is empty, retrying in 5 seconds...")
                time.sleep(5)
                continue

            if prev_size == 0:
            # First non-empty download, check again
                prev_size = curr_size
                print("Zip file is not empty, checking again in 5 seconds to validate full package...")
                time.sleep(5)
                continue

            if curr_size != prev_size:
            # Size changed, possible background loading
                prev_size = curr_size
                print("Zip file size changed, checking again in 5 seconds...")
                time.sleep(5)
                continue

            print("Finished package download")
            break
            
    def download_snapshot(self, max_snapshots: int, release_description: str) -> None:
        """
        Prepares the snapshot for download.
        """
        print("Preparing snapshot for download...")
        # First check if the max amount of snapshots is reached
        response = self.session.get(url=f"{self.base_url}/snapshots", params=self.params)
        response.raise_for_status()
        snapshots = response.json().get("items", [])
        print(f"Current number of snapshots: {len(snapshots)}")
        print(f"Max allowed snapshots: {max_snapshots}")

        if len(snapshots) >= int(max_snapshots):
            # Delete the oldest snapshot
            oldest_snapshot = snapshots[-1]
            snapshot_id = oldest_snapshot["_id"]
            self.session.delete(url=f"{self.base_url}/snapshots/{snapshot_id}")
            response.raise_for_status()
            # Poll until the number of snapshots is less than max_snapshots
            while True:
                poll_response = self.session.get(url=f"{self.base_url}/snapshots", params=self.params)
                poll_response.raise_for_status()
                poll_snapshots = poll_response.json().get("items", [])
                if len(poll_snapshots) < int(max_snapshots):
                    break
                    time.sleep(2)
            print(f"Deleted oldest snapshot: {snapshot_id}")


        # Determine the new snapshot name
        today_str = datetime.now().strftime("%d_%m_%Y")
        base_snapshot_name = f"{self.bot_name}_{today_str}"
        new_snapshot_name = ""
        existing_names = [s["name"] for s in snapshots if s["name"].startswith(base_snapshot_name)]
        if not existing_names:
            new_snapshot_name = base_snapshot_name
        else:
            # Find the next available suffix
            suffix = 1
            while f"{base_snapshot_name}_{suffix}" in existing_names:
                suffix += 1
            new_snapshot_name = f"{base_snapshot_name}_{suffix}"
        
        self.snapshot_name = new_snapshot_name
        # Create a new snapshot
        response = self.session.post(
            url=f"{self.base_url}/snapshots",
            json={
                "name": self.snapshot_name,
                "description": release_description,
                "projectId": self.project_id
            }
        )
        response.raise_for_status()
        print("Created task to create new snapshot")
        print("Polling for snapshot to be created...")

        #Get all snapshots again to get snapshot id
        snapshot_id = None
        while snapshot_id is None:
            response = self.session.get(url=f"{self.base_url}/snapshots", params=self.params)
            response.raise_for_status()
            snapshots = response.json().get("items", [])
            snapshot_id = next((snapshot["_id"] for snapshot in snapshots if snapshot["name"] == self.snapshot_name), None)
            if snapshot_id is None:
                print("Snapshot not found, retrying in 5 seconds...")
                time.sleep(5)
        print(f"Snapshot was found, preparing download...")

        # Package snapshot
        response = self.session.post(url=f"{self.base_url}/snapshots/{snapshot_id}/package")
        response.raise_for_status()

        # Poll for the snapshot to be packaged and download the actual snapshot file
        download_link_url = f"{self.base_url}/snapshots/{snapshot_id}/downloadLink"
        target_dir = os.path.join("agent", "snapshot")
        os.makedirs(target_dir, exist_ok=True)
        snapshot_path = os.path.join(target_dir, f"{self.snapshot_name}.csnap")

        while True:
            response = self.session.post(download_link_url)
            response.raise_for_status()
            download_link = response.json().get("downloadLink", "")
            print("Attempting to download snapshot...")

            with self.session.get(download_link, stream=True) as r:
                r.raise_for_status()
                with open(snapshot_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Check if the file only contains the text "csnap"
                with open(snapshot_path, "rb") as f:
                    content = f.read()
                    if content.strip() == b"csnap":
                        print("Downloaded file is placeholder 'csnap', retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    else:
                        print("Snapshot downloaded successfully.")
                        break
                    
        return self.snapshot_name





