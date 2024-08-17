import { FormControl, InputLabel, Select, OutlinedInput, Box, Chip, ListSubheader, MenuItem, Checkbox, FormControlLabel, Grid, Stack, Typography } from '@mui/material'
import React, { useState } from 'react'

type Props = {
    propCountries:string[],
    onCountriesChange: (v:string[])=>void
}
const translate:any = {
    as:'Asia',
    af:'Africa',
    sa:"South America",
    na:'North America',
    oc:'Oceania',
    eu:'Europe',
    ot:'Other'
}

export default function CustomRegions({propCountries,onCountriesChange}: Props) {

    const [countries,setCountries] = useState<string[]>(propCountries)
    
    // const [selectedCountry,setSelectedCountry] = useState<string[]>([])

    const updateSelected = (params:any) => {
        let newSelected:string[] = []
        for(let country in params.batch[0].selected){
            if(params.batch[0].selected[country] === true){
                newSelected.push(country)
            }
        }
        console.log(newSelected)
        onCountriesChange(newSelected)
    }

    // const updateCheckBox = () => {

    // }

    const checkSelectedCount = (cont:string) => {
        let hit = 0
        let total = 0
        for(let country of data){
            if(country.cont === cont){
                total++
                if(propCountries.indexOf(country.name) !== -1)
                    hit++
            }
        }
        return [hit,total]
    }
    const renderMenuItems = (data:any[]) => {
        let continent:any = {
            as:[],
            eu:[],
            sa:[],
            na:[],
            oc:[],
            af:[],
            ot:[]
        }
        for(let country of data){
            continent[country.cont].push(country)
        }
        let itemsGroup:JSX.Element[] = []
        for(let cont in continent){
            let countries:any[] = continent[cont]
            itemsGroup.push(<ListSubheader><strong>{translate[cont]}</strong></ListSubheader>)
            itemsGroup.push(
                    ...countries.map((country) => (
                    <MenuItem
                        key={country.name}
                        value={country.name}
                    >
                        {country.name}
                    </MenuItem>
                ))
            )
        }
        return itemsGroup
    }

    const checkboxState = (cont:string,state:string) => {
        let checkres = checkSelectedCount(cont)
        if(state === 'indeterminate'){
            return checkres[0] > 0 && checkres[0] < checkres[1]
        }
        if(state === 'checked'){
            return checkres[0] === checkres[1]
        }
        return false
    }


    const quickSelect = (cont:string) => {
        console.log('quick')
        let newSelected =[...propCountries]
        if (!checkboxState(cont,'checked')){
            for(let country of data){
                //add
                if(country.cont === cont){
                    if(newSelected.indexOf(country.name) === -1){
                        toggleCountrySelect(country.name)
                        newSelected.push(country.name)
                    }
                }
            }
        }
        else {//remove
            for(let country of data){
                if(country.cont === cont){
                    let index = newSelected.indexOf(country.name)
                    newSelected.splice(index,1)
                    toggleCountrySelect(country.name)
                }
            }
        }
        onCountriesChange(newSelected)
    }

    const onMenuSelect = (e:any) => {
        console.log(e)
        const {
            target: { value },
        } = e;
        let v = typeof value === 'string' ? value.split(',') : value
        if(v.length >= propCountries.length){
            //new country added
            for(let name of v){
                if(propCountries.indexOf(name) === -1){
                    toggleCountrySelect(name)
                } 
            }
        }else{
            //country unselected
            for(let name of propCountries){
                if(v.indexOf(name) === -1){
                    toggleCountrySelect(name)
                } 
            }
        }
        onCountriesChange(v)
    }

    const toggleCountrySelect = (name:string) => {
        let type:string
        let index = propCountries.indexOf(name) 
        if(index !== -1){
            type = 'mapUnSelect'
            let newselected = [...propCountries]
            newselected.splice(index)
        } else {
            type = 'mapSelect'
            let newselected = [...propCountries]
            newselected.push(name)
        }

    }

    const renderValue = (selected:string[]) => {
        if(selected.length<=5){
            return  <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: 0.5 }}>
                        {selected.map((value) => (
                        <Chip key={value} label={value} />
                        ))}
                    </Box>
        }else{
            return  <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: 0.5 }}>
                        {selected.slice(0,5).map((value) => (
                        <Chip key={value} label={value} />
                        ))}
                        <Chip key={`+${selected.length-5} more...`} label={`+${selected.length-5} more...`}/>
                    </Box>
        }
    }


  return (
    <Stack spacing={2} alignItems={'center'}>
        <Typography variant='h6' alignSelf={'flex-start'}><strong>Data Coverage</strong></Typography>
        <Box sx={{px:2}}>
        <FormControl sx={{alignSelf:'flex-start'}} fullWidth>
            <InputLabel id="demo-select-country-label">Country/Region</InputLabel>
            <Select
                MenuProps={{sx:{maxHeight:'50vh'}}}
                id='demo-select-country'
                labelId='demo-select-country-label'
                multiple
                value={propCountries}
                onChange={onMenuSelect}
                input={<OutlinedInput fullWidth id="demo-select-country-chip" label="Country/Region"/>}
                renderValue={(selected)=>renderValue(selected)}
            >
                {renderMenuItems(data)}
            </Select>
        </FormControl>
        <Grid>
            <FormControlLabel
                label="Asia"
                control={
                    <Checkbox checked={checkboxState('as','checked')}
                        indeterminate={checkboxState('as','indeterminate')}
                        onChange={(e)=>quickSelect('as')}/>
                }
            />
            <FormControlLabel
                label="Europe"
                control={
                    <Checkbox checked={checkboxState('eu','checked')}
                        indeterminate={checkboxState('eu','indeterminate')}
                        onChange={(e)=>quickSelect('eu')}/>
                }
            />
            <FormControlLabel
                label="South America"
                control={
                    <Checkbox checked={checkboxState('sa','checked')}
                        indeterminate={checkboxState('sa','indeterminate')}
                        onChange={(e)=>quickSelect('sa')}/>
                }
            />
            <FormControlLabel
                label="North America"
                control={
                    <Checkbox checked={checkboxState('na','checked')}
                        indeterminate={checkboxState('na','indeterminate')}
                        onChange={(e)=>quickSelect('na')}/>
                }
            />
            <FormControlLabel
                label="Oceania"
                control={
                    <Checkbox checked={checkboxState('oc','checked')}
                        indeterminate={checkboxState('oc','indeterminate')}
                        onChange={(e)=>quickSelect('oc')}/>
                }
            />
            <FormControlLabel
                label="Africa"
                control={
                    <Checkbox checked={checkboxState('af','checked')}
                        indeterminate={checkboxState('af','indeterminate')}
                        onChange={(e)=>quickSelect('af')}/>
                }
            />
        </Grid>
        </Box>
        
    </Stack>
   
        

  )
}

