"""
zonewize/analyzer.py
Core zoning compliance analysis logic with zero-loop execution.

Responsibilities:
- Orchestrate compliance check workflow
- Implement 3-tier fallback system
- Calculate confidence scores
- Log observability metrics
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import from ZoneWise observability (to be implemented)
# from src.observability import structured_logger, log_metric, track_error

# Import skill components
from .scraper import scrape_ordinance, get_cached_ordinance
from .parser import parse_ordinance, extract_zoning_rules
from .forecaster import predict_compliance_confidence
from .config import JURISDICTION_CONFIGS


class ZoneWizeAnalyzer:
    """
    Main analyzer for zoning compliance checks.
    Implements zero-loop execution with comprehensive fallbacks.
    """
    
    def __init__(self, supabase_client=None, firecrawl_client=None):
        """
        Initialize analyzer with optional clients.
        
        Args:
            supabase_client: Supabase client for database operations
            firecrawl_client: Firecrawl client for web scraping
        """
        self.supabase = supabase_client
        self.firecrawl = firecrawl_client
    
    async def analyze_zoning(
        self,
        property_id: str,
        jurisdiction: str,
        address: str,
        parcel_id: Optional[str] = None,
        property_type: str = "residential",
        current_use: Optional[str] = None,
        proposed_use: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze property zoning compliance.
        
        ZERO-LOOP GUARANTEE:
        - Always returns a result (never raises exception to caller)
        - Three-tier fallback: Fresh scrape → Cache → Manual review
        
        Args:
            property_id: Unique property ID in ZoneWise database
            jurisdiction: One of 17 Brevard jurisdictions
            address: Full property address
            parcel_id: County parcel ID (optional)
            property_type: Type of property (residential, commercial, etc.)
            current_use: Actual current use of property
            proposed_use: Proposed future use (for development analysis)
            correlation_id: For distributed tracing
        
        Returns:
            Dict containing compliance analysis results
        """
        start_time = time.time()
        correlation_id = correlation_id or str(uuid.uuid4())
        
        # Log start
        self._log_start(correlation_id, property_id, jurisdiction)
        
        try:
            # Validate jurisdiction
            if jurisdiction not in JURISDICTION_CONFIGS:
                return self._manual_review_result(
                    f"Unknown jurisdiction: {jurisdiction}",
                    correlation_id,
                    start_time
                )
            
            jurisdiction_config = JURISDICTION_CONFIGS[jurisdiction]
            
            # Step 1: Get ordinance data (with fallback chain)
            ordinance_result = await self._get_ordinance_data(
                jurisdiction,
                jurisdiction_config,
                correlation_id
            )
            
            if not ordinance_result['success']:
                return self._manual_review_result(
                    ordinance_result['error'],
                    correlation_id,
                    start_time
                )
            
            ordinance_data = ordinance_result['data']
            data_source = ordinance_result['source']
            cache_hit = ordinance_result['cache_hit']
            
            # Step 2: Parse ordinance
            try:
                zoning_rules = parse_ordinance(ordinance_data, jurisdiction)
            except Exception as e:
                self._log_error("ordinance_parse_failed", str(e), correlation_id)
                return self._manual_review_result(
                    f"Failed to parse ordinance: {str(e)}",
                    correlation_id,
                    start_time
                )
            
            # Step 3: Fetch property data
            property_data = await self._fetch_property_data(property_id)
            
            # Step 4: Analyze compliance
            violations = self._check_compliance(
                property_data,
                zoning_rules,
                jurisdiction_config
            )
            
            compliance_status = "COMPLIANT" if len(violations) == 0 else "NON_COMPLIANT"
            
            # Step 5: Calculate confidence
            confidence_score = self._calculate_confidence(
                ordinance_result,
                property_data,
                zoning_rules,
                violations
            )
            
            # Step 6: Determine variance requirement
            requires_variance = self._requires_variance(
                proposed_use,
                zoning_rules,
                property_data
            )
            
            # Calculate cost
            cost_usd = 0.005 if not cache_hit else 0.0  # Firecrawl cost
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Build result
            result = {
                "success": True,
                "compliance_status": compliance_status,
                "zoning_district": property_data.get('zoning_district', 'UNKNOWN'),
                "allowed_uses": zoning_rules.get('allowed_uses', {}).get(
                    property_data.get('zoning_district'), []
                ),
                "violations": violations,
                "confidence_score": confidence_score,
                "requires_variance": requires_variance,
                "ordinance_sections": zoning_rules.get('sections_referenced', []),
                "ordinance_last_updated": ordinance_result.get('last_updated'),
                "data_source": data_source,
                "cache_hit": cache_hit,
                "execution_time_ms": execution_time_ms,
                "cost_usd": cost_usd,
                "jurisdiction_config": {
                    "full_name": jurisdiction_config['full_name'],
                    "contact_email": jurisdiction_config.get('contact_email'),
                    "contact_phone": jurisdiction_config.get('contact_phone')
                }
            }
            
            # Log completion
            self._log_completion(result, correlation_id)
            
            return result
            
        except Exception as e:
            # Ultimate fallback: Return manual review
            self._log_error("zonewize_unexpected_error", str(e), correlation_id)
            return self._manual_review_result(
                f"Unexpected error: {str(e)}",
                correlation_id,
                start_time
            )
    
    async def _get_ordinance_data(
        self,
        jurisdiction: str,
        config: Dict,
        correlation_id: str
    ) -> Dict:
        """
        Get ordinance data with fallback chain.
        
        Priority:
        1. Fresh cache (<7 days old)
        2. Fresh Firecrawl scrape
        3. Expired cache (>7 days old)
        4. Manual review (all failed)
        """
        # Check cache first
        cached = get_cached_ordinance(jurisdiction, self.supabase)
        
        if cached and cached['age_days'] < 7:
            # Cache hit - use it
            return {
                'success': True,
                'data': cached['data'],
                'source': 'firecrawl_cache',
                'cache_hit': True,
                'last_updated': cached['last_updated']
            }
        
        # Cache miss or expired - try fresh scrape
        try:
            scrape_result = await scrape_ordinance(
                config['ordinance_url'],
                self.firecrawl
            )
            
            if scrape_result['success']:
                # Cache the fresh data
                self._cache_ordinance(
                    jurisdiction,
                    scrape_result['content'],
                    correlation_id
                )
                
                return {
                    'success': True,
                    'data': scrape_result['content'],
                    'source': 'firecrawl_fresh',
                    'cache_hit': False,
                    'last_updated': datetime.now().isoformat()
                }
        
        except Exception as e:
            self._log_error("firecrawl_scrape_failed", str(e), correlation_id)
        
        # Fallback 1: Use expired cache
        if cached:
            self._log_metric("zonewize_expired_cache_used", 1, correlation_id)
            return {
                'success': True,
                'data': cached['data'],
                'source': 'firecrawl_cache_expired',
                'cache_hit': True,
                'last_updated': cached['last_updated']
            }
        
        # Fallback 2: Manual review required
        return {
            'success': False,
            'error': 'No ordinance data available (scrape failed, no cache)'
        }
    
    async def _fetch_property_data(self, property_id: str) -> Dict:
        """Fetch property data from Supabase."""
        if not self.supabase:
            # Mock data for testing
            return {
                'property_id': property_id,
                'zoning_district': 'R-1',
                'property_type': 'residential',
                'current_use': 'single_family_residence',
                'lot_size': 7500,
                'front_setback': 30,
                'side_setback': 10,
                'rear_setback': 20,
                'building_height': 25
            }
        
        # Real Supabase query
        try:
            result = self.supabase.table('properties').select('*').eq(
                'id', property_id
            ).single().execute()
            
            return result.data
        except Exception as e:
            self._log_error("property_fetch_failed", str(e), property_id)
            return {}
    
    def _check_compliance(
        self,
        property_data: Dict,
        zoning_rules: Dict,
        config: Dict
    ) -> List[Dict]:
        """
        Check property compliance against zoning rules.
        
        Returns:
            List of violations (empty if compliant)
        """
        violations = []
        zoning_district = property_data.get('zoning_district')
        
        if not zoning_district:
            return violations
        
        # Check 1: Allowed Use
        allowed_uses = zoning_rules.get('allowed_uses', {}).get(zoning_district, [])
        current_use = property_data.get('current_use')
        
        if current_use and current_use not in allowed_uses:
            violations.append({
                'type': 'use',
                'description': f"{current_use} is not permitted in {zoning_district}",
                'severity': 'CRITICAL',
                'code_reference': zoning_rules.get('use_section', 'N/A'),
                'current_value': current_use,
                'required_value': ', '.join(allowed_uses)
            })
        
        # Check 2: Setbacks
        setback_rules = zoning_rules.get('setbacks', {}).get(zoning_district, {})
        
        if 'front' in setback_rules:
            required_front = setback_rules['front']
            actual_front = property_data.get('front_setback', 0)
            
            if actual_front < required_front:
                violations.append({
                    'type': 'setback',
                    'description': f'Front setback violation',
                    'severity': 'MAJOR',
                    'code_reference': zoning_rules.get('setback_section', 'N/A'),
                    'current_value': f'{actual_front} ft',
                    'required_value': f'{required_front} ft minimum'
                })
        
        # Check 3: Height
        height_limit = zoning_rules.get('height_limits', {}).get(zoning_district)
        
        if height_limit:
            actual_height = property_data.get('building_height', 0)
            
            if actual_height > height_limit:
                violations.append({
                    'type': 'height',
                    'description': 'Building height exceeds limit',
                    'severity': 'MAJOR',
                    'code_reference': zoning_rules.get('height_section', 'N/A'),
                    'current_value': f'{actual_height} ft',
                    'required_value': f'{height_limit} ft maximum'
                })
        
        # Check 4: Lot Size
        min_lot_size = zoning_rules.get('lot_requirements', {}).get(
            zoning_district, {}
        ).get('min_size')
        
        if min_lot_size:
            actual_lot_size = property_data.get('lot_size', 0)
            
            if actual_lot_size < min_lot_size:
                violations.append({
                    'type': 'lot_size',
                    'description': 'Lot size below minimum',
                    'severity': 'CRITICAL',
                    'code_reference': zoning_rules.get('lot_section', 'N/A'),
                    'current_value': f'{actual_lot_size} sqft',
                    'required_value': f'{min_lot_size} sqft minimum'
                })
        
        return violations
    
    def _calculate_confidence(
        self,
        ordinance_result: Dict,
        property_data: Dict,
        zoning_rules: Dict,
        violations: List[Dict]
    ) -> int:
        """
        Calculate confidence score (0-100) for analysis.
        
        Factors:
        - Data recency (newer = higher)
        - Ordinance clarity (clear rules = higher)
        - Property data completeness (more data = higher)
        - Edge cases (ambiguity = lower)
        """
        confidence = 100
        
        # Factor 1: Data age
        if ordinance_result['source'] == 'firecrawl_cache_expired':
            confidence -= 20
        elif ordinance_result['source'] == 'firecrawl_cache':
            confidence -= 5
        
        # Factor 2: Property data completeness
        required_fields = ['zoning_district', 'current_use', 'lot_size']
        missing_fields = [f for f in required_fields if not property_data.get(f)]
        confidence -= len(missing_fields) * 10
        
        # Factor 3: Rule clarity
        if zoning_rules.get('has_ambiguous_language'):
            confidence -= 15
        
        # Factor 4: Edge cases
        if property_data.get('has_overlay_district'):
            confidence -= 10
        
        if property_data.get('has_grandfathered_status'):
            confidence -= 15
        
        # Clamp to 0-100
        return max(0, min(100, confidence))
    
    def _requires_variance(
        self,
        proposed_use: Optional[str],
        zoning_rules: Dict,
        property_data: Dict
    ) -> bool:
        """Determine if proposed use requires variance."""
        if not proposed_use:
            return False
        
        zoning_district = property_data.get('zoning_district')
        if not zoning_district:
            return False
        
        allowed_uses = zoning_rules.get('allowed_uses', {}).get(zoning_district, [])
        
        # If proposed use not in allowed uses, variance likely needed
        return proposed_use not in allowed_uses
    
    def _cache_ordinance(
        self,
        jurisdiction: str,
        content: str,
        correlation_id: str
    ) -> None:
        """Cache ordinance data in Supabase."""
        if not self.supabase:
            return
        
        try:
            self.supabase.table('ordinance_cache').upsert({
                'jurisdiction': jurisdiction,
                'content': content,
                'last_updated': datetime.now().isoformat(),
                'correlation_id': correlation_id
            }).execute()
        except Exception as e:
            self._log_error("cache_write_failed", str(e), correlation_id)
    
    def _manual_review_result(
        self,
        error_message: str,
        correlation_id: str,
        start_time: float
    ) -> Dict:
        """Return MANUAL_REVIEW result (final fallback)."""
        execution_time_ms = (time.time() - start_time) * 1000
        
        result = {
            "success": True,  # Still success (didn't crash!)
            "compliance_status": "MANUAL_REVIEW",
            "zoning_district": "UNKNOWN",
            "allowed_uses": [],
            "violations": [],
            "confidence_score": 0,
            "requires_variance": False,
            "requires_manual": True,
            "error": error_message,
            "execution_time_ms": execution_time_ms,
            "cost_usd": 0.0
        }
        
        self._log_completion(result, correlation_id)
        return result
    
    # Observability helpers (placeholders until integrated)
    def _log_start(self, correlation_id, property_id, jurisdiction):
        """Log analysis start."""
        print(f"[zonewize_started] correlation_id={correlation_id} property={property_id} jurisdiction={jurisdiction}")
    
    def _log_completion(self, result, correlation_id):
        """Log analysis completion."""
        print(f"[zonewize_completed] correlation_id={correlation_id} status={result['compliance_status']} confidence={result['confidence_score']}")
    
    def _log_metric(self, metric_name, value, correlation_id):
        """Log metric."""
        print(f"[METRIC] {metric_name}={value} correlation_id={correlation_id}")
    
    def _log_error(self, error_type, message, correlation_id):
        """Log error."""
        print(f"[ERROR] {error_type}: {message} correlation_id={correlation_id}")


# Convenience function for direct use
async def analyze_zoning(**kwargs) -> Dict[str, Any]:
    """
    Convenience function to analyze zoning compliance.
    
    See ZoneWizeAnalyzer.analyze_zoning for full documentation.
    """
    analyzer = ZoneWizeAnalyzer()
    return await analyzer.analyze_zoning(**kwargs)
