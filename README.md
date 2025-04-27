Slow auto login to mega.nz with playwright to keep files alive. It has been created for handle with some mega.nz popups, which generates errors during using [megatools](https://xff.cz/megatools/).

`pip install asyncio`


`pip install playwright`

Add your path to your browser:

`executable_path="your browser path",`

## Account list
Add your file
`    with open('accounts.txt', 'r') as f:`

Example line: `email,password`

Comma is as a separator.

## Adjust parameters\arguments

If you use Chrome, you can just set: `headless=True,` and delete:

```             
    '--no-startup-window',
    '--silent-launch',
    '--window-position=-32000,-32000',
```

## Enhancements
Feel free to add multithreading/multiprocessing with AI, if you have many accounts.

## Disclaimer
I am posting this code for educational purposes. I am not responsible for any bans on your accounts.
