"""Main workflow script for Deep Lynx queries and processing."""
import json
import logging
import argparse
from typing import Dict, List

from config import get_settings
from query import query_products, query_lots, get_product_query, save_raw_data
from process import process_results

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Query Deep Lynx for Products with specific Shape and Comp values'
    )
    parser.add_argument(
        'shape',
        type=int,
        help='Value for hasShape filter (e.g., 6 or 8)'
    )
    parser.add_argument(
        'comp',
        type=str,
        help='Value for HasComp filter (e.g., "N" or "V")'
    )
    parser.add_argument(
        '--include-example',
        action='store_true',
        help='Include example Lot 01-52 in results',
        default=False
    )
    return parser.parse_args()

def extract_has_p_values(product_result: Dict) -> List[str]:
    """Extract HasP values from product query result."""
    has_p_values = []
    products = product_result.get('data', {}).get('metatypes', {}).get('Product', [])
    logger.info(f"\nExtracting HasP values from {len(products)} products")
    
    for product in products:
        has_p = product.get('HasP')
        if has_p:
            has_p_values.append(has_p)
            logger.info(f"Found HasP value: {has_p}")
        else:
            logger.warning(f"No HasP value found for product {product.get('_record', {}).get('original_id')}")
    
    logger.info(f"Total HasP values found: {len(has_p_values)}")
    return has_p_values

def run_workflow(shape: int, comp: str, include_example: bool = False) -> Dict:
    """Run the complete workflow.
    
    Args:
        shape: Value for hasShape filter
        comp: Value for HasComp filter
        include_example: Whether to include example Lot 01-52 in results (default: False)
        
    Returns:
        Dict containing processed results
    """
    try:
        # Get settings
        settings = get_settings()
        logger.info("\n=== Configuration ===")
        logger.info(f"Host: {settings.DEEP_LYNX_URL}")
        logger.info(f"Container ID: {settings.DEEP_LYNX_CONTAINER_ID}")
        logger.info(f"Filters: hasShape={shape}, HasComp={comp}")
        
        # Query products
        logger.info("\n=== Querying Products ===")
        product_result = query_products(settings, shape, comp)
        
        # Get HasP values
        has_p_values = extract_has_p_values(product_result)
        if include_example:
            has_p_values.append("01-52")
        
        # Query lots
        logger.info("\n=== Querying Lots ===")
        lot_results = query_lots(settings, has_p_values)
        
        # Save raw data to JSON
        save_raw_data(product_result, lot_results, shape, comp)
        
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
        # Parse command line arguments
        args = parse_args()
        
        # Run workflow with provided arguments
        result = run_workflow(args.shape, args.comp, args.include_example)
        
        print("\nProcessed Results:")
        print(json.dumps(result, indent=2))
        
        # Print summary
        print("\nSummary:")
        print("=== Products ===")
        print(f"Products processed: {result['products']}")
        
        # Show Product details
        print("\nProduct Details:")
        print("ProductId\tShape\tComp\tHasD\tHasP")
        print("-" * 60)
        for product in result['product_details']:
            print(f"{product['id']}\t{product['hasShape']}\t{product['HasComp']}\t{product['HasD']}\t{product.get('HasP', 'N/A')}")
        
        if result['product_averages']['HasD']:
            print(f"\nAverage Product HasD: {result['product_averages']['HasD']:.4f}")
            
        print("\n=== Lots ===")
        print(f"Lots processed: {result['lots']['total']}")
        print(f"Lots with values: {result['lots']['with_values']}")
        
        # Show Lot details
        if result['lot_details']:
            print("\nLot Details:")
            print("LotId\tHasEtc\tHasB\tHasEuC")
            print("-" * 50)
            for lot in result['lot_details']:
                print(f"{lot['lot_id']}\t{lot.get('HasEtc', 'N/A')}\t{lot.get('HasB', 'N/A')}\t{lot.get('HasEuC', 'N/A')}")
        
        if result['lot_averages']['HasEtc']:
            print(f"\nAverage Lot HasEtc: {result['lot_averages']['HasEtc']:.4f}")
        if result['lot_averages']['HasB']:
            print(f"Average Lot HasB: {result['lot_averages']['HasB']:.4f}")
        if result['lot_averages']['HasEuC']:
            print(f"Average Lot HasEuC: {result['lot_averages']['HasEuC']:.4f}")
            
    except Exception as e:
        logger.error(f"Main failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 