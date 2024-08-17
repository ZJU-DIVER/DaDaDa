import { Box, Card, Chip, Divider, Grid, Link, Stack, Typography } from '@mui/material'
import React from 'react'

type Props = {
    prodinfo:any
}

function getFrequenctText(value:string){
    if(value==='no-update'){
        return 'No update'
    }
    let cap_value = value[0].toUpperCase() + value.slice(1) + " update"
    return cap_value
}

function getTagsText(prodinfo:any){
    let dimension = prodinfo.dimension>0?`· ${parseInt(prodinfo.dimension)} dimension(s)`:""
    let volume = prodinfo.volume>0?` · ${getValueText('volume',prodinfo.volume)} data`:""
    let size = prodinfo.size>0?` · ${getValueText('size',prodinfo.size)} size`:""
    return  `${prodinfo.category} · ${prodinfo.provider} · ${getFrequenctText(prodinfo.freq[0])}${dimension}${volume}${size} · ${getCoverageText(prodinfo.geo_coverage)}`

}

export default function ProductCard({prodinfo}: Props) {
    
  return (
    <Card sx={{p:2}}>
        <Grid container>
            <Grid item xs={10}>
                <Stack spacing={1}>
                    <Stack direction={'row'} spacing={2}>
                        <Chip label={prodinfo.platform} color="primary" />
                        <Link href={prodinfo.url} fontSize='20px' underline="hover">
                            {prodinfo.title}
                        </Link>
                    </Stack>
                    
                    <Typography variant="overline" display="block" gutterBottom>
                        <strong>{getTagsText(prodinfo)}</strong>
                    </Typography>
                    <Box maxHeight={'100px'} overflow='clip' >
                        <Typography overflow='hidden' variant="body1" gutterBottom>
                            {prodinfo.desc}
                        </Typography>
                    </Box>

                    </Stack>
            </Grid>
            <Grid item xs={2}>
                <Stack display='flex' justifyContent='center' alignItems='center' height={'100%'}>
                    <Typography variant='h6'><strong>Price</strong></Typography>
                    <Divider flexItem/>
                    <Stack display='flex' justifyContent='center' alignItems='center' height='100%'>
                        <Typography variant='h6'>
                            <strong>{getPricing(prodinfo.pricing_type,prodinfo.price,'USD')}</strong>
                        </Typography>
                        {['subscription','usage-based'].indexOf(prodinfo.pricing_type)!==-1 && 
                        <Typography variant='overline'>
                        <strong>{getPriceTag(prodinfo.pricing_type)}</strong>
                        </Typography>
                        }
                    </Stack>

                </Stack>
            </Grid>
        </Grid>
    </Card>
  )
}

function getPriceTag(mode:string){

    if(mode==='subscription'){
        return `Per payment cycle`
    }
    if(mode==='usage-based'){
        return `Per unit`
    }
}

function getPricing(mode:string,price:number,currency:string){
    if(mode==='free'){
        return 'Free'
    }
    if(mode==='negotiation'){
        return 'By Negotiation'
    }
    let fixedPirce:any = price
    // console.log(fixedPirce)
    return `${parseFloat(fixedPirce).toFixed(2)} ${currency}`
    
}

function getCoverageText(value:string){
    let countryList = value.split(/(?<=\S),(?=\S)/g);
    // console.log(countryList)
    if(countryList.length <= 3){
        return value
    }
    return `${countryList[0]},${countryList[1]},${countryList[2]} and other ${countryList.length - 3} country/region(s)`
}

const getValueText = (type:string,value:number)=>{
    let units = []
    if(type==='volume'){
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
  
    return `${parseFloat(scaledValue.toString()).toFixed(2)} ${units[unitIndex]}`;
  } 