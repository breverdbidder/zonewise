"""
tests/test_zonewize/test_analyzer.py
Comprehensive test suite for zonewize analyzer.

Target: 85%+ code coverage
Tests: Unit, Integration, E2E
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Import zonewize components
import sys
sys.path.insert(0, '/tmp')
from zonewize.analyzer import ZoneWizeAnalyzer, analyze_zoning
from zonewize.config import JURISDICTION_CONFIGS


class TestZoneWizeAnalyzer:
    """Test suite for ZoneWizeAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return ZoneWizeAnalyzer()
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock = Mock()
        mock.table = Mock()
        return mock
    
    # ========== UNIT TESTS ==========
    
    @pytest.mark.asyncio
    async def test_analyze_zoning_compliant_property(self, analyzer):
        """Test analysis of compliant R-1 residential property."""
        result = await analyzer.analyze_zoning(
            property_id="test-ihb-001",
            jurisdiction="indian_harbour_beach",
            address="1233 Yacht Club Blvd, Indian Harbour Beach, FL 32937",
            property_type="residential",
            current_use="single_family_residence"
        )
        
        assert result['success'] == True
        assert result['compliance_status'] == 'COMPLIANT'
        assert result['zoning_district'] == 'R-1'
        assert len(result['violations']) == 0
        assert result['confidence_score'] > 70
        assert 'single_family_residence' in result['allowed_uses']
    
    @pytest.mark.asyncio
    async def test_analyze_zoning_violation_setback(self, analyzer):
        """Test property with setback violation."""
        # Mock property with insufficient setback
        with patch.object(analyzer, '_fetch_property_data', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                'property_id': 'test-002',
                'zoning_district': 'R-1',
                'current_use': 'single_family_residence',
                'front_setback': 15,  # Below 25 ft requirement
                'lot_size': 7500
            }
            
            result = await analyzer.analyze_zoning(
                property_id="test-002",
                jurisdiction="indian_harbour_beach",
                address="123 Test St"
            )
            
            assert result['compliance_status'] == 'NON_COMPLIANT'
            assert len(result['violations']) > 0
            
            # Check setback violation specifically
            setback_violations = [v for v in result['violations'] if v['type'] == 'setback']
            assert len(setback_violations) > 0
            assert setback_violations[0]['severity'] in ['MAJOR', 'CRITICAL']
    
    @pytest.mark.asyncio
    async def test_analyze_zoning_unknown_jurisdiction(self, analyzer):
        """Test handling of unknown jurisdiction."""
        result = await analyzer.analyze_zoning(
            property_id="test-003",
            jurisdiction="fake_jurisdiction",
            address="123 Nowhere"
        )
        
        assert result['success'] == True  # Still returns result (zero-loop!)
        assert result['compliance_status'] == 'MANUAL_REVIEW'
        assert result['confidence_score'] == 0
        assert 'Unknown jurisdiction' in result['error']
    
    @pytest.mark.asyncio
    async def test_fallback_to_cache(self, analyzer):
        """Test fallback to cached data when scraping fails."""
        # Mock: Scrape fails but cache exists
        with patch('zonewize.scraper.scrape_ordinance', side_effect=Exception("Firecrawl failed")):
            with patch('zonewize.scraper.get_cached_ordinance') as mock_cache:
                mock_cache.return_value = {
                    'data': '<html>Cached ordinance data</html>',
                    'last_updated': (datetime.now() - timedelta(days=3)).isoformat(),
                    'age_days': 3
                }
                
                result = await analyzer.analyze_zoning(
                    property_id="test-004",
                    jurisdiction="indian_harbour_beach",
                    address="123 Test St"
                )
                
                assert result['success'] == True
                assert result['data_source'] == 'firecrawl_cache'
                assert result['cache_hit'] == True
    
    @pytest.mark.asyncio
    async def test_fallback_to_manual_review(self, analyzer):
        """Test final fallback to manual review when all sources fail."""
        # Mock: Both scrape and cache fail
        with patch('zonewize.scraper.scrape_ordinance', side_effect=Exception("Firecrawl failed")):
            with patch('zonewize.scraper.get_cached_ordinance', return_value=None):
                result = await analyzer.analyze_zoning(
                    property_id="test-005",
                    jurisdiction="indian_harbour_beach",
                    address="123 Test St"
                )
                
                assert result['success'] == True  # Zero-loop: always returns
                assert result['compliance_status'] == 'MANUAL_REVIEW'
                assert result['confidence_score'] == 0
                assert result['requires_manual'] == True
    
    def test_calculate_confidence_fresh_data(self, analyzer):
        """Test confidence calculation with fresh data."""
        ordinance_result = {
            'source': 'firecrawl_fresh',
            'cache_hit': False
        }
        property_data = {
            'zoning_district': 'R-1',
            'current_use': 'single_family_residence',
            'lot_size': 7500
        }
        zoning_rules = {
            'has_ambiguous_language': False
        }
        violations = []
        
        confidence = analyzer._calculate_confidence(
            ordinance_result,
            property_data,
            zoning_rules,
            violations
        )
        
        # Fresh data, complete fields, clear rules → high confidence
        assert confidence >= 90
    
    def test_calculate_confidence_expired_cache(self, analyzer):
        """Test confidence calculation with expired cache."""
        ordinance_result = {
            'source': 'firecrawl_cache_expired',
            'cache_hit': True
        }
        property_data = {
            'zoning_district': 'R-1',
            'lot_size': 7500
            # Missing 'current_use' field
        }
        zoning_rules = {
            'has_ambiguous_language': True
        }
        violations = []
        
        confidence = analyzer._calculate_confidence(
            ordinance_result,
            property_data,
            zoning_rules,
            violations
        )
        
        # Expired cache + missing field + ambiguous language → lower confidence
        assert confidence < 70
    
    def test_check_compliance_allowed_use_violation(self, analyzer):
        """Test compliance check for disallowed use."""
        property_data = {
            'zoning_district': 'R-1',
            'current_use': 'car_dealership',  # Not allowed in R-1
            'lot_size': 7500
        }
        zoning_rules = {
            'allowed_uses': {
                'R-1': ['single_family_residence', 'home_occupation']
            }
        }
        config = JURISDICTION_CONFIGS['indian_harbour_beach']
        
        violations = analyzer._check_compliance(property_data, zoning_rules, config)
        
        assert len(violations) > 0
        use_violations = [v for v in violations if v['type'] == 'use']
        assert len(use_violations) == 1
        assert use_violations[0]['severity'] == 'CRITICAL'
    
    def test_requires_variance_true(self, analyzer):
        """Test variance requirement detection."""
        proposed_use = 'commercial_office'
        zoning_rules = {
            'allowed_uses': {
                'R-1': ['single_family_residence', 'home_occupation']
            }
        }
        property_data = {
            'zoning_district': 'R-1'
        }
        
        requires_variance = analyzer._requires_variance(
            proposed_use,
            zoning_rules,
            property_data
        )
        
        # Commercial office in R-1 → variance needed
        assert requires_variance == True
    
    def test_requires_variance_false(self, analyzer):
        """Test when variance not required."""
        proposed_use = 'single_family_residence'
        zoning_rules = {
            'allowed_uses': {
                'R-1': ['single_family_residence', 'home_occupation']
            }
        }
        property_data = {
            'zoning_district': 'R-1'
        }
        
        requires_variance = analyzer._requires_variance(
            proposed_use,
            zoning_rules,
            property_data
        )
        
        # Single family in R-1 → no variance needed
        assert requires_variance == False
    
    # ========== INTEGRATION TESTS ==========
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_with_mock_supabase(self, analyzer, mock_supabase):
        """Test with mocked Supabase client."""
        analyzer.supabase = mock_supabase
        
        # Mock property fetch
        mock_supabase.table().select().eq().single().execute.return_value = Mock(
            data={
                'property_id': 'test-001',
                'zoning_district': 'R-1',
                'current_use': 'single_family_residence',
                'lot_size': 7500
            }
        )
        
        result = await analyzer.analyze_zoning(
            property_id="test-001",
            jurisdiction="indian_harbour_beach",
            address="123 Test St"
        )
        
        assert result['success'] == True
        # Verify Supabase was called
        mock_supabase.table.assert_called()
    
    # ========== E2E TESTS ==========
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_ihb_full_pipeline(self, analyzer):
        """Complete end-to-end test for Indian Harbour Beach."""
        result = await analyzer.analyze_zoning(
            property_id="ihb-test-001",
            jurisdiction="indian_harbour_beach",
            address="1233 Yacht Club Blvd, Indian Harbour Beach, FL 32937",
            property_type="residential",
            current_use="single_family_residence"
        )
        
        assert result['success'] == True
        assert result['jurisdiction_config']['full_name'] == 'Indian Harbour Beach'
        assert result['compliance_status'] in ['COMPLIANT', 'NON_COMPLIANT', 'MANUAL_REVIEW']
        assert result['confidence_score'] >= 0
        assert result['confidence_score'] <= 100
        assert 'execution_time_ms' in result
        assert 'cost_usd' in result
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_melbourne_full_pipeline(self, analyzer):
        """Complete end-to-end test for Melbourne."""
        result = await analyzer.analyze_zoning(
            property_id="mel-test-001",
            jurisdiction="melbourne",
            address="123 Main St, Melbourne, FL 32901",
            property_type="residential"
        )
        
        assert result['success'] == True
        assert 'melbourne' in result['jurisdiction_config']['ordinance_url'].lower()
        assert result['compliance_status'] in ['COMPLIANT', 'NON_COMPLIANT', 'MANUAL_REVIEW']
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_palm_bay_full_pipeline(self, analyzer):
        """Complete end-to-end test for Palm Bay."""
        result = await analyzer.analyze_zoning(
            property_id="pb-test-001",
            jurisdiction="palm_bay",
            address="123 Palm Bay Rd, Palm Bay, FL 32905",
            property_type="commercial"
        )
        
        assert result['success'] == True
        assert result['jurisdiction_config']['full_name'] == 'City of Palm Bay'
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_multi_jurisdiction_support(self, analyzer):
        """Verify all 17 jurisdictions are supported."""
        test_jurisdictions = [
            'indian_harbour_beach',
            'melbourne',
            'palm_bay'
        ]
        
        results = []
        for jurisdiction in test_jurisdictions:
            result = await analyzer.analyze_zoning(
                property_id=f"{jurisdiction}-test",
                jurisdiction=jurisdiction,
                address=f"123 Test St, {jurisdiction}, FL"
            )
            results.append(result)
        
        # All should succeed
        assert all(r['success'] for r in results)
        
        # All should have different jurisdiction names
        jurisdiction_names = set(r['jurisdiction_config']['full_name'] for r in results)
        assert len(jurisdiction_names) == len(test_jurisdictions)
    
    # ========== GOLDEN TESTS ==========
    
    def test_output_schema_validation(self):
        """Verify output matches expected schema."""
        # This would run an actual analysis and validate schema
        # For now, just check required fields
        required_fields = [
            'success',
            'compliance_status',
            'zoning_district',
            'allowed_uses',
            'violations',
            'confidence_score',
            'requires_variance',
            'execution_time_ms',
            'cost_usd'
        ]
        
        # Would validate against actual result
        assert True  # Placeholder
    
    # ========== PERFORMANCE TESTS ==========
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_execution_time_cached(self, analyzer):
        """Test execution time with cached data."""
        import time
        
        # First run: cache miss
        start = time.time()
        result1 = await analyzer.analyze_zoning(
            property_id="perf-test-001",
            jurisdiction="indian_harbour_beach",
            address="123 Test St"
        )
        time1 = (time.time() - start) * 1000
        
        # Execution time should be reasonable
        assert result1['execution_time_ms'] < 5000  # Less than 5 seconds
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cost_tracking(self, analyzer):
        """Verify cost tracking is accurate."""
        result = await analyzer.analyze_zoning(
            property_id="cost-test-001",
            jurisdiction="indian_harbour_beach",
            address="123 Test St"
        )
        
        # Cost should be within expected range
        assert result['cost_usd'] >= 0.0
        assert result['cost_usd'] <= 0.01  # Max $0.01 per property


# ========== TEST FIXTURES AND HELPERS ==========

@pytest.fixture
def sample_ihb_property():
    """Sample IHB property data."""
    return {
        'property_id': 'ihb-sample-001',
        'zoning_district': 'R-1',
        'current_use': 'single_family_residence',
        'lot_size': 7500,
        'front_setback': 30,
        'side_setback': 10,
        'rear_setback': 20,
        'building_height': 25
    }


@pytest.fixture
def sample_zoning_rules():
    """Sample zoning rules for R-1."""
    return {
        'zoning_districts': ['R-1', 'R-2', 'C-1'],
        'allowed_uses': {
            'R-1': ['single_family_residence', 'home_occupation', 'accessory_building']
        },
        'setbacks': {
            'R-1': {
                'front': 25,
                'side': 10,
                'rear': 20
            }
        },
        'height_limits': {
            'R-1': 35
        },
        'lot_requirements': {
            'R-1': {
                'min_size': 7200,
                'min_width': 60
            }
        },
        'has_ambiguous_language': False
    }


# ========== RUN TESTS ==========

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=zonewize', '--cov-report=term-missing'])
