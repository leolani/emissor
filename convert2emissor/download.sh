#!/usr/bin/env bash

for arg in "$@"; do
    echo $arg
    if [ $arg = "IEMOCAP" ]; then
        LINK="https://surfdrive.surf.nl/files/index.php/s/EcIkP4iRzoJpBzR/download"
        FILENAME="IEMOCAP.zip"
    elif [ $arg = "MELD" ]; then
        LINK="https://surfdrive.surf.nl/files/index.php/s/nnjxH1oboRN3996/download"
        FILENAME="MELD.zip"
    else
        echo "Currently only IEMOCAP and MELD datasets are supported"
        continue
    fi
    wget -O $FILENAME $LINK
done

for FILE in "IEMOCAP.zip" "MELD.zip"
do
    if test -f "$FILE"; then
        echo $FILE exists
        DS=$(basename -- "$FILE")
        extension="${DS##*.}"
        DS="${DS%.*}"
        unzip -o $FILE -d ./Datasets/
        rm -rf ./Datasets/$DS/face-videos
        rm $FILE
    fi
done