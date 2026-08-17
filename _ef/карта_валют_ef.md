# E&F 04.07.2026 — карта валют

Разобрано из `common/goods/ef_00_goods.txt` и `common/history/global/99_ef_history_global_variable.txt`.

| | шт. |
|---|---:|
| товар есть и валюта кому-то назначена | 55 |
| **назначена, но товара нет (сломаны)** | **12** |
| товар есть, но никому не назначена | 10 |
| закомментирована и никому не назначена | 19 |
| назначена более чем одной стране | 6 |

**Активных валютных товаров: 65.** Всего товаров в игре с E&F: 126 (ваниль 53 + E&F 73).


## 1. Работают: товар есть, страна назначена (55)

| валюта | страны | название |
|---|---|---|
| `dinar_moroccan_dirham` | MOR | Moroccan Dirham |
| `dinar_qiran` | PER | Qiran |
| `dinar_serbian_dinar` | SER | Serbian Dinar |
| `dollar_australian_dollar` | AST, NSW | Australian Dollar |
| `dollar_canadian_dollar` | CAN, ONT, QUE | Canadian Dollar |
| `dollar_caribbean_dollar` | HAI | Caribbean Dollar |
| `dollar_confederate_states_dollar` | CSA | Confederate States Dollar |
| `dollar_new_zealand_dollar` | NZL | New Zealand Dollar |
| `dollar_united_states_dollar` | USA | United States Dollar |
| `eco_south_african_rand` | SAF | South African Rand |
| `franc_belgian_franc` | BEL | Belgian Franc |
| `franc_french_franc` | FRA | French Franc |
| `franc_swiss_franc` | SWI | Swiss Franc |
| `gulden` | AUS | Gulden |
| `gulden_bavarian_gulden` | BAV | Bavarian Gulden |
| `gulden_florin` | NET | Florin |
| `gulden_hungarian_forint` | HUN | Hungarian Forint |
| `krone_danish_krone` | DEN | Danish Krone |
| `krone_norwegian_krone` | NOR | Norwegian Krone |
| `krone_swedish_krona` | SWE | Swedish Krona |
| `leon_leu` | ROM | Leu |
| `leon_lev` | BUL | Lev |
| `lira` | ITA | Lira |
| `lira_ducato` | SIC | Ducato |
| `lira_ottoman_lira` | TUR | Ottoman Lira |
| `lira_scudo_pontificio` | PAP | Scudo Pontificio |
| `lira_scudo_sardo` | SAR | Scudo Sardo |
| `lira_toscane_lira` | TUS | Toscane Lira |
| `mark` | GER | Mark |
| `mark_finnish_markka` | FIN | Finnish Markka |
| `peso_argentine_peso` | ARG | Argentine Peso |
| `peso_bolivien_peso` | BOL, PBC | Peso Bolivien |
| `peso_chilean_peso` | CHL | Chilean Peso |
| `peso_colombian_peso` | CLM | Colombian Peso |
| `peso_cuban_peso` | CUB | Cuban Peso |
| `peso_mexican_peso` | ?, MEX | Mexican Peso |
| `peso_philippine_peso` | PHI | Philippine Peso |
| `peso_sol_de_oro` | PEU | Sol de Oro |
| `pound_egyptian_pound` | EGY | Egyptian Pound |
| `pound_sterling` | GBR | Pound Sterling |
| `real` | POR | Real |
| `real_brazilian_real` | BRZ | Brazilian Real |
| `rupee_indian_rupee` | BIC | Indian Rupee |
| `rupee_indonesian_rupiah` | DEI | Indonesian Rupiah |
| `spe_baht` | SIA | Baht |
| `spe_drachma` | GRE | Drachma |
| `spe_korean_won` | KOR | Korean Won |
| `spe_peseta` | SPA | Peseta |
| `spe_ruble` | RUS | Ruble |
| `spe_yen` | JAP | Yen |
| `spe_yuan` | ?, CHI | Yuan |
| `spe_zloti` | POL | Zloti |
| `thaler_hannoveraner_thaler` | HAN | Hannoveraner Thaler |
| `thaler_prussian_thaler` | NGF, PRU | Prussian Thaler |
| `thaler_saxon_thaler` | SAX | Saxon Thaler |

## 2. СЛОМАНЫ: закон выдаётся, товара нет (12)

Страна получает `activate_law`, но good закомментирован автором. Центробанк не может чеканить, ликвидность бесплатна.

| валюта | страны | название |
|---|---|---|
| `dollar_liberian_dollar` | LIB | Liberian Dollar |
| `gulden_south_german_gulde` | WUR |  |
| `peso_costa_rican_colon` | COS | Costa Rican Colon |
| `peso_ecuadorian_peso` | ECU | Ecuadorian Peso |
| `peso_el_salvador_colon` | ELS | El Salvador Colon |
| `peso_guatemalan_quetzal` | GUA | Guatemalan Quetzal |
| `peso_honduran_lempira` | HON | Honduran Lempira |
| `peso_nicaraguan_cordoba` | NIC | Nicaraguan Cordoba |
| `peso_paraguayan_peso` | PRG | Paraguayan Peso |
| `peso_uruguayan_peso` | URU | Uruguayan Peso |
| `peso_venezuelan_peso` | VNZ | Venezuelan Peso |
| `spe_dong` | DAI | Dong |

## 3. Ничейные: товар есть, никто не получает (10)

Кандидаты на вырезание — освобождают слот и никого не ломают.

| валюта | название | комментарий |
|---|---|---|
| `dinar` | Dinar | базовая generic-валюта |
| `dinar_tunisian_dinar` | Tunisian Dinar |  |
| `dinar_yugoslav_dinar` | Yugoslav Dinar |  |
| `eco_central_african_eco` | Central African Eco |  |
| `eco_east_african_eco` | East African Eco |  |
| `eco_west_african_eco` | West African Eco |  |
| `gulden_indies_guilder` | Indies Guilder |  |
| `gulden_south_german_gulden` | South German Gulden | не выдаётся только из-за опечатки `gulde` в истории |
| `peso` | Peso | базовая generic-валюта |
| `spe_uni` | Uni | **НЕ ТРОГАТЬ** — `default` у `popneed_currency` |

## 4. Назначены нескольким странам (6)

Штатная для мода ситуация: каждая страна чеканит товар сама через `pm_currency_*` у своего центробанка. В одном рынке предложение складывается.

| валюта | страны |
|---|---|
| `dollar_australian_dollar` | AST, NSW |
| `dollar_canadian_dollar` | CAN, ONT, QUE |
| `peso_bolivien_peso` | BOL, PBC |
| `peso_mexican_peso` | ?, MEX |
| `spe_yuan` | ?, CHI |
| `thaler_prussian_thaler` | NGF, PRU |

## 5. Вырезаны автором и никому не нужны (19)

Уже закомментированы в goods, `activate_law` не вызывается. Мёртвый груз: законы, PM, modifier types и переменные на них остались.

`dinar_algerian_dinar`, `dinar_iraqi_dinar`, `dinar_libyan_dinar`, `dinar_omanian_rial`, `dinar_saudi_riyal`, `dollar_sierra_leonean_dollar`, `eco_ariary`, `eco_ethiopian_birr`, `eco_ghanaian_pound`, `eco_nigerian_naira`, `eco_tuareg_ouguiya`, `franc_luxembourgish_franc`, `krone_czech_koruna`, `krone_estonian_kroon`, `krone_icelandic_krona`, `krone_slovak_koruna`, `pound_irish_pound`, `spe_latvian_lats`, `spe_lithuanian_litas`