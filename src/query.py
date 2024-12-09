"""Deep Lynx query functionality."""
import logging
from typing import Dict, Any, List
import requests
import json
from datetime import datetime

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
def get_product_query(shape: int, comp: str) -> str:
    """Get Product query with specific shape and comp values."""
    return f"""{{ 
      metatypes {{
        Product (
          hasShape: {{operator: "eq", value: {shape}}}
          HasComp: {{operator: "eq", value: "{comp}"}}
        ) {{
          hasShape
          HasComp
          HasD
          HasP
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

def get_lot_query(lot_id: str) -> str:
    """Get Lot query for a specific lot ID."""
    return """{ 
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

def save_raw_data(product_result: Dict, lot_results: List[Dict], shape: int, comp: str):
    """Save raw query results to a JSON file.
    
    Args:
        product_result: Raw product query result
        lot_results: List of raw lot query results
        shape: Shape value used in query
        comp: Comp value used in query
    """
    # Create output directory if it doesn't exist
    import os
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare data structure
    raw_data = {
        "query_params": {
            "shape": shape,
            "comp": comp,
            "timestamp": datetime.now().isoformat()
        },
        "product_data": product_result,
        "lot_data": lot_results
    }
    
    # Save to file
    filename = f"output/raw_data_shape{shape}_comp{comp}_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(raw_data, f, indent=2)
    
    logger.info(f"\nRaw data saved to: {filename}")

def query_products(settings, shape: int, comp: str) -> Dict:
    """Query for Products with specific shape and comp values."""
    logger.info("Querying Products...")
    query = get_product_query(shape, comp)
    logger.info(f"Product query: {query}")
    
    result = query_deep_lynx(
        settings.DEEP_LYNX_URL,
        settings.DEEP_LYNX_CONTAINER_ID,
        settings.DEEP_LYNX_API_KEY,
        settings.DEEP_LYNX_API_SECRET,
        query
    )
    
    # Log first product for debugging
    if result.get('data', {}).get('metatypes', {}).get('Product'):
        first_product = result['data']['metatypes']['Product'][0]
        logger.info(f"Sample product data: {json.dumps(first_product, indent=2)}")
    
    return result

def query_lots(settings, has_p_values: List[str]) -> List[Dict]:
    """Query for Lots based on HasP values."""
    # Remove duplicates while preserving order
    unique_has_p_values = list(dict.fromkeys(has_p_values))
    logger.info(f"Querying {len(unique_has_p_values)} unique Lots: {unique_has_p_values}")
    
    results = []
    for has_p in unique_has_p_values:
        logger.info(f"\nQuerying Lot: {has_p}")
        query = get_lot_query(has_p)
        logger.info(f"Query:\n{query}")
        
        result = query_deep_lynx(
            settings.DEEP_LYNX_URL,
            settings.DEEP_LYNX_CONTAINER_ID,
            settings.DEEP_LYNX_API_KEY,
            settings.DEEP_LYNX_API_SECRET,
            query
        )
        
        # Log raw response for debugging
        if result.get('data', {}).get('metatypes', {}).get('Lot'):
            lot_data = result['data']['metatypes']['Lot'][0]
            logger.info("Raw Lot data:")
            logger.info(json.dumps(lot_data, indent=2))
            logger.info(f"Available fields: {list(lot_data.keys())}")
            logger.info(f"Field types:")
            for key, value in lot_data.items():
                if key != '_record':
                    logger.info(f"  {key}: {type(value).__name__} = {value}")
        else:
            logger.warning(f"No lot data found for HasP: {has_p}")
            
        results.append(result)
    return results 