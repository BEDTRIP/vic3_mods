# Megapack Internal Conflicts Report

- Megapack root: `/sessions/rcw-017nsstx3myg2nhohj7hh2ls/mnt/Projects/vic3_mods/__megapacks/megapack`

This report finds **duplicate identifiers** (same key/id defined multiple times within the megapack). It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 4 duplicates
- `building_airport` (defined in 2 files)
  - `common/buildings/zz_ef_mr_buildings_inject.txt`
  - `common/buildings/zztr_compatch_buildings.txt`
- `building_automotive_industry` (defined in 3 files)
  - `common/buildings/zz_tr_kai_tgr_buildings.txt`
  - `common/buildings/zztr_vanilla_buildings.txt`
  - `common/buildings/zzzz_megapack_tgr_industry_groups.txt`
- `building_manzoni_publishing_industry` (defined in 3 files)
  - `common/buildings/zz_ef_mr_buildings_inject.txt`
  - `common/buildings/zztr_compatch_buildings.txt`
  - `common/buildings/zzzz_megapack_mr_liquidity_reinject.txt`
- `building_synthetics_plant` (defined in 3 files)
  - `common/buildings/zz_tr_kai_tgr_buildings.txt`
  - `common/buildings/zztr_vanilla_buildings.txt`
  - `common/buildings/zzzz_megapack_tgr_industry_groups.txt`