const data = [
    {cont:'af',selected:false,name:"Somalia"},
    {cont:'eu',selected:false,name:"Liechtenstein"},
    {cont:'af',selected:false,name:"Morocco"},
    {cont:'af',selected:false,name:"W. Sahara"},
    {cont:'eu',selected:false,name:"Serbia"},
    {cont:'as',selected:false,name:"Afghanistan"},
    {cont:'af',selected:false,name:"Angola"},
    {cont:'eu',selected:false,name:"Albania"},
    {cont:'eu',selected:false,name:"Aland"},
    {cont:'eu',selected:false,name:"Andorra"},
    {cont:'as',selected:false,name:"United Arab Emirates"},
    {cont:'sa',selected:false,name:"Argentina"},
    {cont:'as',selected:false,name:"Armenia"},
    {cont:'oc',selected:false,name:"American Samoa"},
    {cont:'ot',selected:false,name:"Fr. S. Antarctic Lands"},
    {cont:'na',selected:false,name:"Antigua and Barb."},
    {cont:'oc',selected:false,name:"Australia"},
    {cont:'eu',selected:false,name:"Austria"},
    {cont:'as',selected:false,name:"Azerbaijan"},
    {cont:'af',selected:false,name:"Burundi"},
    {cont:'eu',selected:false,name:"Belgium"},
    {cont:'af',selected:false,name:"Benin"},
    {cont:'af',selected:false,name:"Burkina Faso"},
    {cont:'as',selected:false,name:"Bangladesh"},
    {cont:'eu',selected:false,name:"Bulgaria"},
    {cont:'as',selected:false,name:"Bahrain"},
    {cont:'na',selected:false,name:"Bahamas"},
    {cont:'eu',selected:false,name:"Bosnia and Herz."},
    {cont:'eu',selected:false,name:"Belarus"},
    {cont:'na',selected:false,name:"Belize"},
    {cont:'na',selected:false,name:"Bermuda"},
    {cont:'sa',selected:false,name:"Bolivia"},
    {cont:'sa',selected:false,name:"Brazil"},
    {cont:'na',selected:false,name:"Barbados"},
    {cont:'as',selected:false,name:"Brunei"},
    {cont:'as',selected:false,name:"Bhutan"},
    {cont:'af',selected:false,name:"Botswana"},
    {cont:'af',selected:false,name:"Central African Rep."},
    {cont:'na',selected:false,name:"Canada"},
    {cont:'eu',selected:false,name:"Switzerland"},
    {cont:'sa',selected:false,name:"Chile"},
    {cont:'as',selected:false,name:"China"},
    {cont:'af',selected:false,name:"Côte d'Ivoire"},
    {cont:'af',selected:false,name:"Cameroon"},
    {cont:'af',selected:false,name:"Dem. Rep. Congo"},
    {cont:'af',selected:false,name:"Congo"},
    {cont:'sa',selected:false,name:"Colombia"},
    {cont:'af',selected:false,name:"Comoros"},
    {cont:'af',selected:false,name:"Cape Verde"},
    {cont:'na',selected:false,name:"Costa Rica"},
    {cont:'na',selected:false,name:"Cuba"},
    {cont:'na',selected:false,name:"Curaçao"},
    {cont:'na',selected:false,name:"Cayman Is."},
    {cont:'eu',selected:false,name:"N. Cyprus"},
    {cont:'eu',selected:false,name:"Cyprus"},
    {cont:'eu',selected:false,name:"Czech Rep."},
    {cont:'eu',selected:false,name:"Germany"},
    {cont:'af',selected:false,name:"Djibouti"},
    {cont:'na',selected:false,name:"Dominica"},
    {cont:'eu',selected:false,name:"Denmark"},
    {cont:'na',selected:false,name:"Dominican Rep."},
    {cont:'af',selected:false,name:"Algeria"},
    {cont:'sa',selected:false,name:"Ecuador"},
    {cont:'af',selected:false,name:"Egypt"},
    {cont:'af',selected:false,name:"Eritrea"},
    {cont:'eu',selected:false,name:"Spain"},
    {cont:'eu',selected:false,name:"Estonia"},
    {cont:'af',selected:false,name:"Ethiopia"},
    {cont:'eu',selected:false,name:"Finland"},
    {cont:'oc',selected:false,name:"Fiji"},
    {cont:'sa',selected:false,name:"Falkland Is."},
    {cont:'eu',selected:false,name:"France"},
    {cont:'eu',selected:false,name:"Faeroe Is."},
    {cont:'oc',selected:false,name:"Micronesia"},
    {cont:'af',selected:false,name:"Gabon"},
    {cont:'eu',selected:false,name:"United Kingdom"},
    {cont:'eu',selected:false,name:"Georgia"},
    {cont:'af',selected:false,name:"Ghana"},
    {cont:'af',selected:false,name:"Guinea"},
    {cont:'af',selected:false,name:"Gambia"},
    {cont:'af',selected:false,name:"Guinea-Bissau"},
    {cont:'af',selected:false,name:"Eq. Guinea"},
    {cont:'eu',selected:false,name:"Greece"},
    {cont:'na',selected:false,name:"Grenada"},
    {cont:'eu',selected:false,name:"Greenland"},
    {cont:'na',selected:false,name:"Guatemala"},
    {cont:'oc',selected:false,name:"Guam"},
    {cont:'sa',selected:false,name:"Guyana"},
    {cont:'ot',selected:false,name:"Heard I. and McDonald Is."},
    {cont:'na',selected:false,name:"Honduras"},
    {cont:'eu',selected:false,name:"Croatia"},
    {cont:'na',selected:false,name:"Haiti"},
    {cont:'eu',selected:false,name:"Hungary"},
    {cont:'as',selected:false,name:"Indonesia"},
    {cont:'eu',selected:false,name:"Isle of Man"},
    {cont:'as',selected:false,name:"India"},
    {cont:'ot',selected:false,name:"Br. Indian Ocean Ter."},
    {cont:'eu',selected:false,name:"Ireland"},
    {cont:'as',selected:false,name:"Iran"},
    {cont:'as',selected:false,name:"Iraq"},
    {cont:'eu',selected:false,name:"Iceland"},
    {cont:'as',selected:false,name:"Israel"},
    {cont:'eu',selected:false,name:"Italy"},
    {cont:'na',selected:false,name:"Jamaica"},
    {cont:'eu',selected:false,name:"Jersey"},
    {cont:'as',selected:false,name:"Jordan"},
    {cont:'as',selected:false,name:"Japan"},
    {cont:'as',selected:false,name:"Siachen Glacier"},
    {cont:'as',selected:false,name:"Kazakhstan"},
    {cont:'af',selected:false,name:"Kenya"},
    {cont:'as',selected:false,name:"Kyrgyzstan"},
    {cont:'as',selected:false,name:"Cambodia"},
    {cont:'oc',selected:false,name:"Kiribati"},
    {cont:'as',selected:false,name:"Korea"},
    {cont:'as',selected:false,name:"Kuwait"},
    {cont:'as',selected:false,name:"Lao PDR"},
    {cont:'as',selected:false,name:"Lebanon"},
    {cont:'af',selected:false,name:"Liberia"},
    {cont:'af',selected:false,name:"Libya"},
    {cont:'na',selected:false,name:"Saint Lucia"},
    {cont:'as',selected:false,name:"Sri Lanka"},
    {cont:'af',selected:false,name:"Lesotho"},
    {cont:'eu',selected:false,name:"Lithuania"},
    {cont:'eu',selected:false,name:"Luxembourg"},
    {cont:'eu',selected:false,name:"Latvia"},
    {cont:'eu',selected:false,name:"Moldova"},
    {cont:'af',selected:false,name:"Madagascar"},
    {cont:'na',selected:false,name:"Mexico"},
    {cont:'eu',selected:false,name:"Macedonia"},
    {cont:'af',selected:false,name:"Mali"},
    {cont:'eu',selected:false,name:"Malta"},
    {cont:'as',selected:false,name:"Myanmar"},
    {cont:'eu',selected:false,name:"Montenegro"},
    {cont:'as',selected:false,name:"Mongolia"},
    {cont:'oc',selected:false,name:"N. Mariana Is."},
    {cont:'af',selected:false,name:"Mozambique"},
    {cont:'af',selected:false,name:"Mauritania"},
    {cont:'na',selected:false,name:"Montserrat"},
    {cont:'af',selected:false,name:"Mauritius"},
    {cont:'af',selected:false,name:"Malawi"},
    {cont:'as',selected:false,name:"Malaysia"},
    {cont:'af',selected:false,name:"Namibia"},
    {cont:'oc',selected:false,name:"New Caledonia"},
    {cont:'af',selected:false,name:"Niger"},
    {cont:'af',selected:false,name:"Nigeria"},
    {cont:'na',selected:false,name:"Nicaragua"},
    {cont:'oc',selected:false,name:"Niue"},
    {cont:'eu',selected:false,name:"Netherlands"},
    {cont:'eu',selected:false,name:"Norway"},
    {cont:'as',selected:false,name:"Nepal"},
    {cont:'oc',selected:false,name:"New Zealand"},
    {cont:'as',selected:false,name:"Oman"},
    {cont:'as',selected:false,name:"Pakistan"},
    {cont:'na',selected:false,name:"Panama"},
    {cont:'sa',selected:false,name:"Peru"},
    {cont:'as',selected:false,name:"Philippines"},
    {cont:'oc',selected:false,name:"Palau"},
    {cont:'oc',selected:false,name:"Papua New Guinea"},
    {cont:'eu',selected:false,name:"Poland"},
    {cont:'na',selected:false,name:"Puerto Rico"},
    {cont:'as',selected:false,name:"Dem. Rep. Korea"},
    {cont:'eu',selected:false,name:"Portugal"},
    {cont:'sa',selected:false,name:"Paraguay"},
    {cont:'as',selected:false,name:"Palestine"},
    {cont:'oc',selected:false,name:"Fr. Polynesia"},
    {cont:'as',selected:false,name:"Qatar"},
    {cont:'eu',selected:false,name:"Romania"},
    {cont:'eu',selected:false,name:"Russia"},
    {cont:'af',selected:false,name:"Rwanda"},
    {cont:'as',selected:false,name:"Saudi Arabia"},
    {cont:'af',selected:false,name:"Sudan"},
    {cont:'af',selected:false,name:"S. Sudan"},
    {cont:'af',selected:false,name:"Senegal"},
    {cont:'as',selected:false,name:"Singapore"},
    {cont:'ot',selected:false,name:"S. Geo. and S. Sandw. Is."},
    {cont:'af',selected:false,name:"Saint Helena"},
    {cont:'oc',selected:false,name:"Solomon Is."},
    {cont:'af',selected:false,name:"Sierra Leone"},
    {cont:'na',selected:false,name:"El Salvador"},
    {cont:'na',selected:false,name:"St. Pierre and Miquelon"},
    {cont:'af',selected:false,name:"São Tomé and Principe"},
    {cont:'sa',selected:false,name:"Suriname"},
    {cont:'eu',selected:false,name:"Slovakia"},
    {cont:'eu',selected:false,name:"Slovenia"},
    {cont:'eu',selected:false,name:"Sweden"},
    {cont:'af',selected:false,name:"Swaziland"},
    {cont:'af',selected:false,name:"Seychelles"},
    {cont:'as',selected:false,name:"Syria"},
    {cont:'na',selected:false,name:"Turks and Caicos Is."},
    {cont:'af',selected:false,name:"Chad"},
    {cont:'af',selected:false,name:"Togo"},
    {cont:'as',selected:false,name:"Thailand"},
    {cont:'as',selected:false,name:"Tajikistan"},
    {cont:'as',selected:false,name:"Turkmenistan"},
    {cont:'as',selected:false,name:"Timor-Leste"},
    {cont:'oc',selected:false,name:"Tonga"},
    {cont:'na',selected:false,name:"Trinidad and Tobago"},
    {cont:'af',selected:false,name:"Tunisia"},
    {cont:'as',selected:false,name:"Turkey"},
    {cont:'af',selected:false,name:"Tanzania"},
    {cont:'af',selected:false,name:"Uganda"},
    {cont:'eu',selected:false,name:"Ukraine"},
    {cont:'sa',selected:false,name:"Uruguay"},
    {cont:'na',selected:false,name:"United States"},
    {cont:'as',selected:false,name:"Uzbekistan"},
    {cont:'na',selected:false,name:"St. Vin. and Gren."},
    {cont:'sa',selected:false,name:"Venezuela"},
    {cont:'na',selected:false,name:"U.S. Virgin Is."},
    {cont:'as',selected:false,name:"Vietnam"},
    {cont:'oc',selected:false,name:"Vanuatu"},
    {cont:'oc',selected:false,name:"Samoa"},
    {cont:'as',selected:false,name:"Yemen"},
    {cont:'af',selected:false,name:"South Africa"},
    {cont:'af',selected:false,name:"Zambia"},
    {cont:'af',selected:false,name:"Zimbabwe"},
   ]