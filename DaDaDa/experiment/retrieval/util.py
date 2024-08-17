all_region = "AF,AX,AL,DZ,AS,AD,AO,AI,AQ,AG,AR,AM,AW,AU,AT,AZ,BS,BH,BD,BB,BY,BE,BZ,BJ,BM,BT,BO,BQ,BA,BW,BV,BR,IO,BN,BG,BF,BI,KH,CM,CA,CV,KY,CF,TD,CL,CN,CX,CC,CO,KM,CG,CD,CK,CR,CI,HR,CU,CW,CY,CZ,DK,DJ,DM,DO,EC,EG,SV,GQ,ER,EE,ET,FK,FO,FJ,FI,FR,GF,PF,TF,GA,GM,GE,DE,GH,GI,GR,GL,GD,GP,GU,GT,GG,GN,GW,GY,HT,HM,VA,HN,HK,HU,IS,IN,ID,IR,IQ,IE,IM,IL,IT,JM,JP,JE,JO,KZ,KE,KI,KP,KR,KW,KG,LA,LV,LB,LS,LR,LY,LI,LT,LU,MO,MK,MG,MW,MY,MV,ML,MT,MH,MQ,MR,MU,YT,MX,FM,MD,MC,MN,ME,MS,MA,MZ,MM,NA,NR,NP,NL,NC,NZ,NI,NE,NG,NU,NF,MP,NO,OM,PK,PW,PS,PA,PG,PY,PE,PH,PN,PL,PT,PR,QA,RE,RO,RU,RW,BL,SH,KN,LC,MF,PM,VC,WS,SM,ST,SA,SN,RS,SC,SL,SG,SX,SK,SI,SB,SO,ZA,GS,SS,ES,LK,SD,SR,SJ,SZ,SE,CH,SY,TW,TJ,TZ,TH,TL,TG,TK,TO,TT,TN,TR,TM,TC,TV,UG,UA,AE,GB,US,UM,UY,UZ,VU,VE,VN,VG,VI,WF,EH,YE,ZM,ZW"
region_list = all_region.split(',')
freq_list = ['daily','weekly','monthly','quarterly','yearly','on-demand','secondly','minutely','hourly','real-time']
method_list = ['S3 Bucket','REST API','UI Export','Email','SOAP API','SFTP','Streaming API','Feed API']
formats = ['csv','xls','xml','sql','txt','bin','json']

field_names = ['category','category_aws','coverage','currency','description','dimension','platform','price','price_mode','provider','size','title','update_frequency','url','volume']
field_names_new = ['category','category_aws','coverage','currency','description','dimension','platform','price','price_mode','provider','size','title','update_frequency','url','volume','datasample']
def handle_row(row:dict):

    result_dict = {
            "geo_coverage": row['coverage'],
            "title":row['title'],
            "desc":row['description'],
            "pricing_type":row['price_mode'],
            "currency":row['currency'],
            "category":row['category_aws'],
            "provider":row['provider'],
            "freq":[row['update_frequency']],
            # "format":format_list,
            # "method":methods,
            "url":row['url'],
            # "fixed":row['fixed_fee'],
            # "usage":row['usage_based_cost'],
            # "sub":row['subscription_fee'],
            # "sub_period":row['subscription_period'],
            "platform":row['platform'],
            "price":row['price'],
            "dimension":row['dimension'],
            "size":row['size'],
            "volume":row['volume']
    }
    return result_dict
    
    
def get_provider(path):
    from collections import defaultdict
    provider_dict = defaultdict(int)
    with open(path,'r',encoding='utf-8') as f:
        import csv
        rd = csv.DictReader(f,fieldnames=field_names)
        for row in rd:
            provider = row['provider']
            provider_dict[provider]+=1
    import json
    with open('./res/provider_list.json','w',encoding='utf-8',newline="") as wf:
        json.dump(provider_dict,wf,ensure_ascii=False)
        
def add_datasample(path,save_path):
    import csv
    with open(path,'r',encoding='utf-8') as f:
        rd = csv.DictReader(f)
        header = rd.fieldnames
        with open(save_path,'w',encoding='utf-8',newline="") as wf:
            # field_names.append('datasample')
            writer = csv.DictWriter(wf,field_names_new)
            writer.writeheader()
            # writer.writeheader()
            for row in rd:
                row['datasample'] = ""
                writer.writerow(row)