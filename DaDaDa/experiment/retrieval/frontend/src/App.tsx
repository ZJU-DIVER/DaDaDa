import React, { useState } from 'react';
import logo from './logo.svg';
import { Grid, IconButton, Stack, TextField } from '@mui/material';
import './App.css';
import CustomRadioGroup from './components/CustomRadioGroup';
import CustomSlider from './components/CustomSlider';
import CustomRegions from './components/CustomRegions';
import CustomSelect from './components/CustomSelect'
import SearchIcon from '@mui/icons-material/Search';
import provider_list from './res/provider_list.json'
import sampleresult from './res/sampleresult.json'
import ProductCard from './components/ProductCard';
import { search } from './api/API';
const platformlist = ['AWS Data Exchange','Datarade','Snowflake','Databricks','Beijing International Data Exchange','Canton Data Exchange','Shanghai Data Exchange','Guiyang Global Big Data Exchange','Zhejiang Big Data Exchange']
const pricingTypelist = ['Free','Subscription','One-off','Usage-based','Negotiation']
const frequecylist = ['Daily','Weekly','Monthly','Quaterly','Yearly','Real-time','Never']
const categorylist = ['Retail, Location & Marketing Data','Financial Services Data','Resources Data','Healthcare & Life Sciences Data','Public Sector Data','Media & Entertainment Data','Telecommunications Data','Automotive Data','Manufacturing Data','Environmental Data','Gaming Data','Other']

function priceScale(value:number){
  
  if(value<100){
    return value
  }
  if(value<190){
    return (value - 100)*10+100
  }
  if(value<280){
    return (value - 190)*100 + 1000
  }
  if(value<370){
    return (value - 280)*1000 + 10000
  }
  return (value-370)*10000+100000
}

function volumeScale(value:number){
  return 2 ** value;
}


const labelFormat = (type:string)=>(value:number)=>{
  let units = []
  if(type=='volume'){
    units = ['K', 'M', 'G', 'T'];
  }else{
    units = ['KB', 'MB', 'GB', 'TB'];
  }
  let unitIndex = 0;
  let scaledValue = value;

  while (scaledValue >= 1024 && unitIndex < units.length - 1) {
    unitIndex += 1;
    scaledValue /= 1024;
  }

  return `${scaledValue} ${units[unitIndex]}`;
}

function dimensionScale(value:number){
  if(value<100){
    return value
  }else{
    return (value - 100)*10 +100
  }
}

function App() {
  const [selectedCountries,setSelectedCountry] = useState<string[]>([])
  const [searchText,setSearchText] = useState<string>("")
  const [priceRange,setPriceRange] = useState<number[]>([0,9000000])
  const [volumeRange,setVolumeRange] = useState<number[]>([0,5120000000000])
  const [sizeRange,setSizeRange] = useState<number[]>([0,5120000000000])
  const [depthRange,setDepthRange] = useState<number[]>([0,1000])
  const [platforms,setPlatform] = useState<string[]>([])
  const [pricingtype,setPricingtype] = useState<string[]>([])
  const [frequecy,setFrequecy] = useState<string[]>([])
  const [providers,setProvider] = useState<string[]>([])
  const [category,setCatgory] = useState<string[]>([])
  const [results,setResults] = useState<any[]>(sampleresult.hits)
  let pro_list = []
  for(let k in provider_list){
    pro_list.push(k)
  }

  const handlesearch = (e:any)=>{
    search(searchText,selectedCountries,providers,priceRange,volumeRange,sizeRange,depthRange,frequecy,platforms,pricingtype,category)
    .then(res=>res.json())
    .then(res=>{
      let hits = res.hits.hits
      setResults(hits)
    })
  }

  const handleListChange = (type:string)=>(value:string[])=>{

    switch (type) {
      case 'platform':
        setPlatform(value)
        break;
      case 'pricingtype':
        setPricingtype(value)
        break;
      case 'frequency':
        setFrequecy(value)
        break;
      case 'provider':
        setProvider(value)
        break;
      case 'category':
        setCatgory(value)
        break;
      default:
        break;
    }
  }

  const handleRangeChange = (type:string)=>(value:number[])=>{
    let scaled_value = [...value]
    switch (type) {
      case 'volume':
        scaled_value[0] = volumeScale(value[0])
        scaled_value[1] = volumeScale(value[1])
        // console.log(scaled_value)
        setVolumeRange(scaled_value)
        break;
      case 'price':
        scaled_value[0] = priceScale(value[0])
        scaled_value[1] = priceScale(value[1])
        setPriceRange(scaled_value)
        break;
      case 'size':
        scaled_value[0] = volumeScale(value[0])
        scaled_value[1] = volumeScale(value[1])
        setSizeRange(scaled_value)
        break;
      case 'dimension':
        scaled_value[0] = dimensionScale(value[0])
        scaled_value[1] = dimensionScale(value[1])
        setDepthRange(scaled_value)
      break;
      default:
        break;
    }
  }

  return (
    <Stack display={'flex'} direction='row' alignItems='stretch' justifyContent='center' p={4} spacing={4}>
        <Stack width={'15%'} spacing={2}>
          <CustomSelect keys={platformlist} name='Platform' onChange={handleListChange('platform')}/>
          <CustomSelect keys={pricingTypelist} name='Pricing Mode' onChange={handleListChange('pricingtype')}/>
          <CustomSelect keys={frequecylist} name="Update Ferquency" onChange={handleListChange('frequency')}/>
          <CustomSelect keys={categorylist} name="Category" onChange={handleListChange('category')}/>
          <CustomSlider min={0} max={420} scale={priceScale} name='Price Range' onChange={handleRangeChange('price')}/>
          <CustomSlider min={0} max={39} scale={volumeScale} name='Volume Range' labelformat={labelFormat('volume')} onChange={handleRangeChange('volume')}/>
          <CustomSlider min={0} max={39} scale={volumeScale} name='Size Range' labelformat={labelFormat('size')} onChange={handleRangeChange('size')}/>
          <CustomSlider min={0} max={190} scale={dimensionScale} name='Dimension Range' onChange={handleRangeChange('dimension')}/>
          <CustomSelect keys={pro_list} name="Provider" onChange={handleListChange('provider')}/>
          <CustomRegions propCountries={selectedCountries} onCountriesChange={setSelectedCountry}/>
        </Stack>

        <Stack width={'50%'} spacing={2}>
          <Stack direction='row' spacing={2}>
          <TextField fullWidth label="Search" id="search" onChange={(e)=>setSearchText(e.target.value)}/>
          <IconButton aria-label="search" size="large" onClick={handlesearch}>
            <SearchIcon fontSize="inherit"/>
          </IconButton>
          </Stack>
          <Stack spacing={2}>
            {results.map((value,index)=>
            <ProductCard prodinfo={value['_source']}/>
            )}
          </Stack>
          {/* <CustomRadioGroup keys={platformlist} name='Platform'/> */}
        </Stack>
    </Stack>
  );
}

export default App;
