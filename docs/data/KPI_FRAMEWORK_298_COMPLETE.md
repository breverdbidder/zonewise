# BidDeed.AI / ZoneWise: Complete 298 KPI Framework

**Version:** 2.0  
**Date:** January 25, 2026  
**Status:** PRODUCTION READY  
**Competitive Edge:** 298 KPIs vs PropertyOnion's 96 vs Gridics' 74

---

## Executive Summary

The **298 KPI Framework** combines:
- **PropertyOnion KPIs (96):** Foreclosure/auction data
- **BidDeed.AI Exclusive (74):** ML predictions, investment scoring
- **ZoneWise Exclusive (128):** Zoning, HBU analysis, CMA deep

This unified framework powers our "Claude AI for Real Estate" split-screen interface.

---

## KPI Distribution by Source

```
┌─────────────────────────────────────────────────────────────────┐
│                    298 UNIFIED KPI FRAMEWORK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PROPERTYONION REPLICATED (96 KPIs)                             │
│  ├── Property Basics: ZW-001 to ZW-012 (12)                     │
│  ├── Auction Info: ZW-075 to ZW-092 (18)                        │
│  ├── Financial: ZW-093 to ZW-114 (22)                           │
│  ├── Liens: ZW-115 to ZW-134 (20)                               │
│  ├── Physical: ZW-151 to ZW-164 (14)                            │
│  └── Market: ZW-191 to ZW-200 (10)                              │
│                                                                  │
│  BIDDEED.AI EXCLUSIVE (74 KPIs)                                 │
│  ├── ML Predictions: ZW-135 to ZW-150 (16)                      │
│  ├── Investment Scoring: ZW-165 to ZW-176 (12)                  │
│  ├── Risk Assessment: ZW-249 to ZW-258 (10)                     │
│  ├── Demographics: ZW-177 to ZW-190 (14)                        │
│  ├── Comps Deep: ZW-205 to ZW-220 (16)                          │
│  └── Red Flags: ZW-259 to ZW-264 (6)                            │
│                                                                  │
│  ZONEWISE EXCLUSIVE (128 KPIs)                                  │
│  ├── Zoning & Land Use: ZW-013 to ZW-074 (62)                   │
│  ├── HBU Analysis: ZW-221 to ZW-232 (12) ⭐ UNIQUE              │
│  ├── CMA Deep: ZW-233 to ZW-248 (16) ⭐ UNIQUE                  │
│  ├── Development Process: ZW-265 to ZW-280 (16)                 │
│  └── Environmental: ZW-281 to ZW-298 (18)                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete KPI List by Category

### Category 1: Property Identification (12 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-001 | parcel_id | VARCHAR(50) | BCPAO |
| ZW-002 | county | VARCHAR(50) | BCPAO |
| ZW-003 | address | VARCHAR(255) | BCPAO |
| ZW-004 | city | VARCHAR(100) | BCPAO |
| ZW-005 | zip_code | VARCHAR(10) | BCPAO |
| ZW-006 | state | VARCHAR(2) | BCPAO |
| ZW-007 | legal_description | TEXT | BCPAO |
| ZW-008 | subdivision | VARCHAR(255) | BCPAO |
| ZW-009 | property_type | VARCHAR(50) | BCPAO |
| ZW-010 | land_use_code | VARCHAR(20) | BCPAO |
| ZW-011 | owner_name | VARCHAR(255) | BCPAO |
| ZW-012 | owner_address | VARCHAR(255) | BCPAO |

---

### Category 2: Zoning & Land Use (62 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-013 | zone_code | VARCHAR(20) | Municode |
| ZW-014 | zone_name | VARCHAR(100) | Municode |
| ZW-015 | zone_description | TEXT | Municode |
| ZW-016 | zone_category | VARCHAR(50) | Municode |
| ZW-017 | zone_subcategory | VARCHAR(50) | Municode |
| ZW-018 | overlay_districts | TEXT[] | GIS |
| ZW-019 | special_districts | TEXT[] | GIS |
| ZW-020 | zone_effective_date | DATE | Municode |
| ZW-021 | flum_designation | VARCHAR(50) | Comp Plan |
| ZW-022 | comp_plan_consistent | BOOLEAN | Analysis |
| ZW-023 | min_lot_size_sqft | INTEGER | Municode |
| ZW-024 | min_lot_width_ft | INTEGER | Municode |
| ZW-025 | min_lot_depth_ft | INTEGER | Municode |
| ZW-026 | max_lot_coverage_pct | DECIMAL | Municode |
| ZW-027 | max_impervious_pct | DECIMAL | Municode |
| ZW-028 | front_setback_ft | INTEGER | Municode |
| ZW-029 | side_setback_ft | INTEGER | Municode |
| ZW-030 | rear_setback_ft | INTEGER | Municode |
| ZW-031 | corner_setback_ft | INTEGER | Municode |
| ZW-032 | waterfront_setback_ft | INTEGER | Municode |
| ZW-033 | max_building_height_ft | INTEGER | Municode |
| ZW-034 | max_stories | INTEGER | Municode |
| ZW-035 | floor_area_ratio | DECIMAL | Municode |
| ZW-036 | open_space_pct | DECIMAL | Municode |
| ZW-037 | permitted_uses | TEXT[] | Municode |
| ZW-038 | permitted_uses_count | INTEGER | Derived |
| ZW-039 | conditional_uses | TEXT[] | Municode |
| ZW-040 | conditional_uses_count | INTEGER | Derived |
| ZW-041 | prohibited_uses | TEXT[] | Municode |
| ZW-042 | accessory_uses | TEXT[] | Municode |
| ZW-043 | home_occupation_allowed | BOOLEAN | Municode |
| ZW-044 | short_term_rental_allowed | BOOLEAN | Municode |
| ZW-045 | adu_allowed | BOOLEAN | Municode |
| ZW-046 | adu_max_size_sqft | INTEGER | Municode |
| ZW-047 | commercial_uses_allowed | BOOLEAN | Municode |
| ZW-048 | mixed_use_allowed | BOOLEAN | Municode |
| ZW-049 | max_units_per_acre | DECIMAL | Municode |
| ZW-050 | min_unit_size_sqft | INTEGER | Municode |
| ZW-051 | max_units_per_lot | INTEGER | Municode |
| ZW-052 | max_building_size_sqft | INTEGER | Municode |
| ZW-053 | density_bonus_available | BOOLEAN | Municode |
| ZW-054 | density_bonus_pct | DECIMAL | Municode |
| ZW-055 | flum_max_density | DECIMAL | Comp Plan |
| ZW-056 | flum_max_intensity | DECIMAL | Comp Plan |
| ZW-057 | parking_min_residential | DECIMAL | Municode |
| ZW-058 | parking_min_commercial | DECIMAL | Municode |
| ZW-059 | parking_space_size_sqft | INTEGER | Municode |
| ZW-060 | parking_setback_ft | INTEGER | Municode |
| ZW-061 | shared_parking_allowed | BOOLEAN | Municode |
| ZW-062 | ev_charging_required | BOOLEAN | Municode |
| ZW-063 | bicycle_parking_required | BOOLEAN | Municode |
| ZW-064 | parking_requirements_json | JSONB | Municode |
| ZW-065 | site_plan_required | BOOLEAN | Municode |
| ZW-066 | variance_eligible | BOOLEAN | Municode |
| ZW-067 | rezoning_eligible | BOOLEAN | Municode |
| ZW-068 | building_permit_timeline | VARCHAR(50) | Historical |
| ZW-069 | site_plan_timeline | VARCHAR(50) | Historical |
| ZW-070 | rezoning_timeline | VARCHAR(50) | Historical |
| ZW-071 | development_agreement | BOOLEAN | Municode |
| ZW-072 | impact_fee_district | VARCHAR(50) | County |
| ZW-073 | concurrency_status | VARCHAR(50) | County |
| ZW-074 | ordinance_section_ref | VARCHAR(100) | Municode |

---

### Category 3: Auction Information (18 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-075 | case_number | VARCHAR(50) | RealForeclose |
| ZW-076 | auction_date | DATE | RealForeclose |
| ZW-077 | auction_time | TIME | RealForeclose |
| ZW-078 | auction_type | VARCHAR(50) | RealForeclose |
| ZW-079 | sale_status | VARCHAR(50) | RealForeclose |
| ZW-080 | plaintiff_name | VARCHAR(255) | RealForeclose |
| ZW-081 | plaintiff_type | VARCHAR(50) | Derived |
| ZW-082 | defendant_name | VARCHAR(255) | RealForeclose |
| ZW-083 | attorney_name | VARCHAR(255) | RealForeclose |
| ZW-084 | attorney_phone | VARCHAR(20) | RealForeclose |
| ZW-085 | filing_date | DATE | Clerk |
| ZW-086 | judgment_date | DATE | Clerk |
| ZW-087 | certificate_of_title | VARCHAR(100) | Clerk |
| ZW-088 | auction_location | VARCHAR(255) | RealForeclose |
| ZW-089 | online_bidding_url | VARCHAR(255) | RealForeclose |
| ZW-090 | postponement_count | INTEGER | RealForeclose |
| ZW-091 | cancellation_date | DATE | RealForeclose |
| ZW-092 | clerk_url | VARCHAR(255) | Clerk |

---

### Category 4: Financial Metrics (22 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-093 | opening_bid | DECIMAL | RealForeclose |
| ZW-094 | final_judgment | DECIMAL | Clerk |
| ZW-095 | per_diem | DECIMAL | Clerk |
| ZW-096 | attorney_fees | DECIMAL | Clerk |
| ZW-097 | court_costs | DECIMAL | Clerk |
| ZW-098 | total_due | DECIMAL | Derived |
| ZW-099 | assessed_value_land | DECIMAL | BCPAO |
| ZW-100 | assessed_value_building | DECIMAL | BCPAO |
| ZW-101 | total_assessed_value | DECIMAL | BCPAO |
| ZW-102 | market_value | DECIMAL | BCPAO |
| ZW-103 | arv_estimate | DECIMAL | ML Model |
| ZW-104 | arv_low | DECIMAL | ML Model |
| ZW-105 | arv_high | DECIMAL | ML Model |
| ZW-106 | repair_estimate | DECIMAL | ML Model |
| ZW-107 | holding_costs_estimate | DECIMAL | Calculation |
| ZW-108 | exit_costs_estimate | DECIMAL | Calculation |
| ZW-109 | annual_property_tax | DECIMAL | BCPAO |
| ZW-110 | hoa_fees_monthly | DECIMAL | Research |
| ZW-111 | insurance_estimate | DECIMAL | Calculation |
| ZW-112 | gross_profit_estimate | DECIMAL | Derived |
| ZW-113 | net_profit_estimate | DECIMAL | Derived |
| ZW-114 | roi_estimate | DECIMAL | Derived |

---

### Category 5: Liens & Encumbrances (20 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-115 | total_liens_count | INTEGER | AcclaimWeb |
| ZW-116 | total_liens_amount | DECIMAL | AcclaimWeb |
| ZW-117 | first_mortgage_amount | DECIMAL | AcclaimWeb |
| ZW-118 | first_mortgage_lender | VARCHAR(255) | AcclaimWeb |
| ZW-119 | first_mortgage_date | DATE | AcclaimWeb |
| ZW-120 | second_mortgage_amount | DECIMAL | AcclaimWeb |
| ZW-121 | second_mortgage_lender | VARCHAR(255) | AcclaimWeb |
| ZW-122 | hoa_lien_amount | DECIMAL | AcclaimWeb |
| ZW-123 | hoa_lien_holder | VARCHAR(255) | AcclaimWeb |
| ZW-124 | tax_lien_amount | DECIMAL | RealTDM |
| ZW-125 | tax_certificate_count | INTEGER | RealTDM |
| ZW-126 | code_violation_liens | DECIMAL | Clerk |
| ZW-127 | mechanics_liens | DECIMAL | AcclaimWeb |
| ZW-128 | judgment_liens | DECIMAL | AcclaimWeb |
| ZW-129 | irs_lien | BOOLEAN | AcclaimWeb |
| ZW-130 | irs_lien_amount | DECIMAL | AcclaimWeb |
| ZW-131 | senior_liens_total | DECIMAL | Derived |
| ZW-132 | junior_liens_total | DECIMAL | Derived |
| ZW-133 | liens_survive_sale | BOOLEAN | Analysis |
| ZW-134 | lien_priority_analysis | TEXT | Analysis |

---

### Category 6: ML Predictions (16 KPIs) ⭐ BIDDEED.AI EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-135 | third_party_probability | DECIMAL | XGBoost |
| ZW-136 | predicted_sale_price | DECIMAL | XGBoost |
| ZW-137 | prediction_confidence | DECIMAL | XGBoost |
| ZW-138 | model_version | VARCHAR(20) | System |
| ZW-139 | prediction_date | TIMESTAMP | System |
| ZW-140 | training_accuracy | DECIMAL | Model Metadata |
| ZW-141 | similar_cases_count | INTEGER | ML Model |
| ZW-142 | plaintiff_win_rate | DECIMAL | ML Model |
| ZW-143 | zip_code_third_party_rate | DECIMAL | Historical |
| ZW-144 | property_type_third_party_rate | DECIMAL | Historical |
| ZW-145 | judgment_range_third_party_rate | DECIMAL | Historical |
| ZW-146 | feature_importance_top_5 | JSONB | XGBoost |
| ZW-147 | shap_values | JSONB | XGBoost |
| ZW-148 | model_input_features | JSONB | XGBoost |
| ZW-149 | ensemble_score | DECIMAL | Multi-Model |
| ZW-150 | prediction_explanation | TEXT | XGBoost |

---

### Category 7: Physical Property (14 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-151 | year_built | INTEGER | BCPAO |
| ZW-152 | bedrooms | INTEGER | BCPAO |
| ZW-153 | bathrooms | DECIMAL | BCPAO |
| ZW-154 | half_baths | INTEGER | BCPAO |
| ZW-155 | living_sqft | INTEGER | BCPAO |
| ZW-156 | lot_size_sqft | INTEGER | BCPAO |
| ZW-157 | lot_size_acres | DECIMAL | Derived |
| ZW-158 | stories | INTEGER | BCPAO |
| ZW-159 | garage_spaces | INTEGER | BCPAO |
| ZW-160 | pool | BOOLEAN | BCPAO |
| ZW-161 | construction_type | VARCHAR(50) | BCPAO |
| ZW-162 | roof_type | VARCHAR(50) | BCPAO |
| ZW-163 | foundation_type | VARCHAR(50) | BCPAO |
| ZW-164 | photo_url | VARCHAR(255) | BCPAO |

---

### Category 8: Investment Scoring (12 KPIs) ⭐ BIDDEED.AI EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-165 | max_bid_amount | DECIMAL | Shapira Formula™ |
| ZW-166 | bid_judgment_ratio | DECIMAL | Derived |
| ZW-167 | recommendation | VARCHAR(10) | Decision Engine |
| ZW-168 | recommendation_confidence | DECIMAL | Decision Engine |
| ZW-169 | risk_score | INTEGER | Risk Engine |
| ZW-170 | opportunity_score | INTEGER | Opportunity Engine |
| ZW-171 | investment_grade | VARCHAR(2) | Composite |
| ZW-172 | estimated_profit | DECIMAL | Calculation |
| ZW-173 | estimated_roi | DECIMAL | Calculation |
| ZW-174 | time_to_exit_days | INTEGER | ML Model |
| ZW-175 | exit_strategy | VARCHAR(50) | Analysis |
| ZW-176 | quality_flags | TEXT[] | Analysis |

---

### Category 9: Demographics (14 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-177 | census_tract | VARCHAR(20) | Census API |
| ZW-178 | median_household_income | DECIMAL | Census API |
| ZW-179 | median_home_value | DECIMAL | Census API |
| ZW-180 | median_rent | DECIMAL | Census API |
| ZW-181 | population | INTEGER | Census API |
| ZW-182 | population_density | DECIMAL | Census API |
| ZW-183 | poverty_rate | DECIMAL | Census API |
| ZW-184 | unemployment_rate | DECIMAL | Census API |
| ZW-185 | owner_occupied_pct | DECIMAL | Census API |
| ZW-186 | vacancy_rate | DECIMAL | Census API |
| ZW-187 | median_age | DECIMAL | Census API |
| ZW-188 | college_educated_pct | DECIMAL | Census API |
| ZW-189 | population_growth_yoy | DECIMAL | Census API |
| ZW-190 | income_percentile_fl | INTEGER | Derived |

---

### Category 10: Market Analysis (14 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-191 | walk_score | INTEGER | Walk Score API |
| ZW-192 | transit_score | INTEGER | Walk Score API |
| ZW-193 | bike_score | INTEGER | Walk Score API |
| ZW-194 | school_score | INTEGER | GreatSchools |
| ZW-195 | crime_score | INTEGER | CrimeMapping |
| ZW-196 | days_on_market_avg | INTEGER | MLS Data |
| ZW-197 | price_per_sqft_area | DECIMAL | MLS Data |
| ZW-198 | appreciation_yoy | DECIMAL | Zillow |
| ZW-199 | inventory_months | DECIMAL | MLS Data |
| ZW-200 | foreclosure_rate_area | DECIMAL | Historical |
| ZW-201 | rental_demand_score | INTEGER | Rentometer |
| ZW-202 | investor_activity_score | INTEGER | Historical |
| ZW-203 | market_trend | VARCHAR(20) | Analysis |
| ZW-204 | market_cycle_position | VARCHAR(20) | Analysis |

---

### Category 11: Comparable Sales (16 KPIs)
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-205 | comp_count | INTEGER | MLS/BCPAO |
| ZW-206 | comp_1_address | VARCHAR(255) | MLS/BCPAO |
| ZW-207 | comp_1_sale_price | DECIMAL | MLS/BCPAO |
| ZW-208 | comp_1_sale_date | DATE | MLS/BCPAO |
| ZW-209 | comp_1_sqft | INTEGER | MLS/BCPAO |
| ZW-210 | comp_1_price_per_sqft | DECIMAL | Derived |
| ZW-211 | comp_1_distance_miles | DECIMAL | Calculation |
| ZW-212 | comp_1_similarity_score | DECIMAL | ML Model |
| ZW-213 | comp_2_address | VARCHAR(255) | MLS/BCPAO |
| ZW-214 | comp_2_sale_price | DECIMAL | MLS/BCPAO |
| ZW-215 | comp_3_address | VARCHAR(255) | MLS/BCPAO |
| ZW-216 | comp_3_sale_price | DECIMAL | MLS/BCPAO |
| ZW-217 | avg_comp_price_per_sqft | DECIMAL | Derived |
| ZW-218 | median_comp_sale_price | DECIMAL | Derived |
| ZW-219 | arv_from_comps | DECIMAL | Calculation |
| ZW-220 | comp_adjustment_notes | TEXT | Analysis |

---

### Category 12: HBU Analysis (12 KPIs) ⭐ ZONEWISE EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-221 | hbu_current_use | VARCHAR(100) | Analysis |
| ZW-222 | hbu_highest_use | VARCHAR(100) | HBU Engine |
| ZW-223 | hbu_legally_permissible | BOOLEAN | Zoning Analysis |
| ZW-224 | hbu_physically_possible | BOOLEAN | Site Analysis |
| ZW-225 | hbu_financially_feasible | BOOLEAN | Pro Forma |
| ZW-226 | hbu_maximally_productive | BOOLEAN | ROI Analysis |
| ZW-227 | hbu_score | INTEGER | Composite |
| ZW-228 | hbu_alternative_uses | TEXT[] | Analysis |
| ZW-229 | hbu_value_as_improved | DECIMAL | Calculation |
| ZW-230 | hbu_value_as_vacant | DECIMAL | Calculation |
| ZW-231 | hbu_premium_potential | DECIMAL | Derived |
| ZW-232 | hbu_recommendation | TEXT | HBU Engine |

---

### Category 13: CMA Deep Analysis (16 KPIs) ⭐ ZONEWISE EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-233 | cma_subject_condition | VARCHAR(50) | Analysis |
| ZW-234 | cma_market_conditions | VARCHAR(50) | Analysis |
| ZW-235 | cma_location_adjustment | DECIMAL | Calculation |
| ZW-236 | cma_condition_adjustment | DECIMAL | Calculation |
| ZW-237 | cma_size_adjustment | DECIMAL | Calculation |
| ZW-238 | cma_age_adjustment | DECIMAL | Calculation |
| ZW-239 | cma_feature_adjustments | JSONB | Calculation |
| ZW-240 | cma_total_adjustments | DECIMAL | Sum |
| ZW-241 | cma_adjusted_value | DECIMAL | Calculation |
| ZW-242 | cma_confidence_score | DECIMAL | Analysis |
| ZW-243 | cma_value_range_low | DECIMAL | Statistical |
| ZW-244 | cma_value_range_high | DECIMAL | Statistical |
| ZW-245 | cma_reconciled_value | DECIMAL | Analysis |
| ZW-246 | cma_appraiser_notes | TEXT | Analysis |
| ZW-247 | cma_comparable_quality | VARCHAR(50) | Analysis |
| ZW-248 | cma_market_time | INTEGER | Analysis |

---

### Category 14: Risk Assessment (10 KPIs) ⭐ BIDDEED.AI EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-249 | title_defect_risk | INTEGER | Analysis |
| ZW-250 | environmental_risk | INTEGER | Research |
| ZW-251 | structural_risk | INTEGER | Photos/History |
| ZW-252 | legal_complexity_risk | INTEGER | Case Analysis |
| ZW-253 | eviction_risk | INTEGER | Occupancy Check |
| ZW-254 | market_timing_risk | INTEGER | Market Analysis |
| ZW-255 | financing_risk | INTEGER | Condition |
| ZW-256 | regulatory_risk | INTEGER | Zoning Analysis |
| ZW-257 | composite_risk_score | INTEGER | Weighted Avg |
| ZW-258 | risk_mitigation_notes | TEXT | Analysis |

---

### Category 15: Red Flags (6 KPIs) ⭐ BIDDEED.AI EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-259 | hoa_foreclosure_warning | BOOLEAN | Plaintiff Analysis |
| ZW-260 | senior_lien_survives | BOOLEAN | Lien Priority |
| ZW-261 | title_defect_detected | BOOLEAN | Title Search |
| ZW-262 | bankruptcy_filed | BOOLEAN | Case Search |
| ZW-263 | multiple_defendants | BOOLEAN | Case Analysis |
| ZW-264 | do_not_bid_flag | BOOLEAN | Composite |

---

### Category 16: Development Process (16 KPIs) ⭐ ZONEWISE EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-265 | site_plan_required | BOOLEAN | Municode |
| ZW-266 | site_plan_timeline_days | INTEGER | Historical |
| ZW-267 | building_permit_timeline_days | INTEGER | Historical |
| ZW-268 | rezoning_required | BOOLEAN | Analysis |
| ZW-269 | rezoning_probability | DECIMAL | Historical |
| ZW-270 | variance_required | BOOLEAN | Analysis |
| ZW-271 | variance_type | VARCHAR(50) | Analysis |
| ZW-272 | impact_fees_estimate | DECIMAL | County |
| ZW-273 | connection_fees_estimate | DECIMAL | Utility |
| ZW-274 | permit_fees_estimate | DECIMAL | County |
| ZW-275 | total_soft_costs_estimate | DECIMAL | Derived |
| ZW-276 | entitlement_risk_score | INTEGER | Analysis |
| ZW-277 | approval_body | VARCHAR(100) | Municode |
| ZW-278 | public_hearing_required | BOOLEAN | Municode |
| ZW-279 | neighbor_notification_required | BOOLEAN | Municode |
| ZW-280 | appeal_deadline_days | INTEGER | Municode |

---

### Category 17: Environmental (18 KPIs) ⭐ ZONEWISE EXCLUSIVE
| Code | Name | Data Type | Source |
|------|------|-----------|--------|
| ZW-281 | flood_zone | VARCHAR(10) | FEMA |
| ZW-282 | flood_zone_description | VARCHAR(100) | FEMA |
| ZW-283 | flood_insurance_required | BOOLEAN | FEMA |
| ZW-284 | base_flood_elevation | DECIMAL | FEMA |
| ZW-285 | wetland_present | BOOLEAN | NWI |
| ZW-286 | wetland_acreage | DECIMAL | NWI |
| ZW-287 | wetland_setback_required | INTEGER | SJRWMD |
| ZW-288 | coastal_construction_zone | BOOLEAN | DEP |
| ZW-289 | cccl_setback_ft | INTEGER | DEP |
| ZW-290 | sea_level_rise_exposure | VARCHAR(50) | Analysis |
| ZW-291 | contamination_history | BOOLEAN | EPA/DEP |
| ZW-292 | brownfield_designation | BOOLEAN | EPA |
| ZW-293 | protected_species_habitat | BOOLEAN | FWC |
| ZW-294 | tree_preservation_required | BOOLEAN | Municode |
| ZW-295 | stormwater_requirements | TEXT | County |
| ZW-296 | environmental_permit_required | BOOLEAN | Analysis |
| ZW-297 | phase_1_recommended | BOOLEAN | Analysis |
| ZW-298 | environmental_risk_score | INTEGER | Composite |

---

## KPI Summary by Competitive Position

| Source | KPI Count | Competitive Status |
|--------|-----------|-------------------|
| **PropertyOnion Replicated** | 96 | ✅ Parity achieved |
| **BidDeed.AI Exclusive** | 74 | 🏆 Competitive advantage |
| **ZoneWise Exclusive** | 128 | 🏆 Unique differentiator |
| **TOTAL** | **298** | **3x PropertyOnion** |

---

## Decision Formula Integration

The 298 KPIs feed into our composite scoring:

```
COMPOSITE SCORE = HBU (30%) + CMA (30%) + ML (40%)

