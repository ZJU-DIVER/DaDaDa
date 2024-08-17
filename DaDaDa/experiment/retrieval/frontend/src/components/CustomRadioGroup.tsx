import { FormControl, FormLabel, FormControlLabel, Radio, RadioGroup, Typography } from '@mui/material'
import React, { useState } from 'react'

type Props = {
    keys:string[],
    name:string
}
const maxShow = 5
export default function CustomRadioGroup({keys,name}: Props) {
  const [showall,setShowAll] = useState(false)
  return (
    <FormControl>
      <FormLabel  id="radio-group-name">
        <Typography variant='h6' id="input-slider" gutterBottom>
          <strong>{name}</strong>
        </Typography>
      </FormLabel>
      <RadioGroup

        aria-labelledby="radio-group-name"
        name="radio-group-name"
      >
        {keys.map((key,index)=>
        <FormControlLabel hidden={showall?false:index>=maxShow} value={key} control={<Radio/>} label={key} />
        )}
      </RadioGroup>
    </FormControl>
  )
}