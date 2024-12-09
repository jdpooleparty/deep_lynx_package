import os
import json
import requests
from config import get_settings

def get_auth_token():
    """Get authentication token from Deep Lynx."""
    settings = get_settings()
    auth_endpoint = f"{settings.DEEP_LYNX_URL}/oauth/token"
    headers = {
        "x-api-key": settings.DEEP_LYNX_API_KEY,
        "x-api-secret": settings.DEEP_LYNX_API_SECRET
    }
    
    response = requests.get(auth_endpoint, headers=headers)
    if response.status_code == 200:
        token = response.text
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        return token
    else:
        raise Exception(f"Failed to get auth token: {response.text}")

def query_lot(lot_id: str = "01-52"):
    """Query a single lot with the specified ID."""
    settings = get_settings()
    token = get_auth_token()
    print(f"Successfully retrieved auth token")
    
    # Construct the query exactly as specified
    query = """{ 
  metatypes {
    Lot (
      _record: {
        original_id: {operator: "eq", value: "%s"}
      }
    ) {
      hasP
      HasEtc
      HasB
      HasEuC
      _record { 
        id
        data_source_id
        original_id
        import_id
        metatype_id
        metatype_name
        created_at
        created_by
        modified_at
        modified_by
        metadata
      }
    }
  }
}""" % lot_id

    print("\nQuery being sent:")
    print(query)
    
    # Send the query
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{settings.DEEP_LYNX_URL}/containers/{settings.DEEP_LYNX_CONTAINER_ID}/data",
        headers=headers,
        json={"query": query}
    )
    
    print("\nResponse status code:", response.status_code)
    
    if response.status_code == 200:
        result = response.json()
        print("\nRaw response:")
        print(json.dumps(result, indent=2))
        
        # Extract the Lot data if it exists
        try:
            lot_data = result["data"]["metatypes"]["Lot"][0]
            print("\nLot data found:")
            print(json.dumps(lot_data, indent=2))
        except (KeyError, IndexError):
            print("\nNo Lot data found in the response")
    else:
        print("Query failed:", response.text)

if __name__ == "__main__":
    # Test with default lot ID "01-52"
    print("\nTesting with lot 01-52:")
    query_lot()
    
    # Test with lot 88-77
    print("\nTesting with lot 88-77:")
    query_lot("88-77")