Where:
- HBU Score: ZW-221 to ZW-232 (12 KPIs)
- CMA Score: ZW-233 to ZW-248 (16 KPIs)
- ML Score: ZW-135 to ZW-150 (16 KPIs)

Final Output: ZW-167 (recommendation: BID/REVIEW/SKIP)
```

---

## UI Integration Map

| UI Panel | KPI Categories | KPI Codes |
|----------|----------------|-----------|
| **Property Card** | Property, Physical | ZW-001 to ZW-012, ZW-151 to ZW-164 |
| **Analysis Tab** | Financial, ML, Scoring | ZW-093 to ZW-114, ZW-135 to ZW-176 |
| **Liens Tab** | Liens, Red Flags | ZW-115 to ZW-134, ZW-259 to ZW-264 |
| **Zoning Tab** | Zoning & Land Use | ZW-013 to ZW-074 |
| **Comps Tab** | Comparable Sales, CMA | ZW-205 to ZW-248 |
| **Demographics Tab** | Demographics, Market | ZW-177 to ZW-204 |
| **HBU Tab** | HBU Analysis | ZW-221 to ZW-232 |
| **Development Tab** | Development, Environmental | ZW-265 to ZW-298 |
| **Mapbox Heatmap** | Market, Demographics | ZW-178, ZW-186, ZW-198, ZW-200 |

---

## NLP Chatbot Access

```python
class ZoneWiseChatbot:
    """NLP interface to all 298 KPIs"""
    
    KPI_CATEGORIES = {
        "property": "ZW-001 to ZW-012",
        "zoning": "ZW-013 to ZW-074",
        "auction": "ZW-075 to ZW-092",
        "financial": "ZW-093 to ZW-114",
        "liens": "ZW-115 to ZW-134",
        "ml_predictions": "ZW-135 to ZW-150",
        "physical": "ZW-151 to ZW-164",
        "investment": "ZW-165 to ZW-176",
        "demographics": "ZW-177 to ZW-190",
        "market": "ZW-191 to ZW-204",
        "comps": "ZW-205 to ZW-220",
        "hbu": "ZW-221 to ZW-232",
        "cma": "ZW-233 to ZW-248",
        "risk": "ZW-249 to ZW-258",
        "red_flags": "ZW-259 to ZW-264",
        "development": "ZW-265 to ZW-280",
        "environmental": "ZW-281 to ZW-298"
    }
    
    EXAMPLE_QUERIES = [
        "What's the zoning for 123 Main St?",
        "Show me all 298 KPIs for this property",
        "What's the HBU analysis?",
        "Are there any red flags?",
        "What's the max bid using Shapira Formula?",
        "What liens survive the sale?",
        "What's the ML prediction for third-party purchase?"
    ]
