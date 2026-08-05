#!/usr/bin/bash
# Send msgs to the vestaboard note just for fun
# docs.vestaboard.com/docs/charactercodes/
# https://docs.vestaboard.com/docs/vbml
# CURL examples for text, character array, and vbml compose

# load API keys
source "$HOME/vesta/.env"

MSG="[[64,64,64,63,63,63,68,67,66,66,66,65,65,65,64],[64,64,64,63,63,68,68,67,67,66,66,65,65,65,64],[64,64,64,63,68,68,68,67,67,67,66,65,65,65,64]]"
HELLO="{62}Hello World!{62}"
YODA=$(curl -sS -X POST -H "Content-Type: application/json" -d \
        '{"style": {"height": 3, "width": 15}, "components":[{"template":"Do. Or do not. There is no try.{66}"}]}' \
         https://cloud.vestaboard.com/vbml/compose )

# send star wars quote
# curl -sS -X POST -H "X-Vestaboard-Token: $VESTA_API_KEY" -H "Content-Type: application/json" -d "{\"characters\": $YODA}" https://cloud.vestaboard.com/

# send hello msg
# curl -sS -X POST -H "X-Vestaboard-Token: $VESTA_API_KEY" -H "Content-Type: application/json" -d "{\"text\": \"\n$HELLO\"}" https://cloud.vestaboard.com/
# sleep 60

# send colors
curl -sS -X POST -H "X-Vestaboard-Token: $VESTA_API_KEY" -H "Content-Type: application/json" -d "{\"characters\": $MSG}" https://cloud.vestaboard.com/