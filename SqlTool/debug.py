import re
from idlelib.colorizer import any
def make_pat():
        table="FROM|WHERE|;"

select='''SELECT a.id
FROM
    bpm_master_basic a,
    bpm_landing_product_basic b
WHERE
    a.product_code = b.product_code
        AND (IFNULL(a.english_product_description, '') <> IFNULL(b.english_product_description, '')
        OR IFNULL(a.old_item_code_product_description, '') <> IFNULL(b.old_item_code_product_description, '')
        OR IFNULL(a.quality_guaranteed, '') <> IFNULL(b.quality_guaranteed, '')
        OR IFNULL(a.base_unit_of_measure, '') <> IFNULL(b.base_unit_of_measure, '')
        OR IFNULL(a.old_barcode, '') <> IFNULL(b.old_barcode, '')
        OR IFNULL(a.item_barcode, '') <> IFNULL(b.item_barcode, '')
        OR IFNULL(a.inner_barcode, '') <> IFNULL(b.inner_barcode, '')
        OR IFNULL(a.bp_component_barcode, '') <> IFNULL(b.bp_component_barcode, '')
        OR IFNULL(a.shipper_barcode, '') <> IFNULL(b.shipper_barcode, '')
        OR IFNULL(a.su_factor_for_buom, '') <> IFNULL(b.su_factor_for_buom, '')
        OR IFNULL(a.su_factor_for_sales_unit_to_customer,
            '') <> IFNULL(b.su_factor_for_sales_unit_to_customer,
            '')
        OR IFNULL(a.case_count_item_case, '') <> IFNULL(b.case_count_item_case, '')
        OR IFNULL(a.bundle_pack_case, '') <> IFNULL(b.bundle_pack_case, '')
        OR IFNULL(a.item_bundle_pack, '') <> IFNULL(b.item_bundle_pack, '')
        OR IFNULL(a.inner_count_item_inner, '') <> IFNULL(b.inner_count_item_inner, '')
        OR IFNULL(a.inner_case, '') <> IFNULL(b.inner_case, '')
        OR IFNULL(a.outside_case_dimension_length, '') <> IFNULL(b.outside_case_dimension_length, '')
        OR IFNULL(a.outside_case_dimension_width, '') <> IFNULL(b.outside_case_dimension_width, '')
        OR IFNULL(a.outside_case_dimension_high, '') <> IFNULL(b.outside_case_dimension_high, '')
        OR IFNULL(a.case_volume, '') <> IFNULL(b.case_volume, '')
        OR IFNULL(a.inner_case_dimension_length, '') <> IFNULL(b.inner_case_dimension_length, '')
        OR IFNULL(a.inner_case_dimension_width, '') <> IFNULL(b.inner_case_dimension_width, '')
        OR IFNULL(a.inner_case_dimension_high, '') <> IFNULL(b.inner_case_dimension_high, '')
        OR IFNULL(a.inner_volume, '') <> IFNULL(b.inner_volume, '')
        OR IFNULL(a.item_dimension_length, '') <> IFNULL(b.item_dimension_length, '')
        OR IFNULL(a.item_dimension_width, '') <> IFNULL(b.item_dimension_width, '')
        OR IFNULL(a.item_dimension_high, '') <> IFNULL(b.item_dimension_high, '')
        OR IFNULL(a.gross_weight_kg_per_case, '') <> IFNULL(b.gross_weight_kg_per_case, '')
        OR IFNULL(a.jp_code_sk_only, '') <> IFNULL(b.jp_code_sk_only, '')
        OR IFNULL(a.bp_component_code, '') <> IFNULL(b.bp_component_code, '')
        OR IFNULL(a.item_code_bp_code, '') <> IFNULL(b.item_code_bp_code, '')
        OR IFNULL(a.local_import, '') <> IFNULL(b.local_import, '')
        OR IFNULL(a.old_bp_component_code, '') <> IFNULL(b.old_bp_component_code, '')
        OR IFNULL(a.cdh_category_en, '') <> IFNULL(b.cdh_category_en, '')
        OR IFNULL(a.cdh_full_category_cn, '') <> IFNULL(b.cdh_full_category_cn, '')
        OR IFNULL(a.category, '') <> IFNULL(b.category, '')
        OR IFNULL(a.brand, '') <> IFNULL(b.brand, '')
        OR IFNULL(a.item_status, '') <> IFNULL(b.item_status, '')
        OR IFNULL(a.sap_sos_date, '') <> IFNULL(b.sap_sos_date, '')
        OR IFNULL(a.discontinue_date, '') <> IFNULL(b.discontinue_date, '')
        OR IFNULL(a.internal_project_name, '') <> IFNULL(b.internal_project_name, '')
        OR IFNULL(a.variant, '') <> IFNULL(b.variant, '')
        OR IFNULL(a.sub_brand, '') <> IFNULL(b.sub_brand, '')
        OR IFNULL(a.sales_unit_to_customer, '') <> IFNULL(b.sales_unit_to_customer, '')
        OR IFNULL(a.sales_unit_to_consumer, '') <> IFNULL(b.sales_unit_to_consumer, '')
        OR IFNULL(a.sales_organization, '') <> IFNULL(b.sales_organization, '')
        OR IFNULL(a.distribution_channel, '') <> IFNULL(b.distribution_channel, '')
        OR IFNULL(a.selling_barcode, '') <> IFNULL(b.selling_barcode, '')
        OR IFNULL(a.product_form, '') <> IFNULL(b.product_form, '')
        OR IFNULL(a.net_weight_kg_per_case, '') <> IFNULL(b.net_weight_kg_per_case, '')
        OR IFNULL(a.product_plant, '') <> IFNULL(b.product_plant, '')
        OR IFNULL(a.cn_category, '') <> IFNULL(b.cn_category, '')
        OR IFNULL(a.cn_brand, '') <> IFNULL(b.cn_brand, '')
        OR IFNULL(a.sub_sector, '') <> IFNULL(b.sub_sector, '')
        OR IFNULL(a.item_status_code, '') <> IFNULL(b.item_status_code, '')
        OR IFNULL(a.repeat_item_barcode, '') <> IFNULL(b.repeat_item_barcode, '')
        OR IFNULL(a.pack_count, '') <> IFNULL(b.pack_count, '')
        OR IFNULL(a.sales_unit_to_consumer_code, '') <> IFNULL(b.sales_unit_to_consumer_code, '')
        OR IFNULL(a.cdh_brand_en, '') <> IFNULL(b.cdh_brand_en, '')
        OR IFNULL(a.cdh_sub_brand_en, '') <> IFNULL(b.cdh_sub_brand_en, '')
        OR IFNULL(a.cdh_product_form_en, '') <> IFNULL(b.cdh_product_form_en, '')
        OR IFNULL(a.cdh_variant_en, '') <> IFNULL(b.cdh_variant_en, '')
        OR IFNULL(a.cdh_category_code, '') <> IFNULL(b.cdh_category_code, '')
        OR IFNULL(a.same_barcode_price_json,'') <> IFNULL(b.same_barcode_price_json,'')
        ) ;
        '''

re.findall("SELECT .* FROM (.[^where]*)? [where]?",select,flags=re.I)