```

---

## Competitive Comparison

| KPI Category | BidDeed/ZoneWise | PropertyOnion | Gridics | Zoneomics |
|--------------|------------------|---------------|---------|-----------|
| Property Identification | ✅ 12 | ✅ 10 | ✅ 8 | ✅ 6 |
| Zoning & Land Use | ✅ 62 | ❌ 0 | ✅ 45 | ✅ 52 |
| Auction Information | ✅ 18 | ✅ 16 | ❌ 0 | ❌ 0 |
| Financial Metrics | ✅ 22 | ✅ 18 | ⚠️ 5 | ❌ 0 |
| Liens Analysis | ✅ 20 | ✅ 12 | ❌ 0 | ❌ 0 |
| ML Predictions | ✅ 16 | ❌ 0 | ❌ 0 | ❌ 0 |
| HBU Analysis | ✅ 12 | ❌ 0 | ⚠️ 3 | ❌ 0 |
| CMA Deep | ✅ 16 | ❌ 0 | ❌ 0 | ❌ 0 |
| Risk Assessment | ✅ 10 | ⚠️ 5 | ❌ 0 | ❌ 0 |
| Environmental | ✅ 18 | ⚠️ 3 | ✅ 12 | ⚠️ 8 |
| **TOTAL** | **298** | **96** | **74** | **66** |

---

*This framework powers "Claude AI for Real Estate" - the most comprehensive property intelligence platform in the market.*
