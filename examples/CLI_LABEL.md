# CLI Label

In Preferences, you may define one or more, new line-separated one-liner commands to produce some useful output.
**Do not forget to set the refresh rate** accordingly. You probably wouldn't like to check the weather once a second.
Set the refresh rate to 0 to disable periodical script execution.

## Default command

Prints 'Linux <kernel-release>'.

`a=$(uname -s ; uname -r) ; echo $a`

## Now playing

Requires the `playerctl` package.

`info=$(playerctl metadata --format '{{title}} - {{artist}}'); echo $info`

## Weather

`weather=$(curl 'https://wttr.in/Auckland?format=3') ; echo $weather`

Surely every one-liner may just execute an external script, e.g.:

## Now playing / date and time

```bash
#!/bin/sh

status=$(playerctl status)

if [[ ${status} == "Playing" ]] || [[ ${status} == "Paused" ]]
then
  info=$(playerctl metadata --format '{{artist}} - {{title}}')
else
  info=$(date "+%a, %d. %b  %H:%M")
fi

echo $info
```