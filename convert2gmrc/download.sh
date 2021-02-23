#!/usr/bin/env bash

for arg in "$@"; do
    echo $arg
    if [ $arg = "IEMOCAP" ]; then
        FILEID="1iq6ocRu3jkQgyVMmKj5EGb9A_wBmxzGh"
    elif [ $arg = "MELD" ]; then
        FILEID="1YZ9Zz_TdRaYsM6Lwx34IwpFgiVLNIAZ6"
    else
        echo "Currently only IEMOCAP and MELD datasets are supported"
        continue
    fi
    gdown --id $FILEID
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