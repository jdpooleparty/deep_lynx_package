"""Main workflow script for Deep Lynx queries and processing."""
import json
import logging
from typing import Dict, List

from config import get_settings
from query import query_products, query_lots
from process import process_results

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def extract_has_p_values(product_result: Dict) -> List[str]:
    """Extract HasP values from product query result."""
    has_p_values = []
    products = product_result.get('data', {}).get('metatypes', {}).get('Product', [])
    for product in products:
        has_p = product.get('HasP')
        if has_p:
            has_p_values.append(has_p)
    return has_p_values

def run_workflow(include_example: bool = True) -> Dict:
    """Run the complete workflow.
    
    Args:
        include_example: Whether to include example Lot 01-52 in results
        
    Returns:
        Dict containing processed results
    """
    try:
        # Get settings
        settings = get_settings()
        logger.info("\n=== Configuration ===")
        logger.info(f"Host: {settings.DEEP_LYNX_URL}")
        logger.info(f"Container ID: {settings.DEEP_LYNX_CONTAINER_ID}")
        
        # Query products
        logger.info("\n=== Querying Products ===")
        product_result = query_products(settings)
        
        # Get HasP values
        has_p_values = extract_has_p_values(product_result)
        if include_example:
            has_p_values.append("01-52")
        
        # Query lots
        logger.info("\n=== Querying Lots ===")
        lot_results = query_lots(settings, has_p_values)
        
        # Process results
        logger.info("\n=== Processing Results ===")
        result = process_results(product_result, lot_results)
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        raise

def main():
    """Run workflow and print results."""
    try:
        result = run_workflow()
        print("\nProcessed Results:")
        print(json.dumps(result, indent=2))
        
        # Print summary
        print("\nSummary:")
        print(f"Products processed: {result['products']}")
        print(f"Lots processed: {result['lots']['total']}")
        print(f"Lots with values: {result['lots']['with_values']}")
        if result['averages']['HasEtc']:
            print(f"Average HasEtc: {result['averages']['HasEtc']:.4f}")
        if result['averages']['HasB']:
            print(f"Average HasB: {result['averages']['HasB']:.4f}")
        if result['averages']['HasEuC']:
            print(f"Average HasEuC: {result['averages']['HasEuC']:.4f}")
            
    except Exception as e:
        logger.error(f"Main failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 