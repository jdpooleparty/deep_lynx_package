"""Deep Lynx query functionality."""
import logging
from typing import Dict, Any, List
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_auth_token(base_url: str, api_key: str, api_secret: str) -> str:
    """Get authentication token from Deep Lynx."""
    try:
        auth_endpoint = f"{base_url}/oauth/token"
        headers = {
            "x-api-key": api_key,
            "x-api-secret": api_secret
        }
        
        response = requests.get(auth_endpoint, headers=headers)
        response.raise_for_status()
        
        token = response.text
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
            
        logger.info("Successfully retrieved auth token")
        return token
        
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        raise

def query_deep_lynx(base_url: str, container_id: str, api_key: str, api_secret: str, query: str) -> Dict:
    """Send GraphQL query to Deep Lynx."""
    try:
        # Get token
        token = get_auth_token(base_url, api_key, api_secret)
        
        # Make request
        endpoint = f"{base_url}/containers/{container_id}/data"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {"query": query}
        
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise

# Query templates
PRODUCT_QUERY = """
{ 
  metatypes {
    Product (
      hasShape: {operator: "eq", value: 6}
      HasComp: {operator: "eq", value: "N"}
    ) {
      hasShape
      HasComp
      HasD
      HasP
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
}
"""

def get_lot_query(original_id: str) -> str:
    """Get Lot query for a specific original_id."""
    return f"""{{ 
      metatypes {{
        Lot (
          _record: {{
            original_id: {{operator: "eq", value: "{original_id}"}}
          }}
        ) {{
          hasP
          HasEtc
          HasB
          HasEuC
          _record {{ 
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
          }}
        }}
      }}
    }}"""

def query_products(settings) -> Dict:
    """Query for Products."""
    logger.info("Querying Products...")
    return query_deep_lynx(
        settings.DEEP_LYNX_URL,
        settings.DEEP_LYNX_CONTAINER_ID,
        settings.DEEP_LYNX_API_KEY,
        settings.DEEP_LYNX_API_SECRET,
        PRODUCT_QUERY
    )

def query_lots(settings, has_p_values: List[str]) -> List[Dict]:
    """Query for Lots based on HasP values."""
    logger.info(f"Querying {len(has_p_values)} Lots...")
    results = []
    for has_p in has_p_values:
        logger.info(f"Querying Lot: {has_p}")
        result = query_deep_lynx(
            settings.DEEP_LYNX_URL,
            settings.DEEP_LYNX_CONTAINER_ID,
            settings.DEEP_LYNX_API_KEY,
            settings.DEEP_LYNX_API_SECRET,
            get_lot_query(has_p)
        )
        results.append(result)
    return results 