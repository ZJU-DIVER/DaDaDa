import { Box, Slider, Typography } from '@mui/material'
import React, { useState } from 'react'

type Props = {
    min:number,
    max:number,
    name:string,
    scale?:(value: number) => number,
    labelformat?:((value: number, index: number) => React.ReactNode),
    onChange:(keys:number[])=>void
}

export default function CustomSlider({name,min,max,scale,labelformat,onChange}: Props) {
    const [value,setValue] = useState([0,600000])
    const handleChange = (event: Event, newValue: number | number[]) => {
        setValue(newValue as number[]);
        onChange(newValue as number[])
      };
    return (
        <Box>
            <Typography variant='h6' id="input-slider" gutterBottom>
                <strong>{name}</strong>
            </Typography>
            <Box sx={{px:2}}>
                <Slider
                    min={min}
                    max={max}
                    value={value}
                    scale={scale}
                    onChange={handleChange}
                    valueLabelDisplay="auto"
                    valueLabelFormat={labelformat}
                />
            </Box>
            
        </Box>
        
    )
}