### common/company_types — 98 duplicates
- `company_BancaCommercialeItaliana` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancaDItalia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCentralDeCostaRica` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCentralDeGuatemala` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCentralDeHonduras` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCentralDeVenezuela` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCentralDelUruguay` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCommercialDoBrasil` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoCommercialPortugues` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoDeBilbao` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoDeChile` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoDeMexico` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoDePortugal` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoDeValparaiso` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoDoBrasil` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoEspanolDeLaHabana` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoEstado` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoHipotecarioNacional` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoHispanoColonial` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoMercantil` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoMercantilMexicano` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoNacionArgentina` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoNacionalDeBolivia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoNacionalDePanama` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoNacionalDelParaguay` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoProvincia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BancoRepublicaColombia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankAmericanExpress` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankAngloPersian` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankBOCOM` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankCreditLyonnais` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankDesjardins` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankGoldmanSachs` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankHSBC` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankIBC` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankJPMorgan` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankMelliIran` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankOfBombay` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankOfIndiaCompany` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankOfJapan` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankOfMontreal` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankSBoBSA` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankTejaratPersia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankWellsFargo` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Bank_Ultramarino` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Bankenverein` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankofEngland` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BankofSpain` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BanqueDeBruxelles` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BanqueDeFrance` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BanqueDeParisEtDesPaysBas` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BanqueEgyptienne` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BanqueImperialeOttomane` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BanqueNationaleDeBelgique` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_BayerischeHypothekenUndWechselBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_CanadianImperialBankOfCommerce` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_CassaDiRisparmioDiTorino` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_ChaseBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_ChohungBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_ChristianiaBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_ColonialBankOfAustralia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_DaQingBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_DeNederlandscheBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_DeutscheBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_HandelsBanken` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_ImperialBankofIndia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_ImperialBankofPersia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_LandmandsBanken` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_LloydsBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Mitsubishiexchangehousebank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_NationalBankOfAustralia` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_NationalWestminsterBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_OesterreichischeCreditAnstalt` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_OesterreichischeNationalbank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_OttomanBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_PreussischeSeehandlung` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Reichsbank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Rothschild_Bank_aus` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Rothschild_Bank_fra` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Rothschild_Bank_gbr` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Rothschild_Bank_ger` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_Rothschild_Bank_ita` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_RotterdamscheBankvereeniging` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_RoyalBankOfScotland` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_RoyalBankofCanada` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_SocieteGenerale` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_SocieteGeneraledeBelgique` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_SouthAustralianBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_StateBankRussianEmpire` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_SumitomoBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_TurkishZiraatBankasi` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_WienerBankverein` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_amsterdamschebank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_bancodelondresmexico` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_bankofgreec` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `company_barclaysBank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `russo_chinese_bank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`
- `saint_petersburg_international_commercial_bank` (defined in 2 files)
  - `common/company_types/00_ef_companies.txt`
  - `common/company_types/zz_ef_cm_companies.txt`

### common/history/global — 1 duplicates
- `GLOBAL` (defined in 2 files)
  - `common/history/global/zz_ef_mr_stocks_init.txt`
  - `common/history/global/zzzz_ef_tr_fix_init.txt`

### common/on_actions — 1 duplicates
- `on_yearly_pulse_country` (defined in 2 files)
  - `common/on_actions/zz_ef_mr_on_actions.txt`
  - `common/on_actions/zzzz_ef_tr_fix_on_actions.txt`

### common/production_methods — 8 duplicates
- `pm_arc_welded_buildings` (defined in 2 files)
  - `common/production_methods/zz_pb_ef_construction_pm.txt`
  - `common/production_methods/zzz_PSC_TR_construction.txt`
- `pm_autonomous_and_remote_ops_building_gold_mine` (defined in 2 files)
  - `common/production_methods/zef_mines_production_methods.txt`
  - `common/production_methods/zzzz_ef_tr_fix_gold_minting.txt`
- `pm_diesel_pump_building_gold_mine` (defined in 2 files)
  - `common/production_methods/zef_mines_production_methods.txt`
  - `common/production_methods/zzzz_ef_tr_fix_gold_minting.txt`
- `pm_electric_fueled_pump_building_gold_mine` (defined in 2 files)
  - `common/production_methods/zef_mines_production_methods.txt`
  - `common/production_methods/zzzz_ef_tr_fix_gold_minting.txt`
- `pm_heavy_machineries_building_gold_mine` (defined in 2 files)
  - `common/production_methods/zef_mines_production_methods.txt`
  - `common/production_methods/zzzz_ef_tr_fix_gold_minting.txt`
- `pm_iron_frame_buildings` (defined in 2 files)
  - `common/production_methods/zz_pb_ef_construction_pm.txt`
  - `common/production_methods/zzz_PSC_TR_construction.txt`
- `pm_prefabricated_concrete_buildings` (defined in 2 files)
  - `common/production_methods/zzz_PSC_TR_construction.txt`
  - `common/production_methods/zzzz_megapack_concrete_stock.txt`
- `pm_steel_frame_buildings` (defined in 2 files)
  - `common/production_methods/zz_pb_ef_construction_pm.txt`
  - `common/production_methods/zzz_PSC_TR_construction.txt`

### common/script_values — 1 duplicates
- `calculate_state_construction_base_price` (defined in 2 files)
  - `common/script_values/z_PSC_TR_construction_values.txt`
  - `common/script_values/zz_pb_ef_psc_scope_fix.txt`

### common/technology/technologies — 1 duplicates
- `malaria_prevention` (defined in 3 files)
  - `common/technology/technologies/zz_tr_kai_tgr_technologies.txt`
  - `common/technology/technologies/zzz_compatch_mr_society.txt`
  - `common/technology/technologies/zzzz_megapack_malaria_prevention.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **35**
  - `concept_building_urban_center_lvl_by_base_rate_desc` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_l_english.yml`
    - `localization/french/zz_pb_ef_psc_l_french.yml`
    - `localization/german/zz_pb_ef_psc_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_l_japanese.yml`
    - ... and 6 more files
  - `concept_maximum_pcs_capacity_desc` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_l_english.yml`
    - `localization/french/zz_pb_ef_psc_l_french.yml`
    - `localization/german/zz_pb_ef_psc_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_l_japanese.yml`
    - ... and 6 more files
  - `concrete_construction` (in 10 files)
    - `localization/braz_por/PSC_TR_goods_l_braz_por.yml`
    - `localization/english/PSC_TR_goods_l_english.yml`
    - `localization/french/PSC_TR_goods_l_french.yml`
    - `localization/german/PSC_TR_goods_l_german.yml`
    - `localization/japanese/PSC_TR_goods_l_japanese.yml`
    - ... and 5 more files
  - `dlc_pbe` (in 11 files)
    - `localization/braz_por/zz_dlc_menu_icons_l_braz_por.yml`
    - `localization/english/zz_dlc_menu_icons_l_english.yml`
    - `localization/french/zz_dlc_menu_icons_l_french.yml`
    - `localization/german/zz_dlc_menu_icons_l_german.yml`
    - `localization/japanese/zz_dlc_menu_icons_l_japanese.yml`
    - ... and 6 more files
  - `dlc_pbe_desc` (in 11 files)
    - `localization/braz_por/zz_dlc_menu_icons_l_braz_por.yml`
    - `localization/english/zz_dlc_menu_icons_l_english.yml`
    - `localization/french/zz_dlc_menu_icons_l_french.yml`
    - `localization/german/zz_dlc_menu_icons_l_german.yml`
    - `localization/japanese/zz_dlc_menu_icons_l_japanese.yml`
    - ... and 6 more files
  - `dlc_psc` (in 11 files)
    - `localization/braz_por/zz_dlc_menu_icons_l_braz_por.yml`
    - `localization/english/zz_dlc_menu_icons_l_english.yml`
    - `localization/french/zz_dlc_menu_icons_l_french.yml`
    - `localization/german/zz_dlc_menu_icons_l_german.yml`
    - `localization/japanese/zz_dlc_menu_icons_l_japanese.yml`
    - ... and 6 more files
  - `dlc_psc_desc` (in 11 files)
    - `localization/braz_por/zz_dlc_menu_icons_l_braz_por.yml`
    - `localization/english/zz_dlc_menu_icons_l_english.yml`
    - `localization/french/zz_dlc_menu_icons_l_french.yml`
    - `localization/german/zz_dlc_menu_icons_l_german.yml`
    - `localization/japanese/zz_dlc_menu_icons_l_japanese.yml`
    - ... and 6 more files
  - `dlc_tgr` (in 11 files)
    - `localization/braz_por/zz_dlc_menu_icons_l_braz_por.yml`
    - `localization/english/zz_dlc_menu_icons_l_english.yml`
    - `localization/french/zz_dlc_menu_icons_l_french.yml`
    - `localization/german/zz_dlc_menu_icons_l_german.yml`
    - `localization/japanese/zz_dlc_menu_icons_l_japanese.yml`
    - ... and 6 more files
  - `dlc_tgr_desc` (in 11 files)
    - `localization/braz_por/zz_dlc_menu_icons_l_braz_por.yml`
    - `localization/english/zz_dlc_menu_icons_l_english.yml`
    - `localization/french/zz_dlc_menu_icons_l_french.yml`
    - `localization/german/zz_dlc_menu_icons_l_german.yml`
    - `localization/japanese/zz_dlc_menu_icons_l_japanese.yml`
    - ... and 6 more files
  - `economic_sentiment_index_base_1_button` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `economic_sentiment_index_base_3_button` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `economic_sentiment_index_base_5_button` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `financial_center_je_2_reason` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `financial_center_je_2_reason_2` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `goods_input_concrete_construction_add` (in 10 files)
    - `localization/braz_por/PSC_TR_modifiers_l_braz_por.yml`
    - `localization/english/PSC_TR_modifiers_l_english.yml`
    - `localization/french/PSC_TR_modifiers_l_french.yml`
    - `localization/german/PSC_TR_modifiers_l_german.yml`
    - `localization/japanese/PSC_TR_modifiers_l_japanese.yml`
    - ... and 5 more files
  - `goods_input_concrete_construction_add_desc` (in 10 files)
    - `localization/braz_por/PSC_TR_modifiers_l_braz_por.yml`
    - `localization/english/PSC_TR_modifiers_l_english.yml`
    - `localization/french/PSC_TR_modifiers_l_french.yml`
    - `localization/german/PSC_TR_modifiers_l_german.yml`
    - `localization/japanese/PSC_TR_modifiers_l_japanese.yml`
    - ... and 5 more files
  - `goods_output_concrete_construction_add` (in 10 files)
    - `localization/braz_por/PSC_TR_modifiers_l_braz_por.yml`
    - `localization/english/PSC_TR_modifiers_l_english.yml`
    - `localization/french/PSC_TR_modifiers_l_french.yml`
    - `localization/german/PSC_TR_modifiers_l_german.yml`
    - `localization/japanese/PSC_TR_modifiers_l_japanese.yml`
    - ... and 5 more files
  - `goods_output_concrete_construction_add_desc` (in 10 files)
    - `localization/braz_por/PSC_TR_modifiers_l_braz_por.yml`
    - `localization/english/PSC_TR_modifiers_l_english.yml`
    - `localization/french/PSC_TR_modifiers_l_french.yml`
    - `localization/german/PSC_TR_modifiers_l_german.yml`
    - `localization/japanese/PSC_TR_modifiers_l_japanese.yml`
    - ... and 5 more files
  - `pm_autonomous_and_remote_ops_building_gold_mine` (in 2 files)
    - `localization/english/zef_production_methods_mines_l_english.yml`
    - `localization/russian/zzzz_ef_tr_fix_l_russian.yml`
  - `pm_autonomous_and_remote_ops_building_silver_mine` (in 2 files)
    - `localization/english/zef_production_methods_mines_l_english.yml`
    - `localization/russian/zzzz_ef_tr_fix_l_russian.yml`
  - `pm_concrete_point_conversion` (in 10 files)
    - `localization/braz_por/PSC_TR_production_methods_l_braz_por.yml`
    - `localization/english/PSC_TR_production_methods_l_english.yml`
    - `localization/french/PSC_TR_production_methods_l_french.yml`
    - `localization/german/PSC_TR_production_methods_l_german.yml`
    - `localization/japanese/PSC_TR_production_methods_l_japanese.yml`
    - ... and 5 more files
  - `pm_electric_fueled_pump_building_gold_mine` (in 2 files)
    - `localization/english/zef_production_methods_mines_l_english.yml`
    - `localization/russian/zzzz_ef_tr_fix_l_russian.yml`
  - `pm_electric_fueled_pump_building_silver_mine` (in 2 files)
    - `localization/english/zef_production_methods_mines_l_english.yml`
    - `localization/russian/zzzz_ef_tr_fix_l_russian.yml`
  - `pm_heavy_machineries_building_gold_mine` (in 2 files)
    - `localization/english/zef_production_methods_mines_l_english.yml`
    - `localization/russian/zzzz_ef_tr_fix_l_russian.yml`
  - `pm_heavy_machineries_building_silver_mine` (in 2 files)
    - `localization/english/zef_production_methods_mines_l_english.yml`
    - `localization/russian/zzzz_ef_tr_fix_l_russian.yml`
  - `speculative_share_10_button_tt_effect_1_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `speculative_share_11_button_tt_effect_1_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `speculative_share_12_button_tt_effect_1_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `speculative_share_13_button_tt_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `speculative_share_13_button_tt_effect_1_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `speculative_share_9_button_tt_effect_1_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `speculative_share_modifier_7` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_je_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_je_l_english.yml`
    - `localization/french/zz_pb_ef_psc_je_l_french.yml`
    - `localization/german/zz_pb_ef_psc_je_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_je_l_japanese.yml`
    - ... and 6 more files
  - `state_building_construction_sector_max_level_add` (in 11 files)
    - `localization/braz_por/zz_ef_psc_modifiers_l_braz_por.yml`
    - `localization/english/zz_ef_psc_modifiers_l_english.yml`
    - `localization/french/zz_ef_psc_modifiers_l_french.yml`
    - `localization/german/zz_ef_psc_modifiers_l_german.yml`
    - `localization/japanese/zz_ef_psc_modifiers_l_japanese.yml`
    - ... and 6 more files
  - `state_building_construction_sector_max_level_add_desc` (in 11 files)
    - `localization/braz_por/zz_ef_psc_modifiers_l_braz_por.yml`
    - `localization/english/zz_ef_psc_modifiers_l_english.yml`
    - `localization/french/zz_ef_psc_modifiers_l_french.yml`
    - `localization/german/zz_ef_psc_modifiers_l_german.yml`
    - `localization/japanese/zz_ef_psc_modifiers_l_japanese.yml`
    - ... and 6 more files
  - `status_speculative_share_2_1` (in 11 files)
    - `localization/braz_por/zz_pb_ef_psc_l_braz_por.yml`
    - `localization/english/zz_pb_ef_psc_l_english.yml`
    - `localization/french/zz_pb_ef_psc_l_french.yml`
    - `localization/german/zz_pb_ef_psc_l_german.yml`
    - `localization/japanese/zz_pb_ef_psc_l_japanese.yml`
    - ... and 6 more files

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**

---

# Разбор: почему это конфликт / почему это не конфликт

Сверено 2026-08-24. Сборка: `__megapacks/megapack` — восемь компачей
(`ef+morg`, `ef+psc`, `ef+tgr`, `ef+tr+kai`, `morg+tr+kai`, `pbe+tgr`,
`psc+tr+kai`, `tgr+tr+kai`) плюс `dlc menu icons`.

Порядок файлов **внутри** мода — по имени. Везде ниже это и есть причина.

## Требуют работы — сделано

### `building_automotive_industry`, `building_synthetics_plant`
Два компача делают `REPLACE:` одних и тех же двух зданий, каждый по своей причине:

| файл | что несёт |
|---|---|
| `zz_tr_kai_tgr_buildings.txt` (TGR+T&R) | тело T&R + `building_group` от TGR |
| `zztr_vanilla_buildings.txt` (E&F+T&R, генерируемый) | тело T&R + две PM-группы E&F |

`zztr_` сортируется после `zz_tr_`, поэтому побеждает копия E&F+T&R и
`building_group` от TGR теряется. TGR заводит свои `bg_industry_heavy` /
`bg_industry_light` (дети `bg_manufacturing`) и через них ключует свой
промышленный декрет, законы экономических стимулов и `building_group_*`
модификаторы. `bg_heavy_industry` у T&R — группа-**сестра**, не родитель, так что
`is_building_group` до неё не дотягивается: оба здания молча выпадают из декрета
и законов TGR. В `error.log` при этом ничего нет — триггер не сломан, он просто
отвечает «нет».

**Решение:** `zzzz_megapack_tgr_industry_groups.txt` — тело из
`zztr_vanilla_buildings.txt` с заменённой одной строкой `building_group`.
`REPLACE:`, а не `INJECT:`, потому что `building_group` — скаляр: списка, в
который можно дописать, нет, а поведение `INJECT:` на скаляре в этом репозитории
в игре не проверялось. Полный `REPLACE:` корректен при любом прочтении того, как
1.13 применяет префиксы БД.

Цена решения та же, что и в компаче TGR+T&R: бонусы T&R
`building_group_bg_heavy_industry_throughput_add` (законы экологической политики,
две автомобильные компании; ±0.01…0.02) до этих двух зданий больше не доходят.

### `malaria_prevention`
T&R делает `REPLACE_OR_CREATE:` всей технологии, поэтому каждый компач, который
возвращает свою строку в блок `modifier`, вынужден переписывать запись целиком —
и выживает только последний файл:

* `zz_tr_kai_tgr_technologies.txt` (TGR+T&R) возвращает TGR-овский
  `country_institution_environment_max_investment_add = 1`;
* `zzz_compatch_mr_society.txt` (MR+T&R) возвращает морген-ротовский
  `state_harvest_condition_panum_yellow_fever_condition_impact_mult = -0.25`.

`zz_tr_` идёт раньше `zzz_`, значит в сборке побеждает морген-ротовский патч, а
строка TGR пропадает: институт Environment у TGR упирается в потолок на один
уровень инвестиций ниже задуманного. Симптом молчаливый — модификатор не
отсутствует и не написан с ошибкой, он просто никогда не применяется.

**Решение:** `zzzz_megapack_malaria_prevention.txt` — тело морген-ротовского
патча плюс строка TGR. Тела двух патчей в остальном совпадают, сверено построчно.

### `building_manzoni_publishing_industry` и `pm_prefabricated_concrete_buildings`
Разобраны в шапках `zzzz_megapack_mr_liquidity_reinject.txt` и
`zzzz_megapack_concrete_stock.txt`. Перенесены из сборки no-TGR без изменений —
TGR ни то, ни другое не трогает.

## Не конфликты

| Группа | Почему |
|---|---|
| `common/company_types`, 98 банков | Не конфликт компачей, а штатная конструкция `ef+psc`: `zz_ef_cm_companies.txt` — это `INJECT:` хотфикса поверх собственной копии списка E&F в `00_ef_companies.txt`. Внутри мода `zz_` ложится на `00_`. Разобрано в шапке файла. |
| `GLOBAL`, `BUILDINGS`, `on_yearly_pulse_country`, `on_monthly_pulse_country` | Аддитивные категории 1.13. Несколько определений складываются, не перекрывают. |
| `building_airport` | `TRY_INJECT:` (E&F+MR) и `INJECT:` (MR+T&R) — оба добавляют группы, ничего не убирают. |
| `pm_iron_frame_buildings`, `pm_steel_frame_buildings`, `pm_arc_welded_buildings` | `zz_pb_ef_construction_pm.txt` (`REPLACE:`) грузится раньше `zzz_PSC_TR_construction.txt` (`INJECT:`) — порядок правильный сам собой. |
| Золотые рудники, 4 PM | `zef_mines_production_methods.txt` и `zzzz_ef_tr_fix_gold_minting.txt` — оба из компача-замены E&F+T&R, второй `INJECT:`-ит чеканку в первый. По имени попадает после. |
| `calculate_state_construction_base_price` | `z_PSC_TR_construction_values.txt` vs `zz_pb_ef_psc_scope_fix.txt` — мердж уже сделан в megapack-версии второго файла: лестница из пяти ступеней от PSC+T&R, гард `has_building` от E&F+PSC. |
| 35 «дублей» локализации в отчёте выше | Ложные срабатывания: скрипт не различает языковые папки. Проверка по каждой папке `localization/<язык>/` отдельно — 0 дублей. |

## Пересечения сборки с самими модами (не только внутри сборки)

`scan_conflicts.py --a megapack --b TheGreatRevision`: 43 общих ключа. Все, кроме
одного, — это то, ради чего компачи и написаны (кнопки и журнал займов TGR,
`base_values`, технологии через `INJECT:`, товары, законы, PM портов и железных
дорог, `force_regime_change`, `NEconomy.PRICE_RANGE`).

Единственный, который стоит назвать явно, — **`building_construction_sector`**.
Его переопределяют и TGR (`REPLACE_OR_CREATE:`), и сборка
(`zz_pb_ef_construction_sector.txt`, из `ef+psc`). Это **не** новая развилка:
PSC грузится после TGR и выигрывает и без сборки — ровно поэтому пара
`psc+tgr` помечена `noneed`. Файл сборки — это копия `REPLACE:` от PSC с
добавками E&F, то есть сборка воспроизводит ровно тот же исход, что и связка
PSC+TGR без неё. Ничего мерджить не требуется.

Оговорка оттуда же остаётся в силе: PSC (и, следовательно, этот файл) не
упоминает `has_max_level`, который есть в ванили и в TGR. Наследуется он или
теряется — зависит от того, патчит ли `REPLACE:` по под-блокам или заменяет
запись целиком, а по этому вопросу записи в репозитории противоречат друг другу
(см. ниже). Симптом, если что-то не так, однозначный: построенный
`building_construction_sector` не расширяется выше 1 уровня.

Пути файлов пересекаются со сборкой только там, где это задумано:
`gui/budget_panel.gui` (TGR и E&F — трёхсторонний мердж из `ef+tgr`),
`common/company_types/00_ef_companies.txt`, `zz_ef_cm_companies.txt` и
`common/history/buildings/00_ef_building.txt` (E&F и хотфикс — генерируемые копии
из `ef+psc`, разобрано в их шапках). С MR, PSC, PBE, T&R и KAI — ноль пересечений
по путям.

## `REPLACE:` патчит по под-блокам — закрыто 24.08.2026

Две записи в репозитории от 21.08.2026 описывали `REPLACE:` по-разному. Решение
принято: **`REPLACE:` патчит по перечисленным под-блокам, а не заменяет запись
целиком.** Отсюда следует, что `ef_tgr_company_hq_pm_compat.txt` удалён верно
(`REPLACE:` у E&F перечисляет только `building_modifiers`, `state_modifiers` от
TGR выживает сам), и что `zz_disable_tgr_international_loans_buttons.txt` со
своими `REPLACE_OR_CREATE:tgr_loans_button_N = { visible possible }` работает
именно потому, что остальное тело кнопки остаётся на месте.

На саму сборку это не влияет: все четыре megapack-only файла используют либо
`INJECT:`, либо `REPLACE:` с полным телом — корректно при любом прочтении.
Шапка `zzzz_ef_tr_fix_gold_minting.txt` (в компаче-замене E&F+T&R) всё ещё
утверждает обратное со ссылкой на два наблюдения в игре 21.08.2026 — её стоит
перечитать отдельно, вместе с тем, нужен ли ещё сам файл.

## Займы TGR: модификатор убран, а не обнулён (24.08.2026)

`ef+tgr` выключает модуль International Loans (журнал `je_international_loans`,
кнопки `tgr_loans_button_1..8`). Его базовая ставка
`country_loan_interest_rate_add = -0.2` раньше «сбрасывалась» через
`INJECT:base_values = { country_loan_interest_rate_add = 0 }` — что ничего не
делало: повторяющиеся ключи внутри одного блока модификаторов складываются, и
`0 + (-0.2)` остаётся `-0.2`. Ванильные и E&F-займы всё это время выдавались
почти без процента, молча.

Теперь патч перекрывает по пути сам файл TGR
`common/static_modifiers/TGR_LOANS_code_static_modifiers.txt`, в котором лежит
ровно этот один `INJECT:` и больше ничего. Тот же путь есть в отдельном мини-моде
«TGR International Loans» — один файл закрывает оба. Контрвес `+0.2` был бы верен
только при сложении и ровно наоборот при перезаписи; `REPLACE:base_values`
запинил бы числа четырёх модов. Приём тот же, что в `stuff/anti_tgr_loans`.

Файл `ef_tgr_base_values_compat.txt` удалён из компача и из обеих сборок с TGR.

## Проверки сборки

* 178 файлов; баланс скобок по всем `.txt` — 0.
* BOM: есть везде, кроме семи файлов. Шесть — побайтовые копии чужого компача из
  компача-замены E&F+T&R, все чистый ASCII (BOM там ничего не меняет и сломал бы
  побайтовый дифф против чужого компача). Седьмой — `gui/budget_panel.gui`,
  не-ASCII в нём только в ASCII-арт комментариях, ни одной некомментарной строки.
* `.metadata/metadata.json` — без BOM, `json.loads` проходит.
* Локализация: 0 дублей внутри любой языковой папки.
* Товары: **106 из 128** (ваниль 53 + PSC 4 + E&F с хотфиксом 8 + MR 5 + T&R 35
  + `concrete_construction` 1; TGR своих товаров не добавляет). Запас 22.
* `gui/budget_panel.gui` — надмножество имён виджетов TGR и E&F. Против ванили не
  хватает трёх (`bankruptcy_progress_bar`, `bankruptcy_progressbar`,
  `declare_bankruptcy_button`), но их независимо убрали **оба** мода, так что
  восстанавливать нечего.
* Все файлы восьми компачей лежат в сборке побайтово, кроме задокументированных
  исключений: `zz_ef_mr_inflation_patch.txt`, `zztr_mr_buildings.txt` и
  `zztr_modified_mr_buildings.txt` не берутся вовсе; `zef_00_economic_scripted_value.txt`
  и `zz_pb_ef_psc_scope_fix.txt` — megapack-версии;
  `zz_ef_tgr_private_ownership_stock_l_*.yml` берётся из `ef+tgr` (новая
  урезанная версия), а не из `ef+morg` / `ef+psc` (старая).
