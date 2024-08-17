const pricingTypelist = ['Free','Subscription','One-off','Usage-based','Negotiation']
const frequecylist = ['Daily','Weekly','Monthly','Quaterly','Yearly','Real-time','Never','Hourly','Minutely','Secondly','Irregular']

const pricing_type_translate:any = {
    'Free':'free',
    'Subscription':'subscription',
    'One-off':'one-off',
    'Usage-based':'usage-based',
    'Negotiation':'negotiation'
}

const frequecy_translate:any = {
    'Daily':'daily',
    'Weekly':'weekly',
    'Monthly':'monthly',
    'Quaterly':'quaterly',
    'Yearly':'yearly',
    'Real-time':'real-time',
    'Never':'no-update',
    'Hourly':'hourly',
    'Minutely':'minutely',
    'Secondly':'secondly',
    'Irregular':'irregular'
}

export function search(text:string,coverage:string[],provider:string[],price_range:number[],volume_range:number[],size_range:number[],dimension_range:number[],freq:string[],platform:string[],pricing_type:string[],category:string[]){
    
    let must=[]
    let tran_type = pricing_type.map((value,index)=>pricing_type_translate[value])
    let trans_freq = freq.map((value,index)=>frequecy_translate[value])
    if(provider.length>0)
        must.push(
            {'terms':{"provider":provider}}
        )
    if(platform.length>0)
        must.push(
            {'terms':{"platform":platform}}
        )
    if(pricing_type.length>0)
        must.push(
            {'terms':{"pricing_type":tran_type}}
        )
    if(freq.length>0)
        must.push(
            {'terms':{"freq":trans_freq}}
        )
    if(category.length>0)
    must.push(
        {'terms':{"category":category}}
    )
    must.push({
        'range':{
            'price':{
                'gte':price_range[0],
                'lte':price_range[1]
            }
        }
    })
    must.push({
        'range':{
            'volume':{
                'gte':volume_range[0],
                'lte':volume_range[1]
            }
        }
    })
    must.push({
        'range':{
            'size':{
                'gte':size_range[0],
                'lte':size_range[1]
            }
        }
    })
    must.push({
        'range':{
            'dimension':{
                'gte':dimension_range[0],
                'lte':dimension_range[1]
            }
        }
    })

    
    let querybody = {
        "query": {
            "bool": {
              "must": must,
              "should": [
                { 
                    "multi_match": { 
                        "query":text,
                        "fields":["title^3","geo_coverage^10","desc"]
                    } 
                }
              ]
            }
          }
    }
    return fetch('/data_market/_search',
        {
            method:'POST',
            body:JSON.stringify(querybody),
            // mode:'cors',
            headers:{
                'Content-Type':'application/json',
                // 'Access-Control-Allow-Origin':'*'
            }
            // credentials:'include',
            // headers:{
            //     'X-CSRFToken':cookie.load('csrftoken')
            // }
        }
    )
}