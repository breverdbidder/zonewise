-- Migration 005: Create fl_parcels table for 10.8M Florida statewide parcel data
-- Source: FDOR Statewide Cadastral 2025 (ArcGIS Online)
-- Expected: ~10.8M rows, ~3.2GB storage

-- Drop existing table if schema needs update (safe: this is a scrape-and-replace table)
DROP TABLE IF EXISTS fl_parcels;

CREATE TABLE fl_parcels (
    id BIGSERIAL PRIMARY KEY,
    co_no SMALLINT NOT NULL,
    parcel_id TEXT NOT NULL,
    dor_uc TEXT,
    pa_uc TEXT,
    jv BIGINT,
    jv_chng BIGINT,
    av_sd BIGINT,
    av_nsd BIGINT,
    tv_sd BIGINT,
    tv_nsd BIGINT,
    jv_hmstd BIGINT,
    av_hmstd BIGINT,
    jv_non_hms BIGINT,
    av_non_hms BIGINT,
    lnd_val BIGINT,
    lnd_unts_c TEXT,
    no_lnd_unt REAL,
    lnd_sqfoot BIGINT,
    eff_yr_blt SMALLINT,
    act_yr_blt SMALLINT,
    tot_lvg_ar INTEGER,
    no_buldng SMALLINT,
    no_res_unt SMALLINT,
    imp_qual TEXT,
    const_clas TEXT,
    sale_prc1 BIGINT,
    sale_yr1 SMALLINT,
    sale_mo1 SMALLINT,
    qual_cd1 TEXT,
    own_name TEXT,
    own_addr1 TEXT,
    own_addr2 TEXT,
    own_city TEXT,
    own_state TEXT,
    own_zipcd TEXT,
    phy_addr1 TEXT,
    phy_addr2 TEXT,
    phy_city TEXT,
    phy_zipcd TEXT,
    spec_feat_ BIGINT,
    grp_no TEXT,
    spass_cd TEXT,
    centroid_lat DOUBLE PRECISION,
    centroid_lng DOUBLE PRECISION,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(co_no, parcel_id)
);

-- Performance indexes
CREATE INDEX idx_fl_parcels_co_no ON fl_parcels(co_no);
CREATE INDEX idx_fl_parcels_parcel_id ON fl_parcels(parcel_id);
CREATE INDEX idx_fl_parcels_phy_city ON fl_parcels(phy_city);
CREATE INDEX idx_fl_parcels_phy_zipcd ON fl_parcels(phy_zipcd);
CREATE INDEX idx_fl_parcels_dor_uc ON fl_parcels(dor_uc);
CREATE INDEX idx_fl_parcels_jv ON fl_parcels(jv);
CREATE INDEX idx_fl_parcels_centroid ON fl_parcels(centroid_lat, centroid_lng);
CREATE INDEX idx_fl_parcels_sale_yr ON fl_parcels(sale_yr1);

-- RLS: public read, service role write
ALTER TABLE fl_parcels ENABLE ROW LEVEL SECURITY;

CREATE POLICY fl_parcels_read ON fl_parcels
    FOR SELECT USING (true);

CREATE POLICY fl_parcels_service_write ON fl_parcels
    FOR ALL USING (
        (current_setting('request.jwt.claims', true)::json->>'role') = 'service_role'
    );

COMMENT ON TABLE fl_parcels IS 'Florida statewide parcel data from FDOR Cadastral 2025. ~10.8M parcels across 67 counties with centroids.';
