let AN=null, FILTER="전체", PREVIEW=false;
const FALLBACK={"generated_at":"2026-09-26T17:16:44.621306+09:00","history_lookback_days":30,"history_used":1,"history_source":"실제 낙찰가 + 국토부 시세(매도가 추정)","market_stats":{"sold":1,"avg_ratio":95.9,"avg_bidders":12,"by_type":{"아파트":{"n":1,"avg_ratio":95.9}},"top":{"region":"경기 수원시","type":"아파트","ratio":95.9},"bottom":{"region":"경기 수원시","type":"아파트","ratio":95.9}},"assumptions":{"score_weights":{"liquidity":0.35,"margin":0.2,"sharpe":0.2,"rights":0.15,"win":0.1}},"properties":[{"id":"2024타경45678","court":"수원지방법원","address":"경기 수원시 영통구 이의동 000","region":"경기 수원시","type":"아파트","apt_name":"광교아이파크","exclusive_area":101.2,"floor":18,"total_floors":29,"built_year":2018,"building_detail":null,"note":null,"orientation":"남향","appraisal":980000000,"min_bid":686000000,"fail_rounds":1,"sale_date":"2026-10-14","case_no":null,"market_price":1120000000,"market_source":"override","value_adjusted":1023621749,"winners_curse":0.086,"recommended_bid":748883333,"bid_strategies":{"ev_optimal":748883333,"safe_max":620468809,"win_target":897677831,"roi_floor":0.174,"min_roi_floor":0.08},"discount_vs_market":0.3314,"success_prob":0.0839,"expected_bidders":8.4,"net_profit":64960130,"roi":0.0821,"expected_value":5452379,"cost_items":{"인수권리":0,"취득세":17911875,"명도비":3000000,"수리비":20240000,"미납관리비":1518000,"보유비용":39244167,"매도중개":5118109,"등기·법무 등":1500000,"양도세":121246135},"total_cost":209778286,"assumed_rights":0,"rights_risk":{"score":0,"level":"낮음","flags":[]},"liquidity":{"score":76,"grade":"A","signals":["아파트(높음)","비선호 면적"]},"ratio_dist":{"mean":88.6,"mean_raw":83.8,"std":9.0},"curve":[{"bid":686000000,"win":0.0185,"profit":88996430,"roi":0.1229},{"bid":720300000,"win":0.0446,"profit":75910166,"roi":0.0998},{"bid":754600000,"win":0.0942,"profit":62765234,"roi":0.0787},{"bid":788900000,"win":0.1755,"profit":49561634,"roi":0.0594},{"bid":823200000,"win":0.2903,"profit":36299366,"roi":0.0416},{"bid":857500000,"win":0.4298,"profit":22978431,"roi":0.0253},{"bid":891800000,"win":0.5759,"profit":9598829,"roi":0.0101},{"bid":926100000,"win":0.7076,"profit":-14372859,"roi":-0.0146},{"bid":960400000,"win":0.8599,"profit":-51588359,"roi":-0.0506},{"bid":994700000,"win":0.9283,"profit":-88803859,"roi":-0.0842},{"bid":1029000000,"win":0.9677,"profit":-126019359,"roi":-0.1156}],"score":66,"score_breakdown":{"환금성":76,"안전마진":100,"위험조정수익":46,"권리안전":100,"낙찰가능성":8},"kelly_fraction":1.0,"special":[],"checklist":[{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null},{"id":"2024타경12345","court":"수원지방법원","address":"경기 수원시 영통구 매탄동 000","region":"경기 수원시","type":"아파트","apt_name":"매탄위브하늘채","exclusive_area":84.9,"floor":9,"total_floors":25,"built_year":2008,"building_detail":null,"note":"유치권 신고, 대지권미등기","orientation":"남향","appraisal":720000000,"min_bid":504000000,"fail_rounds":1,"sale_date":"2026-10-14","case_no":"2024타경12345","market_price":760000000,"market_source":"override","value_adjusted":694600472,"winners_curse":0.086,"recommended_bid":512400000,"bid_strategies":{"ev_optimal":512400000,"safe_max":421832212,"win_target":657066374,"roi_floor":0.17,"min_roi_floor":0.08},"discount_vs_market":0.3258,"success_prob":0.0275,"expected_bidders":8.2,"net_profit":43441974,"roi":0.0806,"expected_value":1194726,"cost_items":{"인수권리":0,"취득세":5636400,"명도비":3000000,"수리비":16980000,"미납관리비":1273500,"보유비용":27420000,"매도중개":3473002,"등기·법무 등":1500000,"양도세":79475596},"total_cost":138758498,"assumed_rights":0,"rights_risk":{"score":35,"level":"보통","flags":["대항력 임차인"]},"liquidity":{"score":80,"grade":"A","signals":["아파트(높음)"]},"ratio_dist":{"mean":88.2,"mean_raw":83.8,"std":9.0},"curve":[{"bid":504000000,"win":0.0203,"profit":46472189,"roi":0.0876},{"bid":529200000,"win":0.0483,"profit":37381541,"roi":0.0672},{"bid":554400000,"win":0.1007,"profit":28290893,"roi":0.0486},{"bid":579600000,"win":0.1853,"profit":19200245,"roi":0.0316},{"bid":604800000,"win":0.303,"profit":10037215,"roi":0.0159},{"bid":630000000,"win":0.4441,"profit":-3242030,"roi":-0.0049},{"bid":655200000,"win":0.5896,"profit":-31245479,"roi":-0.0455},{"bid":680400000,"win":0.719,"profit":-59342068,"roi":-0.0832},{"bid":705600000,"win":0.868,"profit":-87531796,"roi":-0.1183},{"bid":730800000,"win":0.9333,"profit":-115814663,"roi":-0.151},{"bid":756000000,"win":0.9703,"profit":-144190670,"roi":-0.1816}],"score":63,"score_breakdown":{"환금성":80,"안전마진":100,"위험조정수익":45,"권리안전":65,"낙찰가능성":3},"kelly_fraction":1.0,"special":["유치권","대지권미등기","선순위임차인"],"checklist":[{"item":"선순위 임차인 배당요구 확인","note":"배당요구를 안 했거나 배당이 부족하면 보증금을 낙찰자가 인수합니다. 명세서에서 전입일·확정일자·배당요구 종기를 확인하세요.","level":"high"},{"item":"유치권 성립·금액 확인","note":"성립 시 변제 전까지 인도 거부가 가능합니다. 공사대금 근거와 실제 점유를 현장에서 확인하세요.","level":"high"},{"item":"대지권 미등기","note":"토지 지분 확보가 불확실합니다. 추후 대지권 취득 비용·분쟁 가능성을 확인하세요.","level":"high"},{"item":"선순위 권리 인수 여부","note":"말소기준권리보다 앞선 전세권·임차권은 인수될 수 있습니다.","level":"high"},{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"경락잔금대출 가능 여부","note":"특수물건·위반건축물은 대출이 제한될 수 있어 실투자금이 커질 수 있습니다.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":{"낙찰가":512400000,"경매비용":7686000,"배당재원":504714000,"말소기준일":"2020-05-01","인수합계":120000000,"rows":[{"권리":"임차보증금","청구액":120000000,"배당액":0,"상태":"일부배당·잔액 인수"},{"권리":"근저당","청구액":400000000,"배당액":400000000,"상태":"전액배당"}],"note":"법원경매 물건상세의 등기·임차 데이터 기반 추정. 실제 배당은 법원 판단."},"households":447,"builder":"대림산업(주)","molit_count":6,"molit_low":820000000.0,"molit_high":970000000.0,"price_per_pyeong":38000000.0},{"id":"2024타경34567","court":"인천지방법원","address":"인천 연수구 송도동 000","region":"인천 연수구","type":"오피스텔","apt_name":"송도더샵퍼스트파크","exclusive_area":59.5,"floor":20,"total_floors":40,"built_year":2019,"building_detail":null,"note":null,"orientation":"남서향","appraisal":430000000,"min_bid":301000000,"fail_rounds":1,"sale_date":"2026-10-21","case_no":null,"market_price":520000000,"market_source":"override","value_adjusted":487267100,"winners_curse":0.063,"recommended_bid":328591666,"bid_strategies":{"ev_optimal":328591666,"safe_max":260849469,"win_target":317024973,"roi_floor":0.192,"min_roi_floor":0.08},"discount_vs_market":0.3681,"success_prob":0.6907,"expected_bidders":4.2,"net_profit":33644852,"roi":0.0907,"expected_value":23239098,"cost_items":{"인수권리":25000000,"취득세":3614508,"명도비":1000000,"수리비":11900000,"미납관리비":892500,"보유비용":18229583,"매도중개":2436336,"등기·법무 등":1500000,"양도세":60457655},"total_cost":125030582,"assumed_rights":25000000,"rights_risk":{"score":28,"level":"낮음","flags":["유치권"]},"liquidity":{"score":58,"grade":"B","signals":["오피스텔(중)"]},"ratio_dist":{"mean":70.9,"mean_raw":72.0,"std":11.0},"curve":[{"bid":301000000,"win":0.466,"profit":43598269,"roi":0.1271},{"bid":316050000,"win":0.592,"profit":38169132,"roi":0.1065},{"bid":331100000,"win":0.7092,"profit":32739995,"roi":0.0876},{"bid":346150000,"win":0.8076,"profit":27310858,"roi":0.0703},{"bid":361200000,"win":0.8824,"profit":21881721,"roi":0.0542},{"bid":376250000,"win":0.9339,"profit":16452584,"roi":0.0392},{"bid":391300000,"win":0.9659,"profit":11023447,"roi":0.0254},{"bid":406350000,"win":0.9839,"profit":5594310,"roi":0.0124},{"bid":421400000,"win":0.9931,"profit":-4367135,"roi":-0.0094},{"bid":436450000,"win":0.9973,"profit":-20335185,"roi":-0.0424},{"bid":451500000,"win":0.999,"profit":-36303235,"roi":-0.0733}],"score":60,"score_breakdown":{"환금성":58,"안전마진":100,"위험조정수익":50,"권리안전":72,"낙찰가능성":69},"kelly_fraction":1.0,"special":[],"checklist":[{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null},{"id":"2024타경89012","court":"인천지방법원","address":"인천 연수구 연수동 000","region":"인천 연수구","type":"빌라","apt_name":"연수한신빌라","exclusive_area":54.2,"floor":3,"total_floors":4,"built_year":2005,"building_detail":null,"note":null,"orientation":"남향","appraisal":320000000,"min_bid":224000000,"fail_rounds":1,"sale_date":"2026-10-21","case_no":null,"market_price":360000000,"market_source":"override","value_adjusted":341220446,"winners_curse":0.052,"recommended_bid":229600000,"bid_strategies":{"ev_optimal":229600000,"safe_max":192751770,"win_target":224000000,"roi_floor":0.203,"min_roi_floor":0.08},"discount_vs_market":0.3622,"success_prob":0.6933,"expected_bidders":3.0,"net_profit":28834953,"roi":0.1178,"expected_value":19992184,"cost_items":{"인수권리":0,"취득세":2525600,"명도비":1000000,"수리비":10840000,"미납관리비":813000,"보유비용":13280000,"매도중개":1706102,"등기·법무 등":1500000,"양도세":51120791},"total_cost":82785493,"assumed_rights":0,"rights_risk":{"score":0,"level":"낮음","flags":[]},"liquidity":{"score":47,"grade":"C","signals":["빌라(낮음)"]},"ratio_dist":{"mean":65.2,"mean_raw":68.0,"std":13.0},"curve":[{"bid":224000000,"win":0.6446,"profit":30855096,"roi":0.129},{"bid":235200000,"win":0.7389,"profit":26814808,"roi":0.1071},{"bid":246400000,"win":0.8184,"profit":22774520,"roi":0.087},{"bid":257600000,"win":0.8807,"profit":18734232,"roi":0.0686},{"bid":268800000,"win":0.9261,"profit":14693944,"roi":0.0517},{"bid":280000000,"win":0.957,"profit":10653656,"roi":0.036},{"bid":291200000,"win":0.9765,"profit":6613368,"roi":0.0215},{"bid":302400000,"win":0.9879,"profit":2573080,"roi":0.0081},{"bid":313600000,"win":0.9942,"profit":-9168256,"roi":-0.0278},{"bid":324800000,"win":0.9974,"profit":-21051456,"roi":-0.0617},{"bid":336000000,"win":0.9989,"profit":-32934656,"roi":-0.0935}],"score":60,"score_breakdown":{"환금성":47,"안전마진":100,"위험조정수익":65,"권리안전":100,"낙찰가능성":69},"kelly_fraction":1.0,"special":[],"checklist":[{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null},{"id":"2024타경78901","court":"수원지방법원","address":"경기 수원시 팔달구 인계동 000","region":"경기 수원시","type":"아파트","apt_name":"수원힐스테이트","exclusive_area":59.9,"floor":14,"total_floors":22,"built_year":2013,"building_detail":null,"note":null,"orientation":"남향","appraisal":640000000,"min_bid":448000000,"fail_rounds":1,"sale_date":"2026-10-14","case_no":null,"market_price":720000000,"market_source":"override","value_adjusted":658042553,"winners_curse":0.086,"recommended_bid":496533333,"bid_strategies":{"ev_optimal":496533333,"safe_max":327154504,"win_target":585792759,"roi_floor":0.17,"min_roi_floor":0.08},"discount_vs_market":0.3104,"success_prob":0.1068,"expected_bidders":8.4,"net_profit":11425670,"roi":0.0191,"expected_value":1220568,"cost_items":{"인수권리":80000000,"취득세":5461867,"명도비":3000000,"수리비":11980000,"미납관리비":898500,"보유비용":26626667,"매도중개":3290213,"등기·법무 등":1500000,"양도세":17326303},"total_cost":150083550,"assumed_rights":80000000,"rights_risk":{"score":55,"level":"보통","flags":["대항력 임차인","인수보증금 8,000만"]},"liquidity":{"score":80,"grade":"A","signals":["아파트(높음)"]},"ratio_dist":{"mean":88.5,"mean_raw":83.8,"std":9.0},"curve":[{"bid":448000000,"win":0.0189,"profit":28933585,"roi":0.0527},{"bid":470400000,"win":0.0453,"profit":20853009,"roi":0.0365},{"bid":492800000,"win":0.0955,"profit":12772433,"roi":0.0215},{"bid":515200000,"win":0.1775,"profit":4691857,"roi":0.0076},{"bid":537600000,"win":0.2929,"profit":-14819759,"roi":-0.0232},{"bid":560000000,"win":0.4327,"profit":-38586159,"roi":-0.0583},{"bid":582400000,"win":0.5787,"profit":-62352559,"roi":-0.0911},{"bid":604800000,"win":0.7099,"profit":-86331849,"roi":-0.122},{"bid":627200000,"win":0.8616,"profit":-111136414,"roi":-0.152},{"bid":649600000,"win":0.9293,"profit":-136014571,"roi":-0.1802},{"bid":672000000,"win":0.9682,"profit":-160966319,"roi":-0.2067}],"score":54,"score_breakdown":{"환금성":80,"안전마진":98,"위험조정수익":11,"권리안전":45,"낙찰가능성":11},"kelly_fraction":1.0,"special":["선순위임차인"],"checklist":[{"item":"선순위 임차인 배당요구 확인","note":"배당요구를 안 했거나 배당이 부족하면 보증금을 낙찰자가 인수합니다. 명세서에서 전입일·확정일자·배당요구 종기를 확인하세요.","level":"high"},{"item":"선순위 권리 인수 여부","note":"말소기준권리보다 앞선 전세권·임차권은 인수될 수 있습니다.","level":"high"},{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"경락잔금대출 가능 여부","note":"특수물건·위반건축물은 대출이 제한될 수 있어 실투자금이 커질 수 있습니다.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null},{"id":"2024타경23456","court":"서울북부지방법원","address":"서울 노원구 상계동 000","region":"서울 노원구","type":"아파트","apt_name":"상계주공7단지","exclusive_area":49.9,"floor":5,"total_floors":15,"built_year":1988,"building_detail":null,"note":null,"orientation":"동향","appraisal":610000000,"min_bid":610000000,"fail_rounds":0,"sale_date":"2026-10-07","case_no":null,"market_price":640000000,"market_source":"override","value_adjusted":582624451,"winners_curse":0.09,"recommended_bid":610000000,"bid_strategies":{"ev_optimal":610000000,"safe_max":245484405,"win_target":629681738,"roi_floor":0.16,"min_roi_floor":0.08},"discount_vs_market":0.0469,"success_prob":0.4404,"expected_bidders":8.7,"net_profit":-209974504,"roi":-0.2778,"expected_value":-92471772,"cost_items":{"인수권리":120000000,"취득세":7157333,"명도비":8000000,"수리비":9980000,"미납관리비":748500,"보유비용":32300000,"매도중개":2913122,"등기·법무 등":1500000,"양도세":0},"total_cost":182598955,"assumed_rights":120000000,"rights_risk":{"score":65,"level":"높음","flags":["대항력 임차인","인수보증금 12,000만"]},"liquidity":{"score":90,"grade":"A","signals":["아파트(높음)"]},"ratio_dist":{"mean":101.2,"mean_raw":96.0,"std":8.0},"curve":[{"bid":610000000,"win":0.4404,"profit":-209974504,"roi":-0.2778},{"bid":613050000,"win":0.4652,"profit":-213349910,"roi":-0.2811},{"bid":616100000,"win":0.49,"profit":-216726679,"roi":-0.2843},{"bid":619150000,"win":0.515,"profit":-220104814,"roi":-0.2875},{"bid":622200000,"win":0.5398,"profit":-223484312,"roi":-0.2907},{"bid":625250000,"win":0.5646,"profit":-226865175,"roi":-0.2939},{"bid":628300000,"win":0.589,"profit":-230247403,"roi":-0.297},{"bid":631350000,"win":0.6131,"profit":-233630994,"roi":-0.3001},{"bid":634400000,"win":0.6368,"profit":-237015950,"roi":-0.3032},{"bid":637450000,"win":0.66,"profit":-240402271,"roi":-0.3063},{"bid":640500000,"win":0.6826,"profit":-243789956,"roi":-0.3093}],"score":20,"score_breakdown":{"환금성":90,"안전마진":0,"위험조정수익":0,"권리안전":35,"낙찰가능성":44},"kelly_fraction":0.0,"special":["선순위임차인"],"checklist":[{"item":"선순위 임차인 배당요구 확인","note":"배당요구를 안 했거나 배당이 부족하면 보증금을 낙찰자가 인수합니다. 명세서에서 전입일·확정일자·배당요구 종기를 확인하세요.","level":"high"},{"item":"선순위 권리 인수 여부","note":"말소기준권리보다 앞선 전세권·임차권은 인수될 수 있습니다.","level":"high"},{"item":"재건축 연한(1988년 준공)","note":"노후 단지는 재건축 기대이익/멸실 리스크가 큽니다. 정비사업 단계를 확인하세요.","level":"info"},{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"경락잔금대출 가능 여부","note":"특수물건·위반건축물은 대출이 제한될 수 있어 실투자금이 커질 수 있습니다.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null},{"id":"2024타경56789","court":"인천지방법원","address":"인천 부평구 부평동 000","region":"인천 부평구","type":"아파트","apt_name":"부평아이파크","exclusive_area":74.5,"floor":9,"total_floors":20,"built_year":2015,"building_detail":null,"note":null,"orientation":"남동향","appraisal":560000000,"min_bid":560000000,"fail_rounds":0,"sale_date":"2026-10-07","case_no":null,"market_price":590000000,"market_source":"override","value_adjusted":541697098,"winners_curse":0.082,"recommended_bid":560000000,"bid_strategies":{"ev_optimal":560000000,"safe_max":326853050,"win_target":560000000,"roi_floor":0.17,"min_roi_floor":0.08},"discount_vs_market":0.0508,"success_prob":0.8369,"expected_bidders":6.6,"net_profit":-77488887,"roi":-0.1324,"expected_value":-64848602,"cost_items":{"인수권리":0,"취득세":6160000,"명도비":3000000,"수리비":14900000,"미납관리비":1117500,"보유비용":29800000,"매도중개":2708485,"등기·법무 등":1500000,"양도세":0},"total_cost":59185985,"assumed_rights":0,"rights_risk":{"score":0,"level":"낮음","flags":[]},"liquidity":{"score":80,"grade":"A","signals":["아파트(높음)"]},"ratio_dist":{"mean":90.2,"mean_raw":88.0,"std":10.0},"curve":[{"bid":560000000,"win":0.8369,"profit":-77488887,"roi":-0.1324},{"bid":562800000,"win":0.8489,"profit":-80459687,"roi":-0.1368},{"bid":565600000,"win":0.8603,"profit":-83430487,"roi":-0.1412},{"bid":568400000,"win":0.8711,"profit":-86401287,"roi":-0.1455},{"bid":571200000,"win":0.8813,"profit":-89372087,"roi":-0.1498},{"bid":574000000,"win":0.891,"profit":-92342887,"roi":-0.1541},{"bid":576800000,"win":0.9,"profit":-95313687,"roi":-0.1583},{"bid":579600000,"win":0.9085,"profit":-98284487,"roi":-0.1625},{"bid":582400000,"win":0.9165,"profit":-101255287,"roi":-0.1666},{"bid":585200000,"win":0.9239,"profit":-104226087,"roi":-0.1707},{"bid":588000000,"win":0.9308,"profit":-107196887,"roi":-0.1747}],"score":20,"score_breakdown":{"환금성":80,"안전마진":0,"위험조정수익":0,"권리안전":100,"낙찰가능성":84},"kelly_fraction":0.0,"special":[],"checklist":[{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null},{"id":"2024타경67890","court":"서울북부지방법원","address":"서울 노원구 중계동 000","region":"서울 노원구","type":"아파트","apt_name":"노원롯데캐슬","exclusive_area":84.7,"floor":7,"total_floors":18,"built_year":2010,"building_detail":null,"note":null,"orientation":"서향","appraisal":850000000,"min_bid":850000000,"fail_rounds":0,"sale_date":"2026-10-28","case_no":null,"market_price":830000000,"market_source":"override","value_adjusted":758576831,"winners_curse":0.086,"recommended_bid":850000000,"bid_strategies":{"ev_optimal":850000000,"safe_max":471864673,"win_target":871195603,"roi_floor":0.16,"min_roi_floor":0.08},"discount_vs_market":-0.0241,"success_prob":0.4767,"expected_bidders":8.2,"net_profit":-187159886,"roi":-0.2089,"expected_value":-89225434,"cost_items":{"인수권리":0,"취득세":24933333,"명도비":3000000,"수리비":16940000,"미납관리비":1270500,"보유비용":44300000,"매도중개":3792884,"등기·법무 등":1500000,"양도세":0},"total_cost":95736717,"assumed_rights":0,"rights_risk":{"score":0,"level":"낮음","flags":[]},"liquidity":{"score":90,"grade":"A","signals":["아파트(높음)"]},"ratio_dist":{"mean":100.5,"mean_raw":96.0,"std":8.0},"curve":[{"bid":850000000,"win":0.4767,"profit":-187159886,"roi":-0.2089},{"bid":854250000,"win":0.5017,"profit":-192013294,"roi":-0.2132},{"bid":858500000,"win":0.5266,"profit":-196869351,"roi":-0.2174},{"bid":862750000,"win":0.5514,"profit":-201728057,"roi":-0.2217},{"bid":867000000,"win":0.576,"profit":-206589413,"roi":-0.2258},{"bid":871250000,"win":0.6003,"profit":-211453417,"roi":-0.23},{"bid":875500000,"win":0.6242,"profit":-216320071,"roi":-0.2341},{"bid":879750000,"win":0.6477,"profit":-221189374,"roi":-0.2382},{"bid":884000000,"win":0.6706,"profit":-226061326,"roi":-0.2422},{"bid":888250000,"win":0.6929,"profit":-230935927,"roi":-0.2462},{"bid":892500000,"win":0.7145,"profit":-235813178,"roi":-0.2502}],"score":20,"score_breakdown":{"환금성":90,"안전마진":0,"위험조정수익":0,"권리안전":100,"낙찰가능성":48},"kelly_fraction":0.0,"special":[],"checklist":[{"item":"미납 관리비 확인","note":"공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.","level":"warn"},{"item":"서류 교차 확인","note":"매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.","level":"info"}],"distribution":null}],"backtest":{"summary":{"n":1,"avg_net_profit":-72815000,"median_net_profit":-72815000,"avg_roi":-0.0692,"win_rate_positive":0.0,"total_net_profit":-72815000},"cases":[{"id":"수원지방법원_2024타경51234_1","court":"수원지방법원","case_no":"2024타경51234","region":"경기 수원시","type":"아파트","apt_name":"광교","won_bid":940000000.0,"resale_price":980000000,"net_profit":-72815000.0,"my_predicted_bid":980000000,"would_win":true,"roi":-0.0692,"sale_ratio":95.9,"bidders":12,"resale_date":"2026-09-12"}]},"region_stats":{"경기 수원시·아파트":{"avg_sale_ratio":95.9,"avg_bidders":12,"n":1}}};
const won=n=>{if(n==null||isNaN(n))return"—";const g=n<0;n=Math.abs(Math.round(n));const e=Math.floor(n/1e8),m=Math.round((n%1e8)/1e4);return(g?"−":"")+(e?`${e}억 ${m?m.toLocaleString()+"만":""}`.trim():`${m.toLocaleString()}만`)};
const pct=x=>x==null?"—":(x*100).toFixed(x*100<10?1:0)+"%";
const sc=n=>n>=0?"pos":"neg";
const el=id=>document.getElementById(id);
const dong=a=>{const m=(a||"").match(/([가-힣]+(?:동|읍|면))/);return m?m[1]:""};
const pName=r=>(r.apt_name&&r.apt_name.trim())||dong(r.address)||r.type||"물건";
const caseNo=r=>{if(r.case_no)return r.case_no;const m=(r.id||"").match(/\d{4}[가-힣]?타경\d+/);return m?m[0]:""};
const courtOf=r=>r.court||((r.id||"").split("_")[0].match(/법원|지원/)?(r.id||"").split("_")[0]:"");
const caseLink=r=>{const c=caseNo(r);if(!c)return "";const q=encodeURIComponent((courtOf(r)?courtOf(r)+" ":"")+c+" 법원경매");return `<a href="https://search.naver.com/search.naver?query=${q}" target="_blank" rel="noopener" onclick="event.stopPropagation()" style="color:var(--link)">사건 ${c} ↗</a>`;};
const COURT="https://www.courtauction.go.kr/";
function verdict(r){const hi=(r.rights_risk||{}).level==="높음";
  if(r.net_profit>0&&r.success_prob>=.35&&r.roi>=.10&&!hi)return["v-go","입찰 적합"];
  if(r.net_profit>0&&r.roi>=.05&&!hi)return["v-hold","조건부"];return["v-skip","보류"]}

function card(r,i){const[vc,vt]=verdict(r);const lq=r.liquidity||{},rk=r.rights_risk||{level:"낮음"},st=r.bid_strategies||{},bd=r.score_breakdown||{};
  const scc=r.score>=55?"s-hi":r.score>=40?"s-mid":"s-lo";
  const rkc=rk.level==="높음"?"rk-high":rk.level==="보통"?"rk-mid":"rk-low";
  const flags=(rk.flags||[]).map(f=>`<span class="flag">${f}</span>`).join("");
  const sp=(r.special||[]).map(x=>`<span class="flag sp">${x}</span>`).join("");
  const chk=r.checklist||[];const hi=chk.filter(c=>c.level==="high").length;
  const wc=r.winners_curse?`<tr><td>승자의 저주 보정</td><td>−${(r.winners_curse*100).toFixed(1)}% → ${won(r.value_adjusted)}원</td></tr>`:"";
  const costs=Object.entries(r.cost_items||{}).map(([k,v])=>v?`<tr><td>− ${k}</td><td>${won(v)}원</td></tr>`:"").join("");
  const py=r.price_per_pyeong?Math.round(r.price_per_pyeong/1e4).toLocaleString()+"만원/평":null;const rng=(r.molit_low&&r.molit_high)?won(r.molit_low)+"~"+won(r.molit_high)+"원":null;const built=r.approve_date?String(r.approve_date).slice(0,4):(r.built_year||r.build_year);const info=[["소재지",r.address],["건물내역",r.building_detail],["세대수",r.households?r.households.toLocaleString()+"세대"+(r.dong_count?" · "+r.dong_count+"개동":""):null],["층",r.floor?(r.floor+"층"+(r.total_floors?" / 총 "+r.total_floors+"층":"")):null],["준공",built?built+"년":null],["실거래(최근)",r.molit_count?r.molit_count+"건":null],["평단가",py],["최근 실거래가",rng],["매각기일",r.sale_date],["비고",r.note]].filter(x=>x[1]);
  const infoHTML=info.length?`<div class="dtitle">물건 정보</div><table class="kv">${info.map(([k,v])=>`<tr><td style="white-space:nowrap">${k}</td><td style="text-align:left;color:var(--tx);font-weight:500">${v}</td></tr>`).join("")}</table>`:"";
  return `<div class="card" data-i="${i}" data-type="${r.type}">
    <div class="chead">
      <div class="score ${scc}">${r.score}</div>
      <div class="cinfo"><div class="cname">${pName(r)}</div>
        <div class="cmeta">${r.region} · ${r.type} · 유찰 ${r.fail_rounds}회${r.sale_date?" · 매각 "+r.sale_date:""}${r.views?" · 조회 "+r.views.toLocaleString():""}<br>
          ${caseLink(r)}</div></div>
      <span class="vpill ${vc}">${vt}</span>
      <button class="fav" data-id="${r.id}" title="관심물건">${FAV.has(r.id)?"★":"☆"}</button>
    </div>
    <div class="stats">
      <div class="stat"><div class="l">적정 입찰가</div><div class="v">${won(r.recommended_bid)}<span class="sm">원</span></div></div>
      <div class="stat"><div class="l">낙찰 성공률</div><div class="v link">${pct(r.success_prob)} <span class="sm">~${r.expected_bidders}명</span></div></div>
      <div class="stat"><div class="l">예상 순이익</div><div class="v ${sc(r.net_profit)}">${won(r.net_profit)}<span class="sm">원</span></div></div>
      <div class="stat"><div class="l">투자수익률</div><div class="v ${sc(r.roi)}">${(r.roi*100).toFixed(1)}%</div></div>
    </div>
    <div class="rrow"><span class="rk ${rkc}">권리 ${rk.level}</span>${hi?`<span class="warnbadge">⚠ 인수주의 ${hi}</span>`:""}${flags}${sp}</div>
    <button class="more" onclick="toggle(this)">자세히 보기</button>
    <div class="detail">
      ${infoHTML}<div class="dtitle">입찰 전략가</div>
      <div class="strat">
        <div class="st"><div class="l">보수</div><div class="v">${won(st.safe_max)}</div></div>
        <div class="st rec"><div class="l">권장</div><div class="v">${won(r.recommended_bid)}</div></div>
        <div class="st"><div class="l">공격</div><div class="v">${won(st.win_target)}</div></div>
      </div>
      <div class="dtitle">수익 계산</div>
      <table class="kv"><tr><td>예상 매도가(시세)</td><td>${won(r.market_price)}원</td></tr>
        ${wc}<tr><td>− 낙찰가(권장)</td><td>${won(r.recommended_bid)}원</td></tr>${costs}
        <tr><td style="color:var(--tx);font-weight:700">= 순이익</td><td class="${sc(r.net_profit)}">${won(r.net_profit)}원</td></tr></table>
      <div class="dtitle">입찰 · 대출</div>
      <table class="kv"><tr><td>입찰 보증금 (최저가 ${(r.special||[]).includes("재매각")?"20":"10"}%)</td><td>${won(Math.round(r.min_bid*((r.special||[]).includes("재매각")?.2:.1)))}원</td></tr></table>
      <table class="kv"><tr><td>대출 (LTV)</td><td style="text-align:right;color:var(--mut);font-weight:600">실투자금</td><td style="text-align:right">레버리지 ROI</td></tr>
      ${[0,.5,.6,.7].map(l=>{const inv=Math.round(r.recommended_bid*(1-l));return `<tr><td>${l?l*100+"%":"현금(0%)"}</td><td style="text-align:right;color:var(--mut);font-weight:600">${won(inv)}원</td><td style="text-align:right" class="${sc(r.net_profit)}">${inv>0?(r.net_profit/inv*100).toFixed(1):"—"}%</td></tr>`}).join("")}</table>
      <div class="dtitle">지도 · 임장</div>
      <div class="maps"><a class="mlink" target="_blank" rel="noopener" href="https://map.kakao.com/?q=${encodeURIComponent(r.address||pName(r))}">카카오맵</a><a class="mlink" target="_blank" rel="noopener" href="https://map.naver.com/p/search/${encodeURIComponent(r.address||pName(r))}">네이버 지도</a></div>
      ${r.distribution?`<div class="dtitle">예상 배당표</div><table class="kv"><tr><td>배당재원 (낙찰가 − 경매비용)</td><td>${won(r.distribution.배당재원)}원</td></tr>${r.distribution.rows.map(x=>`<tr><td>${x.권리} <span style="color:var(--dim)">청구 ${won(x.청구액)}</span></td><td>${won(x.배당액)}원 · <span style="color:${x.상태.includes("인수")?"var(--neg)":"var(--mut)"}">${x.상태}</span></td></tr>`).join("")}<tr><td style="color:var(--tx);font-weight:700">인수 예상액(낙찰자 부담)</td><td class="${r.distribution.인수합계>0?"neg":"pos"}">${won(r.distribution.인수합계)}원</td></tr></table><p style="font-size:11.5px;color:var(--dim);margin:.3em 0 0">등기·임차 데이터 기반 추정. 실제 배당은 법원 판단.</p>`:""}
      ${chk.length?`<div class="dtitle">꼭 확인 · 인수/리스크</div><ul class="chk">${chk.map(c=>`<li class="lv-${c.level}"><b>${c.item}</b><span>${c.note}</span></li>`).join("")}</ul>`:""}<div class="dtitle">종합 점수 구성</div>
      <div class="bd"><span>환금성 ${bd.환금성??"—"}</span><span>안전마진 ${bd.안전마진??"—"}</span><span>위험조정 ${bd.위험조정수익??"—"}</span><span>권리 ${bd.권리안전??"—"}</span><span>낙찰가능 ${bd.낙찰가능성??"—"}</span><span>Kelly ${Math.round((r.kelly_fraction||0)*100)}%</span></div>
      <div class="dtitle">입찰가별 성공률·순이익</div>
      <canvas class="cv" height="120"></canvas>
    </div>
  </div>`}

function toggle(btn){const c=btn.closest(".card");const open=c.classList.toggle("open");
  btn.textContent=open?"접기":"자세히 보기";
  if(open){const r=RENDERED[+c.dataset.i];drawCurve(c.querySelector(".cv"),r)}}

function drawCurve(cv,r){const cur=r.curve;if(!cur)return;const dpr=devicePixelRatio||1,W=cv.clientWidth,H=cv.height;
  cv.width=W*dpr;cv.height=H*dpr;const g=cv.getContext("2d");g.scale(dpr,dpr);g.clearRect(0,0,W,H);
  let pmin=1e18,pmax=-1e18;cur.forEach(c=>{pmin=Math.min(pmin,c.profit);pmax=Math.max(pmax,c.profit)});
  const lo=cur[0].bid,hi=cur.at(-1).bid,p=6,X=b=>p+(b-lo)/(hi-lo)*(W-2*p),Yw=w=>H-p-w*(H-2*p),Yp=v=>H-p-((v-pmin)/((pmax-pmin)||1))*(H-2*p);
  if(pmin<0&&pmax>0){g.strokeStyle="#e5e5ea";g.setLineDash([3,4]);g.beginPath();g.moveTo(p,Yp(0));g.lineTo(W-p,Yp(0));g.stroke();g.setLineDash([])}
  g.strokeStyle="#f59e0b";g.lineWidth=2.2;g.beginPath();cur.forEach((c,i)=>i?g.lineTo(X(c.bid),Yp(c.profit)):g.moveTo(X(c.bid),Yp(c.profit)));g.stroke();
  g.strokeStyle="#3897f0";g.lineWidth=2.2;g.beginPath();cur.forEach((c,i)=>i?g.lineTo(X(c.bid),Yw(c.win)):g.moveTo(X(c.bid),Yw(c.win)));g.stroke();
  g.strokeStyle="rgba(28,28,30,.35)";g.setLineDash([2,3]);g.beginPath();g.moveTo(X(r.recommended_bid),p);g.lineTo(X(r.recommended_bid),H-p);g.stroke();g.setLineDash([])}

const SORT={score:(a,b)=>b.score-a.score,roi:(a,b)=>b.roi-a.roi,profit:(a,b)=>b.net_profit-a.net_profit,win:(a,b)=>b.success_prob-a.success_prob,sched:(a,b)=>((a.sale_date||"9999")<(b.sale_date||"9999")?-1:1)};
let THEME="전체";
const THEMES={"전체":r=>true,"반값경매":r=>r.appraisal&&r.min_bid/r.appraisal<=0.5,"유찰3회↑":r=>(r.fail_rounds||0)>=3,"고수익률":r=>(r.roi||0)>=0.15,"소액(3억↓)":r=>r.appraisal&&r.appraisal<=3e8,"특수물건":r=>(r.special||[]).length>0,"수도권":r=>/^(서울|경기|인천)/.test(r.region||"")};
let REGION="",VERDICT="",Q="",SPECIAL="",PAGE=1,RENDERED=[];const PAGESIZE=40;
let FAV=new Set(),FAVONLY=false;try{FAV=new Set(JSON.parse(localStorage.getItem("auc_fav")||"[]"))}catch(e){}
function toggleFav(id){if(FAV.has(id))FAV.delete(id);else FAV.add(id);try{localStorage.setItem("auc_fav",JSON.stringify([...FAV]))}catch(e){}}
function passF(r){
  if(FILTER!=="전체"&&r.type!==FILTER)return false;
  if(REGION&&!(r.region||"").startsWith(REGION))return false;
  if(VERDICT&&verdict(r)[1]!==VERDICT)return false;
  if(SPECIAL==="__sp"&&!((r.special||[]).length))return false;
  if(SPECIAL==="__no"&&(r.special||[]).length)return false;
  if(SPECIAL&&SPECIAL!=="__sp"&&SPECIAL!=="__no"&&!((r.special||[]).includes(SPECIAL)))return false;
  if(THEME!=="전체"&&!(THEMES[THEME]||(()=>true))(r))return false;
  if(FAVONLY&&!FAV.has(r.id))return false;
  if(Q){const h=(pName(r)+" "+(r.region||"")+" "+(r.address||"")+" "+caseNo(r)).toLowerCase();if(!h.includes(Q))return false;}
  return true;
}
const filtered=()=>AN.properties.filter(passF).sort(SORT[el("sort").value]);
function renderKPIs(rows){const n=rows.length;
  const fit=rows.filter(r=>verdict(r)[1]==="입찰 적합").length;
  const roi=n?rows.reduce((a,r)=>a+(r.roi||0),0)/n:0, avg=n?Math.round(rows.reduce((a,r)=>a+(r.score||0),0)/n):0;
  el("kpibar").innerHTML=[["매물",n.toLocaleString()],["입찰적합",fit.toLocaleString()],["평균 ROI",(roi*100).toFixed(1)+"%"],["평균 점수",avg]]
    .map(([l,v])=>`<div class="kpi2"><div class="l">${l}</div><div class="v">${v}</div></div>`).join("");}
function paint(reset){const rows=RENDERED,end=PAGE*PAGESIZE,start=reset?0:(PAGE-1)*PAGESIZE;
  const html=rows.slice(start,end).map((r,i)=>card(r,start+i)).join("");
  if(reset)el("feed").innerHTML=html||'<div class="msec" style="color:var(--mut)">조건에 맞는 매물이 없습니다.</div>';
  else el("feed").insertAdjacentHTML("beforeend",html);
  el("cnt").textContent=`${rows.length.toLocaleString()}건 중 ${Math.min(end,rows.length).toLocaleString()}건`;
  const rem=rows.length-end;el("more").hidden=rem<=0;el("more").textContent=`더 보기 (${rem.toLocaleString()}건 남음)`;}
function renderFeed(){PAGE=1;RENDERED=filtered();renderKPIs(RENDERED);paint(true);}
function renderThemes(){const ts=Object.keys(THEMES);
  el("themes").innerHTML=ts.map(t=>`<span class="chip th${t===THEME?" on":""}" data-t="${t}">${t}</span>`).join("");
  el("themes").querySelectorAll(".chip").forEach(c=>c.onclick=()=>{THEME=c.dataset.t;
    el("themes").querySelectorAll(".chip").forEach(x=>x.classList.toggle("on",x.dataset.t===THEME));renderFeed();});}
function renderChips(){
  const types=[...new Set(AN.properties.map(r=>r.type).filter(Boolean))];
  el("typesel").innerHTML='<option value="전체">전체 유형</option>'+types.map(t=>`<option>${t}</option>`).join("");
  const regs=[...new Set(AN.properties.map(r=>(r.region||"").split(" ")[0]).filter(Boolean))].sort();
  el("region").innerHTML='<option value="">전체 지역</option>'+regs.map(x=>`<option>${x}</option>`).join("");
  const sps=[...new Set(AN.properties.flatMap(r=>r.special||[]))].sort();
  el("special").innerHTML='<option value="">특수 전체</option><option value="__sp">특수물건만</option><option value="__no">일반물건만</option>'+sps.map(x=>`<option value="${x}">${x}</option>`).join("");}

let PQ="",PREGION="",PTYPE="",PPAGE=1,PALL=[],PRENDERED=[];
const PSORT={roi:(a,b)=>b.roi-a.roi,ratio:(a,b)=>(b.sale_ratio||0)-(a.sale_ratio||0),win:(a,b)=>b.won_bid-a.won_bid};
function ppass(c){
  if(PREGION&&!(c.region||"").startsWith(PREGION))return false;
  if(PTYPE&&c.type!==PTYPE)return false;
  if(PQ){const h=((c.apt_name||"")+" "+(c.region||"")+" "+(c.type||"")).toLowerCase();if(!h.includes(PQ))return false;}
  return true;
}
const pfiltered=()=>PALL.filter(ppass).sort(PSORT[el("psort").value]||PSORT.roi);
function pcard(c){const nm=c.apt_name||(c.region+" "+c.type);
  const roi=c.roi||0,circ=roi>=.1?"s-hi":roi>=0?"s-mid":"s-lo",win=c.would_win;
  return `<div class="card"><div class="chead">
    <div class="score ${circ}" style="font-size:14px">${(roi*100).toFixed(0)}%</div>
    <div class="cinfo"><div class="cname">${nm}</div>
      <div class="cmeta">${c.region} · ${c.type}${c.sale_ratio?' · 낙찰가율 '+c.sale_ratio+'%':''}${caseLink(c)?"<br>"+caseLink(c):""}</div></div>
    ${c.my_predicted_bid!=null?`<span class="vpill ${win?'v-go':'v-skip'}">${win?'예측 적중':'예측 미달'}</span>`:''}
  </div>
  <div class="stats">
    <div class="stat"><div class="l">내 예측 적정가</div><div class="v">${won(c.my_predicted_bid)}<span class="sm">원</span></div></div>
    <div class="stat"><div class="l">실제 낙찰가</div><div class="v">${won(c.won_bid)}<span class="sm">원</span></div></div>
    <div class="stat"><div class="l">매도가(추정)</div><div class="v" style="color:var(--mut)">${won(c.resale_price)}<span class="sm">원</span></div></div>
    <div class="stat"><div class="l">투자수익률</div><div class="v ${sc(roi)}">${(roi*100).toFixed(1)}%</div></div>
  </div></div>`;}
function renderPastKPIs(rows){const n=rows.length,wins=rows.filter(c=>c.would_win).length;
  const roi=n?rows.reduce((a,c)=>a+(c.roi||0),0)/n:0;
  el("pastKpi").innerHTML=[["실현",n.toLocaleString()+"건"],["평균 수익률",(roi*100).toFixed(1)+"%",sc(roi)],
    ["내예측 적중",n?Math.round(wins/n*100)+"%":"—"]]
    .map(([l,v,c])=>`<div class="kpi"><div class="l">${l}</div><div class="v ${c||""}">${v}</div></div>`).join("");}
function paintPast(reset){if(reset){PPAGE=1;PRENDERED=pfiltered();renderPastKPIs(PRENDERED);}
  const rows=PRENDERED,end=PPAGE*PAGESIZE,start=reset?0:(PPAGE-1)*PAGESIZE;
  const html=rows.slice(start,end).map(pcard).join("");
  if(reset)el("pastFeed").innerHTML=html||'<div class="msec" style="color:var(--mut)">조건에 맞는 실적이 없습니다.</div>';
  else el("pastFeed").insertAdjacentHTML("beforeend",html);
  el("pcnt").textContent=`${rows.length.toLocaleString()}건 중 ${Math.min(end,rows.length).toLocaleString()}건`;
  const rem=rows.length-end;el("pmore").hidden=rem<=0;el("pmore").textContent=`더 보기 (${rem.toLocaleString()}건 남음)`;}
function renderPast(){const bt=AN.backtest||{summary:{},cases:[]},wd=AN.history_lookback_days;PALL=bt.cases||[];
  const ms=AN.market_stats;el("mstat").innerHTML=ms?`<div class="msec"><h3 style="font-size:14px">시장 통계 · 실제 매각결과</h3><div class="statrow"><div><b>${(ms.sold||0).toLocaleString()}</b><span>매각 건수</span></div><div><b>${ms.avg_ratio??"—"}%</b><span>평균 매각가율</span></div><div><b>${ms.avg_bidders??"—"}명</b><span>평균 경쟁률</span></div></div>${ms.top?`<p style="font-size:12.5px;color:var(--mut);margin:.5em 0 0">최고 매각가율 ${ms.top.region} ${ms.top.type} ${ms.top.ratio}% · 최저 ${ms.bottom.region} ${ms.bottom.type} ${ms.bottom.ratio}%</p>`:""}</div>`:"";
  el("pastSub").textContent=`실제 낙찰 ${AN.history_used||0}건 · 매도가는 국토부 시세 기준 추정 · 최근 ${wd||30}일`;
  const regs=[...new Set(PALL.map(c=>(c.region||"").split(" ")[0]).filter(Boolean))].sort();
  el("pregion").innerHTML='<option value="">전체 지역</option>'+regs.map(x=>`<option>${x}</option>`).join("");
  const types=[...new Set(PALL.map(c=>c.type).filter(Boolean))];
  el("ptype").innerHTML='<option value="">전체 유형</option>'+types.map(x=>`<option>${x}</option>`).join("");
  paintPast(true);
  const rs=AN.region_stats||{},mx=Math.max(...Object.values(rs).map(x=>x.avg_sale_ratio),100);
  el("bars").innerHTML=Object.entries(rs).map(([k,v])=>`<div class="bar"><div>${k}</div>
    <div class="track"><div class="fill" style="width:${(v.avg_sale_ratio/mx*100).toFixed(0)}%"></div></div>
    <div class="num" style="text-align:right">${v.avg_sale_ratio}%</div></div>`).join("")||'<div style="color:var(--mut);font-size:12.5px">데이터 없음</div>'}

function renderMethod(){const w=(AN.assumptions&&AN.assumptions.score_weights)||{liquidity:.35,margin:.20,sharpe:.20,rights:.15,win:.10};const P=v=>Math.round(v*100)+"%";
  const wt=(lab,v)=>`<div class="wt"><span class="lab">${lab}</span><span class="bar"><i style="width:${Math.round(v*100)}%"></i></span><span class="v">${P(v)}</span></div>`;
  el("method").innerHTML=`<h1>산정 방법</h1><p class="sub">공개 데이터를 자동 분석해 각 지표를 산정합니다. 정의와 계산 기준은 아래와 같습니다.</p>
  <div class="msec"><h3>데이터 출처</h3><ul class="mlist">
    <li><b>경매 물건</b> — 법원경매정보 검색 API를 매일 수집</li>
    <li><b>과거 낙찰</b> — 법원경매정보 매각결과 API (최근 ${AN.history_lookback_days||60}일)</li>
    <li><b>시세</b> — 국토부 실거래가 OpenAPI, 같은 단지·유사 면적 실거래 중앙값(층·향 보정)</li>
    <li><b>단지 정보</b> — 공동주택 단지정보 API (세대수·준공·시공사·주차·난방)</li></ul></div>

  <div class="msec"><h3>매도가 (추정)</h3>
    <p><span class="lead">낙찰 후 되팔 때의 예상 가격입니다.</span></p>
    <p>해당 호실의 실제 재매도가는 공개되지 않아, 같은 단지·유사 면적의 <b>국토부 실거래가 중앙값</b>을 매도가로 씁니다. 실측이 아닌 시세 기준 추정치입니다.</p></div>

  <div class="msec"><h3>적정 입찰가</h3>
    <p><span class="lead">두 단계로 계산합니다.</span></p>
    <div class="step"><span class="n">1</span><span class="t"><b>승자의 저주 보정</b><br>낙찰됐다는 건 내 평가가 응찰자 중 가장 높았다는 뜻이라, 실제 가치는 시세보다 낮게 봅니다. 경쟁·불확실성이 클수록 더 보수적으로 잡습니다.</span></div>
    <div class="formula">보정가치 = 시세 × (1 − 변동계수 × 응찰자수 보정)</div>
    <div class="step"><span class="n">2</span><span class="t"><b>기대가치 최적화</b><br>실제 낙찰가율 분포로 낙찰 확률을 구하고, <b>낙찰확률 × 보정순이익</b>이 가장 큰 가격을 찾습니다.</span></div>
    <p>결과는 <b>보수 · 권장 · 공격</b> 세 가격으로 제시합니다.</p></div>

  <div class="msec"><h3>낙찰 성공률</h3>
    <p><span class="lead">내 입찰가로 낙찰될 확률입니다.</span></p>
    <p>지역·유형별 <b>실제 낙찰가율 분포</b>(과거 낙찰로 학습)에 경쟁도(예상 응찰자)를 반영한 뒤, 내 입찰가율이 그 분포에서 이길 확률로 계산합니다.</p></div>

  <div class="msec"><h3>예상 순이익 · 투자수익률</h3>
    <div class="formula">순이익 = 보정 매도가 − 낙찰가 − 부대비용</div>
    <p>부대비용에 들어가는 항목:</p>
    <ul class="mlist">
      <li>취득세 · <b>양도세</b> (보유기간별 세율·중과 반영)</li>
      <li>명도비 · 수리비 · 보유비용 · 매도 중개보수</li>
      <li>인수해야 할 권리 (임차보증금 등)</li></ul>
    <div class="formula">투자수익률(ROI) = 순이익 ÷ 투자원금</div>
    <p>투자원금은 낙찰가 + 취득비용 + 인수권리를 합한 값입니다.</p></div>

  <div class="msec"><h3>환금성</h3>
    <p><span class="lead">낙찰 후 얼마나 빨리·쉽게 되파는지를 A~D로 표시합니다.</span> 이 시스템이 가장 중요하게 보는 지표입니다.</p>
    <ul class="mlist">
      <li>같은 단지·지역의 <b>실거래 회전율</b></li>
      <li>물건 유형 (아파트 > 오피스텔 > 빌라)</li>
      <li>지역 수요 · 선호 면적대 · 가격대</li></ul></div>

  <div class="msec"><h3>종합 점수</h3>
    <p>아래 항목을 가중 합산한 뒤 <b>환금성 게이트</b>를 곱해 100점 만점으로 냅니다. 순손실 물건은 20점으로 제한합니다.</p>
    ${wt("환금성 <b>(최우선)</b>",w.liquidity)}
    ${wt("안전마진 · 보정가치 대비 쿠션",w.margin)}
    ${wt("위험조정수익 · 수익 대비 위험",w.sharpe)}
    ${wt("권리 안전",w.rights)}
    ${wt("낙찰 가능성",w.win)}
    <p style="margin-top:1.1em">이와 별도로 <b>켈리 기준</b> 권장 자금배분 비중도 함께 제시합니다.</p></div>`}
function renderGuide(){el("guide").innerHTML=`<h1>경매 가이드</h1><p class="sub">경매 절차와 입찰 방법, 자주 쓰는 용어를 정리했습니다.</p>
  <div class="msec"><h3>경매 절차</h3>
    <div class="step"><span class="n">1</span><span class="t"><b>경매개시결정</b><br>채권자 신청으로 법원이 경매를 시작하고 등기부에 기입합니다.</span></div>
    <div class="step"><span class="n">2</span><span class="t"><b>감정평가·현황조사</b><br>감정가가 정해지고 임차인·현황이 조사됩니다.</span></div>
    <div class="step"><span class="n">3</span><span class="t"><b>매각기일 공고</b><br>매각기일과 최저가가 공고됩니다. 유찰되면 최저가가 20~30% 낮아져 다음 기일이 잡힙니다.</span></div>
    <div class="step"><span class="n">4</span><span class="t"><b>입찰(기일입찰)</b><br>정해진 날 법원에서 입찰표와 보증금(최저가 10%)을 제출합니다.</span></div>
    <div class="step"><span class="n">5</span><span class="t"><b>최고가 매수인·매각허가</b><br>최고가 입찰자가 낙찰되고, 1주일 뒤 매각허가결정이 확정됩니다.</span></div>
    <div class="step"><span class="n">6</span><span class="t"><b>대금납부·소유권이전·명도</b><br>잔금(보통 경락잔금대출 활용)을 내면 소유권을 얻고, 점유자를 내보내는 명도를 진행합니다.</span></div></div>
  <div class="msec"><h3>입찰 방법</h3>
    <ul class="mlist">
      <li><b>준비물</b> — 신분증, 도장, 보증금(최저가의 10%, 재매각은 20~30%)</li>
      <li><b>입찰표 작성</b> — 사건번호·물건번호·입찰가·보증금액을 정확히 기재</li>
      <li><b>보증금 봉투</b> — 수표 한 장으로 준비하는 것이 편리</li>
      <li><b>개찰</b> — 최고가 입찰자가 낙찰. 동일가는 추첨</li>
      <li><b>패찰 시</b> — 보증금은 그 자리에서 반환</li></ul></div>
  <div class="msec"><h3>용어 사전</h3>
    <ul class="mlist">
      <li><b>감정가</b> — 감정평가사가 매긴 물건 가치. 1차 최저가의 기준</li>
      <li><b>최저매각가격</b> — 그 기일에 입찰 가능한 하한선. 유찰될수록 낮아짐</li>
      <li><b>유찰</b> — 입찰자가 없어 매각되지 않음. 다음 기일 최저가가 하락</li>
      <li><b>낙찰가율</b> — 낙찰가 ÷ 감정가. 경쟁·인기의 지표</li>
      <li><b>말소기준권리</b> — 이 권리(최선순위 근저당·압류 등)보다 뒤 권리는 소멸, 앞 권리는 인수</li>
      <li><b>대항력</b> — 임차인이 전입+점유로 갖는 힘. 선순위면 보증금을 낙찰자가 인수할 수 있음</li>
      <li><b>배당요구</b> — 임차인·채권자가 배당을 신청하는 것. 안 하면 인수 위험↑</li>
      <li><b>인수 / 소멸</b> — 낙찰 후에도 남는 권리(인수) vs 사라지는 권리(소멸)</li>
      <li><b>명도</b> — 낙찰 후 점유자를 내보내 물건을 인도받는 절차</li>
      <li><b>유치권</b> — 공사대금 등으로 점유하며 인도를 거부할 수 있는 권리(특수물건)</li>
      <li><b>법정지상권</b> — 건물을 위해 토지를 사용할 수 있는 권리(토지·건물 소유가 갈릴 때)</li>
      <li><b>지분매각</b> — 공유지분 일부만 매각. 공유자 우선매수·분할 이슈</li>
      <li><b>대지권미등기</b> — 아파트 등의 토지 지분이 미등기. 확인 필요</li>
      <li><b>재매각 / 재진행</b> — 낙찰자가 대금 미납해 다시 매각(보증금 20~30%)</li>
      <li><b>경락잔금대출</b> — 낙찰 후 잔금을 위한 대출. 레버리지로 실투자금·수익률이 달라짐</li></ul>
    <p style="font-size:12.5px;color:var(--mut)">각 물건의 적정입찰가·수익 산정 방식은 <b>산정 방법</b> 탭을 참고하세요.</p></div>`;}
function boot(){
  fetch("data/analysis.json").then(r=>r.ok?r.json():Promise.reject()).then(a=>{AN=(a&&a.properties&&a.properties.length)?a:FALLBACK;PREVIEW=(AN===FALLBACK);render()}).catch(()=>{AN=FALLBACK;PREVIEW=true;render()});
  document.querySelectorAll(".seg button").forEach(t=>t.onclick=()=>{
    document.querySelectorAll(".seg button").forEach(x=>x.classList.toggle("on",x===t));
    ["now","past","method","guide"].forEach(k=>el("tab-"+k).hidden=t.dataset.tab!==k);
    scrollTo({top:0,behavior:"smooth"})});
  el("typesel").onchange=()=>{FILTER=el("typesel").value;renderFeed();};
  el("sort").onchange=renderFeed;
  el("q").oninput=()=>{Q=el("q").value.trim().toLowerCase();renderFeed();};
  el("region").onchange=()=>{REGION=el("region").value;renderFeed();};
  el("verdict").onchange=()=>{VERDICT=el("verdict").value;renderFeed();};
  el("special").onchange=()=>{SPECIAL=el("special").value;renderFeed();};
  el("favbtn").onclick=()=>{FAVONLY=!FAVONLY;el("favbtn").classList.toggle("on",FAVONLY);el("favbtn").textContent=(FAVONLY?"★":"☆")+" 관심";renderFeed();};
  el("feed").addEventListener("click",e=>{const f=e.target.closest(".fav");if(!f)return;e.stopPropagation();toggleFav(f.dataset.id);f.textContent=FAV.has(f.dataset.id)?"★":"☆";if(FAVONLY)renderFeed();});
  el("more").onclick=()=>{PAGE++;paint(false);};
  el("pq").oninput=()=>{PQ=el("pq").value.trim().toLowerCase();paintPast(true);};
  el("pregion").onchange=()=>{PREGION=el("pregion").value;paintPast(true);};
  el("ptype").onchange=()=>{PTYPE=el("ptype").value;paintPast(true);};
  el("psort").onchange=()=>paintPast(true);
  el("pmore").onclick=()=>{PPAGE++;paintPast(false);};
  addEventListener("resize",()=>{document.querySelectorAll(".card.open").forEach(c=>drawCurve(c.querySelector(".cv"),RENDERED[+c.dataset.i]))});
}
function render(){el("upd").textContent=(PREVIEW?"미리보기 · 샘플":(AN.generated_at||"").slice(0,16).replace("T"," "));
  renderThemes();renderChips();renderFeed();renderPast();renderMethod();renderGuide()}
boot();
