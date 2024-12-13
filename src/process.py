"""Process Deep Lynx query results."""
from typing import Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LotStats:
    """Statistics for a Lot."""
    lot_id: str
    has_etc: float = None
    has_b: float = None
    has_euc: float = None
    
    @classmethod
    def from_lot_data(cls, lot_data: Dict) -> 'LotStats':
        """Create LotStats from lot data."""
        has_etc = float(lot_data['HasEtc']) if lot_data.get('HasEtc') else None
        has_b = float(lot_data['HasB']) if lot_data.get('HasB') else None
        has_euc = float(lot_data['HasEuC']) if lot_data.get('HasEuC') else None
        
        return cls(
            lot_id=lot_data['hasP'],
            has_etc=has_etc,
            has_b=has_b,
            has_euc=has_euc
        )
    
    def has_values(self) -> bool:
        """Check if lot has any non-null values."""
        return any([self.has_etc, self.has_b, self.has_euc])
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'lot_id': self.lot_id,
            'HasEtc': self.has_etc,
            'HasB': self.has_b,
            'HasEuC': self.has_euc
        }

def calculate_averages(lots: List[LotStats]) -> Dict:
    """Calculate averages for non-null values."""
    etc_sum = 0.0
    etc_count = 0
    b_sum = 0.0
    b_count = 0
    euc_sum = 0.0
    euc_count = 0
    
    for lot in lots:
        if lot.has_etc is not None:
            etc_sum += lot.has_etc
            etc_count += 1
        if lot.has_b is not None:
            b_sum += lot.has_b
            b_count += 1
        if lot.has_euc is not None:
            euc_sum += lot.has_euc
            euc_count += 1
    
    return {
        'HasEtc_avg': etc_sum / etc_count if etc_count > 0 else None,
        'HasB_avg': b_sum / b_count if b_count > 0 else None,
        'HasEuC_avg': euc_sum / euc_count if euc_count > 0 else None,
        'total_lots': len(lots),
        'lots_with_values': sum(1 for lot in lots if lot.has_values())
    }

def process_results(product_result: Dict, lot_results: List[Dict]) -> Dict:
    """Process query results and generate statistics."""
    try:
        # Extract products
        products = product_result.get('data', {}).get('metatypes', {}).get('Product', [])
        logger.info(f"Processing {len(products)} products")
        
        # Calculate Product HasD average and collect details
        has_d_sum = 0.0
        has_d_count = 0
        product_details = []
        
        for product in products:
            # Collect product details
            product_details.append({
                'id': product.get('_record', {}).get('original_id', 'Unknown'),
                'hasShape': product.get('hasShape'),
                'HasComp': product.get('HasComp'),
                'HasD': product.get('HasD'),
                'HasP': product.get('HasP')
            })
            
            # Calculate HasD average
            if product.get('HasD'):
                try:
                    has_d_sum += float(product['HasD'])
                    has_d_count += 1
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert HasD value '{product['HasD']}' to float: {e}")
        
        has_d_avg = has_d_sum / has_d_count if has_d_count > 0 else None
        logger.info(f"Average HasD across {has_d_count} products: {has_d_avg}")
        
        # Process lots
        lots = []
        for lot_result in lot_results:
            lot_data = lot_result.get('data', {}).get('metatypes', {}).get('Lot', [])
            if lot_data and len(lot_data) > 0:
                lot = LotStats.from_lot_data(lot_data[0])
                lots.append(lot)
                logger.info(f"Processed lot {lot.lot_id} - Has values: {lot.has_values()}")
        
        # Calculate statistics
        stats = calculate_averages(lots)
        
        # Prepare output
        return {
            'products': len(products),
            'product_details': product_details,
            'product_averages': {
                'HasD': has_d_avg
            },
            'lots': {
                'total': stats['total_lots'],
                'with_values': stats['lots_with_values']
            },
            'lot_averages': {
                'HasEtc': stats['HasEtc_avg'],
                'HasB': stats['HasB_avg'],
                'HasEuC': stats['HasEuC_avg']
            },
            'lot_details': [lot.to_dict() for lot in lots]
        }
    except Exception as e:
        logger.error(f"Error in process_results: {str(e)}")
        raise