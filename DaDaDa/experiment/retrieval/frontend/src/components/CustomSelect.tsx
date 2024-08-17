import * as React from 'react';
import { Theme, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Chip from '@mui/material/Chip';
import { Typography } from '@mui/material';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

type Props = {
    keys:string[],
    name:string,
    onChange:(keys:string[])=>void
}
function getStyles(name: string, personName: readonly string[], theme: Theme) {
  return {
    fontWeight:
      personName.indexOf(name) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  };
}

export default function CustomSelect({keys,name,onChange}: Props) {
  const theme = useTheme();
  const [keysSelected, setkeysSelected] = React.useState<string[]>([]);

  const handleChange = (event: SelectChangeEvent<typeof keysSelected>) => {
    const {
      target: { value },
    } = event;
    let true_value = typeof value === 'string' ? value.split(',') : value
    setkeysSelected(
      // On autofill we get a stringified value.
      true_value,
    );
    onChange(true_value)
  };

  return (
    <Box >
        <Typography variant='h6' id="input-slider" gutterBottom>
            <strong>{name}</strong>
        </Typography>
        <Box sx={{px:2}}>
            <FormControl sx={{width: '100%' }}>
                <InputLabel id="demo-multiple-chip-label">
                {name}
                </InputLabel>
                <Select
                labelId="demo-multiple-chip-label"
                id="demo-multiple-chip"
                multiple
                value={keysSelected}
                onChange={handleChange}
                input={<OutlinedInput id="select-multiple-chip" label={name} />}
                renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                        <Chip key={value} label={value} />
                    ))}
                    </Box>
                )}
                MenuProps={MenuProps}
                >
                {keys.map((key) => (
                    <MenuItem
                    key={key}
                    value={key}
                    style={getStyles(key, keysSelected, theme)}
                    >
                    {key}
                    </MenuItem>
                ))}
                </Select>
            </FormControl>
        </Box>
      
    </Box>
  );
}